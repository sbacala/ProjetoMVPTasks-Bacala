"""Business operations for tasks."""

from uuid import UUID, uuid4

from app.models import Task
from app.repositories.interfaces import IRepository
from app.services.exceptions import EntityAlreadyExistsError, EntityNotFoundError


class TaskService:
    """Coordinate task business rules and task persistence."""

    def __init__(self, repository: IRepository[Task]) -> None:
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
        filters = {"status": task_status} if task_status is not None else None
        return self._repository.get_all(
            offset=offset,
            limit=limit,
            filters=filters,
        )

    def create_task(self, task: Task) -> Task:
        """Create a task and assign a UUID when needed.

        Args:
            task: Task data to persist.

        Returns:
            The persisted task.

        Raises:
            EntityAlreadyExistsError: If the task UUID is already in use.
        """
        task_id = task.id or uuid4()
        if self._repository.get_by_id(task_id) is not None:
            raise EntityAlreadyExistsError(
                f"Task with id {task_id} already exists."
            )
        return self._repository.create(task.model_copy(update={"id": task_id}))

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

    def update_task(self, task_id: UUID, task: Task) -> Task:
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
        updated_task = task.model_copy(
            update={"id": task_id, "created_at": existing_task.created_at}
        )
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
