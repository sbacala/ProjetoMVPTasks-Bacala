"""FastAPI application exposing CRUD operations for tasks."""

import os
import secrets
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Response,
    Security,
    status,
)
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database import create_tables, get_db
from app.models import Task
from app.repositories.task_repository import TaskRepository
from app.services.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.services.task_service import TaskService


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Validate configuration and initialize database tables on startup."""
    api_key = os.getenv("API_KEY")
    if api_key is None or len(api_key) < 32:
        raise RuntimeError("API_KEY must be configured with at least 32 characters.")
    create_tables()
    yield


app = FastAPI(
    title="Task Management API",
    description="A REST API for creating and managing tasks.",
    lifespan=lifespan,
)

FRONTEND_FILE = Path(__file__).parent / "static" / "index.html"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    """Reject task API requests unless they include the configured API key."""
    configured_key = os.getenv("API_KEY")
    if configured_key is None or len(configured_key) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key is not configured.",
        )
    if api_key is None or not secrets.compare_digest(
        api_key.encode("utf-8"),
        configured_key.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )


def get_task_service(
    session: Annotated[Session, Depends(get_db)],
) -> TaskService:
    """Provide a task service backed by a request-scoped database session.

    Returns:
        The task service dependency.
    """
    return TaskService(TaskRepository(session))


@app.get("/", include_in_schema=False)
def get_frontend() -> FileResponse:
    """Serve the task-management web interface."""
    return FileResponse(FRONTEND_FILE)


@app.get(
    "/tasks",
    response_model=list[Task],
    summary="List tasks",
    dependencies=[Depends(require_api_key)],
)
def list_tasks(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    task_status: bool | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Task]:
    """List a page of tasks, optionally filtering by completion status.

    Args:
        task_status: If provided, only return tasks with this status.
        limit: Maximum number of tasks to return (1–100).
        offset: Number of matching tasks to skip.

    Returns:
        The matching tasks.
    """
    return task_service.list_tasks(task_status, offset=offset, limit=limit)


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    dependencies=[Depends(require_api_key)],
)
def create_task(
    task: Task,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> Task:
    """Create a task and assign it a UUID if one was not supplied.

    Args:
        task: The task data to create.

    Returns:
        The created task.

    Raises:
        HTTPException: If the supplied UUID is already in use.
    """
    try:
        return task_service.create_task(task)
    except EntityAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Get a task",
    dependencies=[Depends(require_api_key)],
)
def get_task(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> Task:
    """Return a task by UUID.

    Args:
        task_id: UUID of the task to retrieve.

    Returns:
        The matching task.

    Raises:
        HTTPException: If no task with the UUID exists.
    """
    try:
        return task_service.get_task(task_id)
    except EntityNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        ) from error


@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Update a task",
    dependencies=[Depends(require_api_key)],
)
def update_task(
    task_id: UUID,
    task: Task,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> Task:
    """Replace a task's editable fields while preserving its UUID and creation time.

    Args:
        task_id: UUID of the task to update.
        task: Replacement task data.

    Returns:
        The updated task.

    Raises:
        HTTPException: If no task with the UUID exists.
    """
    try:
        return task_service.update_task(task_id, task)
    except EntityNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        ) from error


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    dependencies=[Depends(require_api_key)],
)
def delete_task(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> Response:
    """Delete a task by UUID.

    Args:
        task_id: UUID of the task to delete.

    Returns:
        An empty response.

    Raises:
        HTTPException: If no task with the UUID exists.
    """
    try:
        task_service.delete_task(task_id)
    except EntityNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
