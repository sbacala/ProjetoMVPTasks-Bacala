"""Business operations for tasks."""

from uuid import UUID, uuid4

from app.models import Task, TaskCreate, TaskUpdate
from app.repositories.exceptions import RepositoryConflictError
from app.repositories.interfaces import TaskRepositoryProtocol
from app.services.exceptions import EntityAlreadyExistsError, EntityNotFoundError


class TaskService:
    """Coordinate task business rules and task persistence."""

    def __init__(self, repository: TaskRepositoryProtocol) -> None:
        """Create a task service with its persistence dependency.

        Args:
            repository: Repository used to store and retrieve tasks.
        """
        self._repository = repository

    def list_tasks(
        self,
        task_status: bool | None = None,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Task]:
        """Return a page of tasks, optionally filtered by completion status.

        Args:
            task_status: If provided, include only tasks with this status.
            offset: Number of matching tasks to skip.
            limit: Maximum number of tasks to return.

        Returns:
            The matching tasks.
        """
        if offset < 0:
            raise ValueError("offset must be non-negative.")
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100.")
        return self._repository.list_by_status(
            task_status,
            offset=offset,
            limit=limit,
        )

    def create_task(self, task: TaskCreate) -> Task:
        """Create a task and assign its server-generated UUID.

        Args:
            task: Task data to persist.

        Returns:
            The persisted task.

        Raises:
            EntityAlreadyExistsError: If persistence reports a UUID conflict.
        """
        task_id = uuid4()
        entity = Task(
            id=task_id,
            title=task.title,
            description=task.description,
            status=task.status,
        )
        try:
            return self._repository.create(entity)
        except RepositoryConflictError as error:
            raise EntityAlreadyExistsError(
                f"Task with id {task_id} already exists."
            ) from error

    def get_task(self, task_id: UUID) -> Task:
        """Retrieve a task by UUID.

        Args:
            task_id: UUID of the task to retrieve.

        Returns:
            The matching task.

        Raises:
            EntityNotFoundError: If no task has the requested UUID.
        """
        task = self._repository.get_by_id(task_id)
        if task is None:
            raise EntityNotFoundError(f"Task {task_id} was not found.")
        return task

    def update_task(self, task_id: UUID, task: TaskUpdate) -> Task:
        """Replace task fields while preserving its UUID and creation time.

        Args:
            task_id: UUID of the task to update.
            task: Replacement task data.

        Returns:
            The updated task.

        Raises:
            EntityNotFoundError: If no task has the requested UUID.
        """
        existing_task = self.get_task(task_id)
        updated_task = existing_task.model_copy(update=task.model_dump())
        result = self._repository.update(task_id, updated_task)
        if result is None:
            raise EntityNotFoundError(f"Task {task_id} was not found.")
        return result

    def delete_task(self, task_id: UUID) -> None:
        """Delete a task by UUID.

        Args:
            task_id: UUID of the task to delete.

        Raises:
            EntityNotFoundError: If no task has the requested UUID.
        """
        if not self._repository.delete(task_id):
            raise EntityNotFoundError(f"Task {task_id} was not found.")
