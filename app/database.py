"""SQLite engine, session factory, and database dependencies."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database_models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_tables() -> None:
    """Create database tables that do not already exist."""
    Base.metadata.create_all(bind=engine)


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
