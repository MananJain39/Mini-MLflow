"""Unit tests for the client exception hierarchy."""

import pytest
from client.exceptions import (
    MiniMLflowError,
    ServerError,
    NotFoundError,
    ValidationError,
    ConnectionError,
)


class TestExceptionHierarchy:
    def test_all_inherit_from_base(self):
        for cls in (ServerError, NotFoundError, ValidationError, ConnectionError):
            assert issubclass(cls, MiniMLflowError)

    def test_server_error_message(self):
        err = ServerError(500, "Internal")
        assert "500" in str(err)
        assert "Internal" in str(err)
        assert err.status_code == 500

    def test_not_found_error_message(self):
        err = NotFoundError("run xyz")
        assert "run xyz" in str(err)

    def test_validation_error_message(self):
        err = ValidationError("bad field")
        assert "bad field" in str(err)

    def test_connection_error_message(self):
        err = ConnectionError("http://localhost:8000")
        assert "localhost:8000" in str(err)

    def test_connection_error_with_cause(self):
        cause = OSError("refused")
        err = ConnectionError("http://localhost:8000", cause=cause)
        assert "refused" in str(err)
