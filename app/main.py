"""FastAPI application exposing CRUD operations for tasks."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
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
    """Initialize database tables when the API starts."""
    create_tables()
    yield


app = FastAPI(
    title="Task Management API",
    description="A REST API for creating and managing tasks.",
    lifespan=lifespan,
)

FRONTEND_FILE = Path(__file__).parent / "static" / "index.html"


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


@app.get("/tasks", response_model=list[Task], summary="List tasks")
def list_tasks(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    task_status: bool | None = Query(default=None, alias="status"),
) -> list[Task]:
    """List all tasks, optionally filtering by completion status.

    Args:
        task_status: If provided, only return tasks with this status.

    Returns:
        The matching tasks.
    """
    return task_service.list_tasks(task_status)


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
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


@app.get("/tasks/{task_id}", response_model=Task, summary="Get a task")
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


@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task")
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
