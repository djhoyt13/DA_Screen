"""Shared pytest fixtures. Email is always mocked; each test gets a temp SQLite DB."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def db_path(tmp_path, monkeypatch):
    db_file = tmp_path / "quiz_results.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    from backend.database import init_db, reset_engine

    reset_engine()
    init_db()
    yield db_file
    reset_engine()


@pytest.fixture(autouse=True)
def mock_send_email():
    with patch("backend.emailer.send_results_email", return_value=(True, None)) as mocked:
        yield mocked


@pytest.fixture(autouse=True)
def mock_send_invite_email():
    with patch("backend.emailer.send_invite_email", return_value=(True, None)) as mocked:
        yield mocked


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from backend.app import app

    with TestClient(app) as test_client:
        yield test_client
