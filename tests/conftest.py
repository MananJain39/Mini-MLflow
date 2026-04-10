"""Shared pytest fixtures for Mini-MLflow tests.

Strategy: override DATABASE_URL *before* any Server module is imported
so every component transparently uses a temporary SQLite file.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# 1. Point DATABASE_URL to a temp file BEFORE anything imports session.py.
_tmp_db = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
_tmp_db.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"

# 2. Make mini_mlflow source importable from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 3. NOW import the session module (picks up the env-var URL).
from mini_mlflow.server.db.session import Base, SessionLocal, engine  # noqa: E402
from mini_mlflow.server.db import models as _models  # noqa: E402  — registers tables


@pytest.fixture(autouse=True)
def _fresh_tables():
    """Create all tables before each test and drop them afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Yield a DB session scoped to a single test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def api_client():
    """FastAPI TestClient — imported lazily so the DB env is already set."""
    from fastapi.testclient import TestClient
    from mini_mlflow.server.main import app
    return TestClient(app)
