"""
Thread-safe Mini-MLflow tracking client.

Uses HTTP requests to communicate with the server — no direct DB/Tracker
imports so the client can run in a separate process.
"""

from __future__ import annotations

import requests as _req
from .exceptions import (
    ConnectionError,
    MiniMLflowError,
    NotFoundError,
    ServerError,
    ValidationError,
)


class MiniMLflowClient:
    """Thread-safe, instance-based tracking client.

    Each instance carries its own ``base_url``, active experiment, and
    active run — no module-level globals, so multiple instances can
    coexist safely across threads.

    Parameters
    ----------
    base_url : str
        Root URL of the Mini-MLflow server API
        (default ``http://localhost:8000/api``).
    timeout : float
        Seconds to wait for each HTTP request (default ``30``).
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api",
        timeout: float = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._active_experiment: dict | None = None
        self._active_run: dict | None = None
        self._session = _req.Session()

    # Internal helpers
    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Send an HTTP request and return the parsed JSON body.

        Raises
        ------
        ConnectionError
            If the server is unreachable.
        NotFoundError
            If the server returns 404.
        ValidationError
            If the server returns 422.
        ServerError
            If the server returns a 5xx status.
        MiniMLflowError
            For any other non-2xx status.
        """
        url = f"{self.base_url}{path}"
        retries = 3
        backoff_factor = 1.0
        
        for attempt in range(retries):
            try:
                resp = self._session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
            except (_req.ConnectionError, _req.Timeout) as exc:
                if attempt < retries - 1:
                    import time
                    time.sleep(backoff_factor * (2 ** attempt))
                    continue
                raise ConnectionError(url, cause=exc) from exc

            if resp.status_code == 404:
                raise NotFoundError(resp.text)
            if resp.status_code == 422:
                raise ValidationError(resp.text)
            if resp.status_code >= 500:
                if attempt < retries - 1:
                    import time
                    time.sleep(backoff_factor * (2 ** attempt))
                    continue
                raise ServerError(resp.status_code, resp.text)
            if not resp.ok:
                raise MiniMLflowError(
                    f"HTTP {resp.status_code}: {resp.text}"
                )

            return resp.json()

    # Experiment API
    def set_experiment(self, name: str) -> dict:
        """Create or retrieve an experiment by *name*.

        The experiment is stored as the active experiment for subsequent
        ``start_run`` calls on **this** client instance.
        """
        data = self._request("POST", "/experiments/set", json={"name": name})
        self._active_experiment = data
        return data

    def list_experiments(self) -> list[dict]:
        """Return every experiment known to the server."""
        return self._request("GET", "/experiments")

    # Run API
    def start_run(self, experiment_id: str | None = None) -> dict:
        """Start a new run.

        Parameters
        ----------
        experiment_id : str, optional
            Explicit experiment ID.  Falls back to the active experiment
            set via :meth:`set_experiment`.

        Raises
        ------
        RuntimeError
            If no experiment is available.
        """
        exp_id = experiment_id or (
            self._active_experiment and self._active_experiment.get("id")
        )
        if not exp_id:
            raise RuntimeError(
                "No active experiment — call set_experiment() first"
            )

        data = self._request(
            "POST", "/run/start", json={"experiment_id": exp_id}
        )
        self._active_run = data
        return data

    def end_run(self, run_id: str | None = None) -> dict:
        """End an active run.

        Parameters
        ----------
        run_id : str, optional
            Explicit run ID.  Falls back to the run started via
            :meth:`start_run`.
        """
        rid = run_id or (self._active_run and self._active_run.get("id"))
        if not rid:
            raise RuntimeError("No active run to end")

        data = self._request("POST", "/run/end", json={"run_id": rid})
        if rid == (self._active_run and self._active_run.get("id")):
            self._active_run = None
        return data

    def list_runs(self, experiment_id: str) -> list[dict]:
        """List all runs for a given experiment."""
        return self._request("GET", f"/experiments/{experiment_id}/runs")

    def get_run_details(self, run_id: str) -> dict:
        """Return params, metrics, and artifacts for a run."""
        return self._request("GET", f"/runs/{run_id}")

    # Logging API
    def log_param(
        self, key: str, value: str, *, run_id: str | None = None
    ) -> dict:
        """Log a parameter to the active (or specified) run."""
        rid = run_id or (self._active_run and self._active_run.get("id"))
        if not rid:
            raise RuntimeError("No active run — call start_run() first")
        return self._request(
            "POST",
            "/param/log",
            json={"run_id": rid, "key": key, "value": value},
        )

    def log_metric(
        self,
        key: str,
        value: float,
        step: int = 0,
        *,
        run_id: str | None = None,
    ) -> dict:
        """Log a metric to the active (or specified) run."""
        rid = run_id or (self._active_run and self._active_run.get("id"))
        if not rid:
            raise RuntimeError("No active run — call start_run() first")
        return self._request(
            "POST",
            "/metric/log",
            json={
                "run_id": rid,
                "key": key,
                "value": value,
                "step": step,
            },
        )

    def log_artifact(
        self, file_path: str, *, run_id: str | None = None
    ) -> dict:
        """Log an artifact to the active (or specified) run."""
        rid = run_id or (self._active_run and self._active_run.get("id"))
        if not rid:
            raise RuntimeError("No active run — call start_run() first")
        return self._request(
            "POST",
            "/artifacts/log",
            json={"run_id": rid, "file_path": file_path},
        )

    def log_tag(
        self, key: str, value: str, *, run_id: str | None = None
    ) -> dict:
        """Log a tag to the active (or specified) run."""
        rid = run_id or (self._active_run and self._active_run.get("id"))
        if not rid:
            raise RuntimeError("No active run — call start_run() first")
        return self._request(
            "POST",
            "/tag/log",
            json={"run_id": rid, "key": key, "value": value},
        )

    # Context-manager support
    def run(self, experiment_id: str | None = None) -> "_RunContext":
        """Return a context manager that starts and ends a run.

        Usage::

            client = MiniMLflowClient()
            client.set_experiment("my-exp")
            with client.run() as run_info:
                client.log_param("lr", "0.01")
        """
        return _RunContext(self, experiment_id)


class _RunContext:
    """Context manager wrapping :meth:`MiniMLflowClient.start_run` /
    :meth:`MiniMLflowClient.end_run`."""

    def __init__(self, client: MiniMLflowClient, experiment_id: str | None):
        self._client = client
        self._experiment_id = experiment_id
        self._run: dict | None = None

    def __enter__(self) -> dict:
        self._run = self._client.start_run(self._experiment_id)
        return self._run

    def __exit__(self, exc_type, exc, tb):
        if self._run:
            self._client.end_run(self._run["id"])
        return False