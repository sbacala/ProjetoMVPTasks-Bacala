"""Pydantic models for the task management API."""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


class TaskFields(BaseModel):
    """Fields shared by task commands and persisted task entities."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=3,
        max_length=100,
        description="Required task title, between 3 and 100 characters.",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional task description, up to 2000 characters.",
    )
    status: StrictBool = Field(
        default=False,
        description="Whether the task is complete.",
    )

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: object) -> object:
        """Trim title whitespace and reject titles too short after trimming."""
        if isinstance(value, str):
            normalized = value.strip()
            if len(normalized) < 3:
                raise ValueError(
                    "Title must contain at least 3 non-whitespace characters."
                )
            return normalized
        return value


class TaskCreate(TaskFields):
    """Client-supplied fields accepted when creating a task."""


class TaskUpdate(TaskFields):
    """Client-supplied fields accepted when replacing a task."""


class TaskResponse(TaskFields):
    """Public representation returned for persisted tasks."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_timezone_aware_created_at(cls, value: datetime) -> datetime:
        """Reject naive datetimes so API responses always carry a timezone."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must include a timezone.")
        return value


class Task(TaskFields):
    """Represent a persisted task returned by the application."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID = Field(description="UUID identifying the persisted task.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC date and time when the task was created.",
    )

    @field_validator("created_at")
    @classmethod
    def require_timezone_aware_created_at(cls, value: datetime) -> datetime:
        """Reject naive datetimes so persisted values always have a timezone."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must include a timezone.")
        return value


class User(BaseModel):
    """Represent a user managed by the application."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = Field(
        default=None,
        description="UUID identifying the user; optional when creating a user.",
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        description="User's name.",
    )
    email: str = Field(
        min_length=3,
        max_length=254,
        description="User's email address.",
    )
