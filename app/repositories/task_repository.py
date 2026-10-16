"""SQLAlchemy repository implementation for tasks."""

from sqlalchemy.orm import Session

from app.database_models import TaskRecord
from app.models import Task
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository


class TaskRepository(SqlAlchemyRepository[Task, TaskRecord]):
    """Persist tasks in the configured relational database."""

    def __init__(self, session: Session) -> None:
        """Initialize the task repository.

        Args:
            session: SQLAlchemy session used for persistence.
        """
        super().__init__(session, TaskRecord, Task)

    def list_by_status(
        self,
        task_status: bool | None,
        *,
        offset: int,
        limit: int,
    ) -> list[Task]:
        """Return a page of tasks, optionally filtered by completion status.

        Args:
            task_status: Completion status to match, or None for all tasks.
            offset: Number of matching tasks to skip.
            limit: Maximum number of tasks to return (1–100).

        Returns:
            Matching tasks ordered by UUID.

        Raises:
            ValueError: If the requested page exceeds the repository limit or
                has invalid bounds.
        """
        if offset < 0:
            raise ValueError("offset must be non-negative.")
        if limit < 1:
            raise ValueError("limit must be positive.")
        if limit > 100:
            raise ValueError("limit must not exceed 100.")
        filters = {"status": task_status} if task_status is not None else None
        return self._get_all(offset=offset, limit=limit, filters=filters)
