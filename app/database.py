"""SQLite engine, session factory, and database dependencies."""

import os
from collections.abc import Generator
from pathlib import Path

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def verify_database_schema() -> None:
    """Fail startup unless the database has been upgraded to the migration head.

    Raises:
        RuntimeError: If the database is not stamped with the current Alembic
            migration revision.
    """
    alembic_config = Config(
        str(Path(__file__).resolve().parent.parent / "alembic.ini")
    )
    script_directory = ScriptDirectory.from_config(alembic_config)
    expected_revision = script_directory.get_current_head()
    with engine.connect() as connection:
        current_revision = MigrationContext.configure(
            connection
        ).get_current_revision()
    if current_revision != expected_revision:
        raise RuntimeError(
            "Database schema is not at the current migration revision "
            f"(found {current_revision!r}, expected {expected_revision!r}); "
            "run 'python -m alembic upgrade head' before starting the API."
        )


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after the request.

    Yields:
        A SQLAlchemy session bound to the application database.
    """
    database_session = SessionLocal()
    try:
        yield database_session
    finally:
        database_session.close()
