"""SQLAlchemy models used for relational database persistence."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator[datetime]):
    """Persist timezone-aware datetimes consistently as UTC."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self,
        value: datetime | None,
        dialect: Dialect,
    ) -> datetime | None:
        """Convert an aware input timestamp to UTC before database storage.

        Args:
            value: Timestamp supplied by the ORM, or None.
            dialect: SQLAlchemy dialect requesting the conversion.

        Returns:
            The UTC-normalized timestamp, or None.

        Raises:
            ValueError: If a non-null timestamp has no timezone.
        """
        del dialect
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime values must include a timezone.")
        return value.astimezone(timezone.utc)

    def process_result_value(
        self,
        value: datetime | None,
        dialect: Dialect,
    ) -> datetime | None:
        """Return database timestamps as timezone-aware UTC values.

        Args:
            value: Timestamp loaded from the database, or None.
            dialect: SQLAlchemy dialect requesting the conversion.

        Returns:
            The timestamp normalized to UTC, or None. Naive values from
            databases without timezone support are interpreted as UTC.
        """
        del dialect
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class EntityRecord(Base):
    """Provide a UUID primary key for persisted entities."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)


class TaskRecord(EntityRecord):
    """Persist a task in the configured relational database."""

    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
    )


class UserRecord(EntityRecord):
    """Persist a user in SQLite."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
