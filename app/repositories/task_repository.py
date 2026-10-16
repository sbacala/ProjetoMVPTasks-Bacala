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
