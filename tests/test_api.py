"""Integration tests for FastAPI API endpoints."""

import pytest


# ── Experiments ──────────────────────────────────────────────────────

class TestExperimentEndpoints:
    def test_set_experiment(self, api_client):
        resp = api_client.post("/api/experiments/set", json={"name": "test-exp"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "test-exp"
        assert "id" in body

    def test_list_experiments(self, api_client):
        api_client.post("/api/experiments/set", json={"name": "list-exp"})
        resp = api_client.get("/api/experiments")
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()]
        assert "list-exp" in names


# ── Runs ─────────────────────────────────────────────────────────────

class TestRunEndpoints:
    def _create_experiment(self, api_client) -> str:
        resp = api_client.post("/api/experiments/set", json={"name": "run-exp"})
        return resp.json()["id"]

    def test_start_run(self, api_client):
        exp_id = self._create_experiment(api_client)
        resp = api_client.post("/api/run/start", json={"experiment_id": exp_id})
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "RUNNING"
        assert body["experiment_id"] == exp_id

    def test_end_run(self, api_client):
        exp_id = self._create_experiment(api_client)
        run = api_client.post(
            "/api/run/start", json={"experiment_id": exp_id}
        ).json()
        resp = api_client.post("/api/run/end", json={"run_id": run["id"]})
        assert resp.status_code == 200
        assert resp.json()["status"] == "FINISHED"

    def test_list_runs(self, api_client):
        exp_id = self._create_experiment(api_client)
        api_client.post("/api/run/start", json={"experiment_id": exp_id})
        resp = api_client.get(f"/api/experiments/{exp_id}/runs")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_get_run_details(self, api_client):
        exp_id = self._create_experiment(api_client)
        run = api_client.post(
            "/api/run/start", json={"experiment_id": exp_id}
        ).json()
        resp = api_client.get(f"/api/runs/{run['id']}")
        assert resp.status_code == 200
        body = resp.json()
        assert "params" in body
        assert "metrics" in body
        assert "artifacts" in body


# ── Logging ──────────────────────────────────────────────────────────

class TestLoggingEndpoints:
    def _start_run(self, api_client) -> str:
        exp = api_client.post(
            "/api/experiments/set", json={"name": "log-exp"}
        ).json()
        run = api_client.post(
            "/api/run/start", json={"experiment_id": exp["id"]}
        ).json()
        return run["id"]

    def test_log_param(self, api_client):
        run_id = self._start_run(api_client)
        resp = api_client.post(
            "/api/param/log",
            json={"run_id": run_id, "key": "lr", "value": "0.01"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    def test_log_metric(self, api_client):
        run_id = self._start_run(api_client)
        resp = api_client.post(
            "/api/metric/log",
            json={"run_id": run_id, "key": "loss", "value": 0.456, "step": 1},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

        
