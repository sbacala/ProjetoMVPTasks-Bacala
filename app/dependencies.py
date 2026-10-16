"""Composition root for FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.interfaces import TaskRepositoryProtocol
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService


def get_task_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaskRepositoryProtocol:
    """Provide a task repository bound to the current request session.

    Args:
        session: Request-scoped SQLAlchemy session.

    Returns:
        Repository implementation satisfying the task persistence protocol.
    """
    return TaskRepository(session)


def get_task_service(
    repository: Annotated[
        TaskRepositoryProtocol,
        Depends(get_task_repository),
    ],
) -> TaskService:
    """Provide a task service without coupling routes to persistence.

    Args:
        repository: Task repository supplied by the dependency graph.

    Returns:
        Service coordinating task operations.
    """
    return TaskService(repository)
