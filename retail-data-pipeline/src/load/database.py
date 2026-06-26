"""Database engine factory and connection helpers."""

import os

from sqlalchemy import Engine, create_engine, event

from src.config import DATABASE_URL


def get_database_url() -> str:
    """
    Return the active database URL.

    Override with the DATABASE_URL environment variable to switch backends
    (e.g. postgresql+psycopg2://user:pass@localhost:5432/retail).
    """
    return os.getenv("DATABASE_URL", DATABASE_URL)


def get_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the configured database."""
    url = database_url or get_database_url()
    engine = create_engine(url, future=True)

    if url.startswith("sqlite"):
        _enable_sqlite_foreign_keys(engine)

    return engine


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    """Ensure SQLite enforces foreign key constraints."""

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
