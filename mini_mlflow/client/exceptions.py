"""Client-side exception hierarchy for Mini-MLflow."""


class MiniMLflowError(Exception):
    """Base exception for all Mini-MLflow client errors."""


class ServerError(MiniMLflowError):
    """Raised when the server returns a 5xx status code."""

    def __init__(self, status_code: int, detail: str = ""):
        self.status_code = status_code
        super().__init__(f"Server error {status_code}: {detail}")


class NotFoundError(MiniMLflowError):
    """Raised when a requested resource does not exist (404)."""

    def __init__(self, detail: str = ""):
        super().__init__(f"Not found: {detail}")


class ValidationError(MiniMLflowError):
    """Raised when the server rejects request data (422)."""

    def __init__(self, detail: str = ""):
        super().__init__(f"Validation error: {detail}")


class ConnectionError(MiniMLflowError):
    """Raised when the client cannot reach the server."""

    def __init__(self, url: str, cause: Exception | None = None):
        self.url = url
        msg = f"Cannot connect to Mini-MLflow server at {url}"
        if cause:
            msg += f": {cause}"
        super().__init__(msg)
