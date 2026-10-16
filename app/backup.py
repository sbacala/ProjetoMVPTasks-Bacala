"""Create, validate, retain, and restore SQLite database backups."""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
import tempfile

from sqlalchemy.engine import make_url

BACKUP_PREFIX = "tasks-"
BACKUP_SUFFIX = ".sqlite3"


def sqlite_database_path(database_url: str) -> Path:
    """Resolve a file-backed SQLite URL into an absolute filesystem path.

    Args:
        database_url: SQLAlchemy database URL from deployment configuration.

    Returns:
        Absolute path to the SQLite database file.

    Raises:
        ValueError: If the URL is not a supported file-backed SQLite URL.
    """
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite") or not url.database:
        raise ValueError("Backup utility supports file-backed SQLite URLs only.")
    if url.database == ":memory:" or url.database.startswith("file::memory:"):
        raise ValueError("In-memory SQLite databases cannot be backed up.")
    return Path(url.database).resolve()


def _verify_database(path: Path) -> None:
    """Reject corrupt SQLite files and files without the application's tasks."""
    connection = sqlite3.connect(path)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchone()
        tasks_table = connection.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'table' AND name = 'tasks'"
        ).fetchone()
    finally:
        connection.close()
    if result is None or result[0] != "ok":
        raise ValueError(f"SQLite integrity check failed for {path}.")
    if tasks_table is None:
        raise ValueError(f"SQLite database has no tasks table: {path}.")


def _copy_database(source_path: Path, destination_path: Path) -> None:
    """Copy a consistent SQLite snapshot and close both handles before rename."""
    source = sqlite3.connect(source_path)
    try:
        destination = sqlite3.connect(destination_path)
        try:
            source.backup(destination)
        finally:
            destination.close()
    finally:
        source.close()


def create_backup(
    database_path: Path,
    backup_directory: Path,
    *,
    keep: int = 7,
) -> Path:
    """Create an online-consistent SQLite snapshot and prune old snapshots.

    Args:
        database_path: Path to the live SQLite database.
        backup_directory: Directory where snapshots are stored.
        keep: Number of newest snapshots to retain.

    Returns:
        Path to the newly created, integrity-checked backup.

    Raises:
        FileNotFoundError: If the configured database file does not exist.
        ValueError: If keep is not positive or a resulting backup is corrupt.
        sqlite3.Error: If SQLite fails while reading or writing the snapshot.
    """
    if keep < 1:
        raise ValueError("keep must be at least 1.")
    if not database_path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {database_path}")

    backup_directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_path = backup_directory / f"{BACKUP_PREFIX}{timestamp}{BACKUP_SUFFIX}"
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=".tasks-backup-",
        suffix=".tmp",
        dir=backup_directory,
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)

    try:
        _copy_database(database_path, temporary_path)
        _verify_database(temporary_path)
        os.replace(temporary_path, backup_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    backups = sorted(
        (
            path
            for path in backup_directory.glob(
                f"{BACKUP_PREFIX}*{BACKUP_SUFFIX}"
            )
            if path.resolve() != database_path.resolve()
        ),
        reverse=True,
    )
    for old_backup in backups[keep:]:
        old_backup.unlink()
    return backup_path


def restore_backup(
    backup_path: Path,
    database_path: Path,
) -> None:
    """Validate and atomically replace a stopped application's SQLite file.

    The caller must stop the application before restoring. This function
    refuses a corrupt source and writes a verified temporary database before
    replacing the target file.

    Args:
        backup_path: Integrity-checked SQLite backup to restore.
        database_path: Target database file to replace.

    Raises:
        FileNotFoundError: If the backup file does not exist.
        ValueError: If the backup fails SQLite's integrity check.
        sqlite3.Error: If SQLite fails while copying or validating.
    """
    if not backup_path.is_file():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    if backup_path.resolve() == database_path.resolve():
        raise ValueError("The backup file cannot also be the restore target.")
    _verify_database(backup_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=".tasks-restore-",
        suffix=".tmp",
        dir=database_path.parent,
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)
    try:
        _copy_database(backup_path, temporary_path)
        _verify_database(temporary_path)
        os.replace(temporary_path, database_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> None:
    """Run the backup or restore command using DATABASE_URL configuration."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser(
        "create",
        help="Create a verified SQLite backup.",
    )
    backup_parser.add_argument(
        "--directory",
        type=Path,
        default=Path(".secrets/backups"),
    )
    backup_parser.add_argument("--keep", type=int, default=7)

    restore_parser = subparsers.add_parser(
        "restore",
        help="Restore a SQLite backup after stopping the application.",
    )
    restore_parser.add_argument("backup", type=Path)
    restore_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm the target database will be replaced.",
    )

    args = parser.parse_args()
    database_url = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
    database_path = sqlite_database_path(database_url)
    if args.command == "create":
        backup_path = create_backup(
            database_path,
            args.directory,
            keep=args.keep,
        )
        print(f"Verified SQLite backup created: {backup_path}")
        return
    if not args.confirm:
        parser.error("restore requires --confirm after stopping the application")
    if database_path.is_file():
        safety_backup = create_backup(
            database_path,
            args.backup.parent / "pre-restore",
            keep=7,
        )
        print(f"Pre-restore safety backup created: {safety_backup}")
    restore_backup(args.backup, database_path)
    print(f"SQLite database restored from: {args.backup}")


if __name__ == "__main__":
    main()
