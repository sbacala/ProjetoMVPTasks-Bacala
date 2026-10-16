"""Operational tests for Alembic migrations and SQLite backup recovery."""

from pathlib import Path
import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, inspect

from app.backup import (
    create_backup,
    restore_backup,
    sqlite_database_path,
)
from app.database import verify_database_schema
from app.database_models import Base


def _alembic_config(database_path: Path) -> Config:
    """Build an isolated Alembic configuration for a temporary SQLite file."""
    repository_root = Path(__file__).resolve().parents[1]
    config = Config(str(repository_root / "alembic.ini"))
    config.set_main_option("script_location", str(repository_root / "migrations"))
    config.set_main_option(
        "sqlalchemy.url",
        f"sqlite:///{database_path.as_posix()}",
    )
    return config


def test_initial_migration_creates_all_application_tables(tmp_path: Path) -> None:
    """A clean database upgrades to the current revision with task/user tables."""
    database_path = tmp_path / "fresh.sqlite3"

    command.upgrade(_alembic_config(database_path), "head")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        assert set(inspect(engine).get_table_names()) == {
            "alembic_version",
            "tasks",
            "users",
        }
    finally:
        engine.dispose()


def test_initial_migration_adopts_legacy_schema_without_losing_rows(
    tmp_path: Path,
) -> None:
    """Legacy create_all databases are stamped through an idempotent upgrade."""
    database_path = tmp_path / "legacy.sqlite3"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        Base.metadata.create_all(engine)
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO tasks "
                "(id, title, description, status, created_at) "
                "VALUES ('00000000-0000-0000-0000-000000000001', "
                "'Legacy task', NULL, 0, '2026-10-16 00:00:00.000000')"
            )
        command.upgrade(_alembic_config(database_path), "head")
        with engine.connect() as connection:
            row = connection.exec_driver_sql(
                "SELECT title FROM tasks"
            ).one()
            assert row[0] == "Legacy task"
    finally:
        engine.dispose()


def test_initial_migration_rejects_incompatible_existing_schema(
    tmp_path: Path,
) -> None:
    """Migration refuses to mark incomplete legacy tables as compatible."""
    database_path = tmp_path / "incompatible.sqlite3"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT)")

    with pytest.raises(RuntimeError, match="expected baseline schema"):
        command.upgrade(_alembic_config(database_path), "head")


def test_startup_schema_check_requires_current_migration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Startup fails for an unversioned database and accepts a migrated one."""
    database_path = tmp_path / "version-check.sqlite3"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    monkeypatch.setattr("app.database.engine", engine)
    try:
        with pytest.raises(RuntimeError, match="alembic upgrade head"):
            verify_database_schema()
        command.upgrade(_alembic_config(database_path), "head")
        verify_database_schema()
    finally:
        engine.dispose()


def test_sqlite_backup_is_consistent_and_restore_recovers_data(
    tmp_path: Path,
) -> None:
    """Online backup and restore preserve a database snapshot."""
    database_path = tmp_path / "live.sqlite3"
    backup_directory = tmp_path / "backups"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("CREATE TABLE tasks (value TEXT NOT NULL)")
        connection.execute("INSERT INTO tasks VALUES ('before')")
        connection.commit()

    backup_path = create_backup(database_path, backup_directory)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("INSERT INTO tasks VALUES ('after')")
    finally:
        connection.close()

    restore_backup(backup_path, database_path)

    connection = sqlite3.connect(database_path)
    try:
        values = connection.execute(
            "SELECT value FROM tasks ORDER BY value"
        ).fetchall()
    finally:
        connection.close()
    assert values == [("before",)]


def test_corrupt_backup_does_not_replace_live_database(tmp_path: Path) -> None:
    """Restore validates the snapshot before touching the target database."""
    database_path = tmp_path / "live.sqlite3"
    corrupt_backup = tmp_path / "corrupt.sqlite3"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("CREATE TABLE tasks (value TEXT NOT NULL)")
        connection.execute("INSERT INTO tasks VALUES ('keep')")
        connection.commit()
    corrupt_backup.write_bytes(b"not a sqlite database")

    with pytest.raises(sqlite3.DatabaseError):
        restore_backup(corrupt_backup, database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        assert connection.execute("SELECT value FROM tasks").fetchone() == (
            "keep",
        )


def test_backup_retains_only_newest_requested_snapshots(
    tmp_path: Path,
) -> None:
    """Retention removes only owned backup files older than the keep count."""
    database_path = tmp_path / "live.sqlite3"
    backup_directory = tmp_path / "backups"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("CREATE TABLE tasks (value INTEGER)")
        connection.commit()

    backups = [
        create_backup(database_path, backup_directory, keep=2)
        for _ in range(3)
    ]

    retained = sorted(backup_directory.glob("tasks-*.sqlite3"))
    assert len(retained) == 2
    assert backups[-1] in retained


def test_backup_rejects_empty_sqlite_database(tmp_path: Path) -> None:
    """A valid but unrelated empty SQLite file is not an application backup."""
    database_path = tmp_path / "empty.sqlite3"
    with closing(sqlite3.connect(database_path)):
        pass

    with pytest.raises(ValueError, match="no tasks table"):
        create_backup(database_path, tmp_path / "backups")


@pytest.mark.parametrize(
    "database_url",
    ["postgresql://localhost/tasks", "sqlite:///:memory:"],
)
def test_backup_rejects_unsupported_database_urls(database_url: str) -> None:
    """Backup path resolution only accepts file-backed SQLite databases."""
    with pytest.raises(ValueError):
        sqlite_database_path(database_url)
