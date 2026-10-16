"""Abstract repository contract shared by application repositories."""

from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar
from uuid import UUID

from pydantic import BaseModel

from app.models import Task

EntityT = TypeVar("EntityT", bound=BaseModel)


class IRepository(ABC, Generic[EntityT]):
    """Define persistence operations required by application services."""

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> EntityT | None:
        """Return an entity by UUID.

        Args:
            entity_id: UUID of the entity to retrieve.

        Returns:
            The entity, or None if no matching record exists.
        """

    @abstractmethod
    def get_all(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[EntityT]:
        """Return entities within optional page bounds.

        Args:
            offset: Number of entities to skip.
            limit: Maximum number to return, or None for no limit.

        Returns:
            Entities in stable repository-defined order.
        """

    @abstractmethod
    def create(self, entity: EntityT) -> EntityT:
        """Persist a new entity.

        Args:
            entity: Entity to store, including its identifier.

        Returns:
            The stored entity, including database-generated values.
        """

    @abstractmethod
    def update(self, entity_id: UUID, entity: EntityT) -> EntityT | None:
        """Replace an entity if it exists.

        Args:
            entity_id: UUID of the entity to replace.
            entity: Replacement field values.

        Returns:
            The updated entity, or None if it does not exist.
        """

    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by UUID.

        Args:
            entity_id: UUID of the entity to delete.

        Returns:
            True if an entity was deleted; otherwise False.
        """


class TaskRepositoryProtocol(Protocol):
    """Persistence operations consumed by task business logic."""

    def get_by_id(self, entity_id: UUID) -> Task | None:
        """Return a task by UUID, or None if it does not exist.

        Args:
            entity_id: UUID of the task to retrieve.

        Returns:
            The matching task, or None.
        """

    def list_by_status(
        self,
        task_status: bool | None,
        *,
        offset: int,
        limit: int,
    ) -> list[Task]:
        """Return a status-filtered task page.

        Args:
            task_status: Completion status to match, or None for all tasks.
            offset: Number of matching tasks to skip.
            limit: Maximum number of tasks to return.

        Returns:
            Matching tasks in stable order.
        """

    def create(self, entity: Task) -> Task:
        """Persist a task.

        Args:
            entity: Task entity to store.

        Returns:
            The stored task.
        """

    def update(self, entity_id: UUID, entity: Task) -> Task | None:
        """Replace a persisted task if it exists.

        Args:
            entity_id: UUID of the task to replace.
            entity: Replacement field values.

        Returns:
            The updated task, or None if it does not exist.
        """

    def delete(self, entity_id: UUID) -> bool:
        """Delete a task by UUID.

        Args:
            entity_id: UUID of the task to delete.

        Returns:
            True if a task was deleted; otherwise False.
        """
