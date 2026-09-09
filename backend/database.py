"""SQLAlchemy engine, session factory, and schema init.

Default database file: ``<repo_root>/quiz_results.db``
(equivalent to ``sqlite:///./quiz_results.db`` when the process cwd is the repo root).

Override with the ``DATABASE_URL`` environment variable, e.g.
``sqlite:///./quiz_results.db`` or ``sqlite:////tmp/quiz_results.db``.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = REPO_ROOT / "quiz_results.db"

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_database_url():
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    return "sqlite:///" + DEFAULT_SQLITE_PATH.as_posix()


def _connect_args(url):
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def get_engine():
    global _engine
    if _engine is None:
        url = get_database_url()
        _engine = create_engine(url, connect_args=_connect_args(url), future=True)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            future=True,
        )
    return _SessionLocal


def get_session():
    return get_session_factory()()


def reset_engine(url=None):
    """Dispose the current engine so tests can point at a temporary database."""
    global _engine, _SessionLocal
    if url is not None:
        os.environ["DATABASE_URL"] = url
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def init_db():
    """Create tables if they do not exist. Safe to call on every startup."""
    import backend.models  # noqa: F401 — register models on Base.metadata

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    _ensure_assessment_column(engine)


def _ensure_assessment_column(engine):
    """Add submissions.assessment for DBs created before multi-assessment support."""
    url = str(engine.url)
    if not url.startswith("sqlite"):
        return
    with engine.begin() as conn:
        rows = conn.exec_driver_sql("PRAGMA table_info(submissions)").fetchall()
        columns = {row[1] for row in rows}
        if "assessment" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE submissions ADD COLUMN assessment VARCHAR DEFAULT 'ds'"
            )
