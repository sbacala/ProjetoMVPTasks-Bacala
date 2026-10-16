"""Create initial task and user tables.

Revision ID: 20261016_0001
Revises:
Create Date: 2026-10-16
"""

from typing import Sequence

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "20261016_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _validate_existing_table(
    table_name: str,
    expected_columns: set[str],
) -> bool:
    """Validate a legacy ORM-created table before adopting it as the baseline.

    Returns True if the table already exists and its required columns and
    primary key match; otherwise returns False if the table is absent.
    """
    if context.is_offline_mode():
        return False

    connection = op.get_bind()
    inspector = inspect(connection)
    if table_name not in inspector.get_table_names():
        return False

    actual_columns = {
        column["name"] for column in inspector.get_columns(table_name)
    }
    primary_key = set(inspector.get_pk_constraint(table_name)["constrained_columns"])
    if not expected_columns.issubset(actual_columns) or primary_key != {"id"}:
        raise RuntimeError(
            f"Existing {table_name} table does not match the expected baseline "
            "schema; inspect and back up the database before migrating."
        )
    if table_name == "users":
        unique_email = any(
            "email" in constraint.get("column_names", [])
            for constraint in inspector.get_unique_constraints(table_name)
        ) or any(
            index.get("unique")
            and "email" in index.get("column_names", [])
            for index in inspector.get_indexes(table_name)
        )
        if not unique_email:
            raise RuntimeError(
                "Existing users table does not enforce unique email; inspect "
                "and back up the database before migrating."
            )
    return True


def upgrade() -> None:
    """Create missing tables or safely adopt tables from the pre-Alembic app."""
    tasks_exist = _validate_existing_table(
        "tasks",
        {"id", "title", "description", "status", "created_at"},
    )
    users_exist = _validate_existing_table(
        "users",
        {"id", "name", "email"},
    )

    if not tasks_exist:
        op.create_table(
            "tasks",
            sa.Column("title", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=2000), nullable=True),
            sa.Column("status", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not users_exist:
        op.create_table(
            "users",
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("email", sa.String(length=254), nullable=False),
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )


def downgrade() -> None:
    """Refuse to drop baseline tables because they may contain user data."""
    raise RuntimeError(
        "The initial schema is a non-destructive baseline; restore a verified "
        "backup instead of downgrading past it."
    )
