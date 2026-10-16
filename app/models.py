"""Pydantic models for the task management API."""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Task(BaseModel):
    """Represent a task managed by the application."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = Field(
        default=None,
        description="UUID identifying the task; optional when creating a task.",
    )
    title: str = Field(
        min_length=3,
        max_length=100,
        description="Required task title, between 3 and 100 characters.",
    )
    description: str | None = Field(
        default=None,
        description="Optional task description.",
    )
    status: bool = Field(
        default=False,
        description="Whether the task is complete.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC date and time when the task was created.",
    )


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
