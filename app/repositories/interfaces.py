"""Abstract repository contract shared by application repositories."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

EntityT = TypeVar("EntityT", bound=BaseModel)


class IRepository(ABC, Generic[EntityT]):
    """Define persistence operations required by application services."""

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> EntityT | None:
        """Return an entity by its UUID, or None when it does not exist."""

    @abstractmethod
    def get_all(
        self,
        offset: int = 0,
        limit: int | None = None,
        filters: Mapping[str, object] | None = None,
    ) -> list[EntityT]:
        """Return persisted entities matching optional filters and page bounds."""

    @abstractmethod
    def create(self, entity: EntityT) -> EntityT:
        """Persist and return a new entity."""

    @abstractmethod
    def update(self, entity_id: UUID, entity: EntityT) -> EntityT | None:
        """Replace an existing entity, or return None when it does not exist."""

    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity and report whether it existed."""
