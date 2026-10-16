"""Unit tests for task services using an isolated SQLite database."""

from collections.abc import Generator
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database_models import Base
from app.models import TaskCreate, TaskUpdate
from app.repositories.task_repository import TaskRepository
from app.services.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.services.task_service import TaskService


@pytest.fixture
def task_service() -> Generator[TaskService, None, None]:
    """Provide a task service backed by a fresh in-memory SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    with session_factory() as session:
        yield TaskService(TaskRepository(session))

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_create_task_with_valid_data(task_service: TaskService) -> None:
    """Creating a valid task assigns an ID and persists its fields."""
    task = TaskCreate(
        title="Prepare release",
        description="Review changes before release.",
    )

    created_task = task_service.create_task(task)

    assert created_task.id is not None
    assert created_task.title == "Prepare release"
    assert created_task.description == "Review changes before release."
    assert created_task.status is False
    assert task_service.get_task(created_task.id) == created_task


def test_create_task_with_short_title_raises_validation_error(
    task_service: TaskService,
) -> None:
    """A task title shorter than three characters is rejected."""
    with pytest.raises(ValidationError):
        task_service.create_task(TaskCreate(title="ab"))


def test_update_task_marks_task_as_completed(task_service: TaskService) -> None:
    """Updating a task can change its status to completed."""
    created_task = task_service.create_task(TaskCreate(title="Complete review"))
    update = TaskUpdate(title=created_task.title, status=True)

    updated_task = task_service.update_task(created_task.id, update)

    assert updated_task.id == created_task.id
    assert updated_task.status is True
    assert task_service.get_task(created_task.id).status is True


def test_get_task_with_unknown_id_raises_not_found(
    task_service: TaskService,
) -> None:
    """Looking up an unknown task ID raises the domain not-found error."""
    with pytest.raises(EntityNotFoundError):
        task_service.get_task(uuid4())


def test_delete_task_with_unknown_id_raises_not_found(
    task_service: TaskService,
) -> None:
    """Deleting an unknown task ID raises the domain not-found error."""
    with pytest.raises(EntityNotFoundError):
        task_service.delete_task(uuid4())


def test_task_title_is_trimmed_and_description_has_a_limit() -> None:
    """Task input normalizes titles and rejects oversized descriptions."""
    normalized = TaskCreate(title="  Plan release  ")
    assert normalized.title == "Plan release"

    with pytest.raises(ValidationError):
        TaskCreate(title="   ")
    with pytest.raises(ValidationError):
        TaskCreate(title="Valid title", description="x" * 2001)


def test_persisted_created_at_is_timezone_aware_utc(
    task_service: TaskService,
) -> None:
    """SQLite round-trips persisted task timestamps as UTC-aware values."""
    created = task_service.create_task(TaskCreate(title="Check UTC timestamp"))
    loaded = task_service.get_task(created.id)

    assert loaded.created_at.tzinfo is not None
    assert loaded.created_at.utcoffset().total_seconds() == 0


@pytest.mark.parametrize(
    ("offset", "limit"),
    [(-1, 10), (0, 0), (0, 101)],
)
def test_service_rejects_invalid_pagination(
    task_service: TaskService,
    offset: int,
    limit: int,
) -> None:
    """Business logic enforces pagination limits outside HTTP requests."""
    with pytest.raises(ValueError):
        task_service.list_tasks(offset=offset, limit=limit)


def test_duplicate_insert_race_returns_domain_conflict(
    task_service: TaskService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A primary-key conflict at insert is translated to a domain error."""
    existing = task_service.create_task(TaskCreate(title="Existing task"))
    monkeypatch.setattr(
        "app.services.task_service.uuid4",
        lambda: existing.id,
    )

    with pytest.raises(EntityAlreadyExistsError):
        task_service.create_task(TaskCreate(title="Concurrent duplicate"))
