"""SQLAlchemy-backed implementation of the repository contract."""

from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database_models import EntityRecord
from app.repositories.exceptions import RepositoryConflictError
from app.repositories.interfaces import IRepository

EntityT = TypeVar("EntityT", bound=BaseModel)
RecordT = TypeVar("RecordT", bound=EntityRecord)


class SqlAlchemyRepository(IRepository[EntityT], Generic[EntityT, RecordT]):
    """Persist Pydantic entities using a SQLAlchemy session."""

    def __init__(
        self,
        session: Session,
        record_type: type[RecordT],
        entity_type: type[EntityT],
    ) -> None:
        """Initialize the repository with a session and model types.

        Args:
            session: SQLAlchemy session used for persistence.
            record_type: ORM class mapped to the database table.
            entity_type: Pydantic schema returned to application services.
        """
        self._session = session
        self._record_type = record_type
        self._entity_type = entity_type

    def get_by_id(self, entity_id: UUID) -> EntityT | None:
        """Return an entity by its UUID, or None when it does not exist."""
        statement = select(self._record_type).where(
            self._record_type.id == entity_id
        )
        record = self._session.scalar(statement)
        if record is None:
            return None
        return self._entity_type.model_validate(record)

    def get_all(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[EntityT]:
        """Return persisted entities within optional page bounds."""
        return self._get_all(offset=offset, limit=limit)

    def _get_all(
        self,
        *,
        offset: int,
        limit: int | None,
        filters: dict[str, object] | None = None,
    ) -> list[EntityT]:
        """Query a stable page and apply internal ORM-column equality filters.

        Args:
            offset: Number of matching records to skip.
            limit: Maximum number of records, or None for no limit.
            filters: Internal ORM field/value pairs used by specialized
                repositories; field names are not accepted from API input.

        Returns:
            Matching entities ordered by their primary key.

        Raises:
            ValueError: If pagination bounds are invalid or a filter field is
                not mapped on the configured record type.
        """
        if offset < 0:
            raise ValueError("offset must be non-negative.")
        if limit is not None and limit < 1:
            raise ValueError("limit must be positive.")
        statement = select(self._record_type)
        for field, value in (filters or {}).items():
            column = getattr(self._record_type, field, None)
            if column is None:
                raise ValueError(f"Unsupported repository filter: {field}")
            statement = statement.where(column == value)
        statement = statement.order_by(self._record_type.id).offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        records = self._session.scalars(statement).all()
        return [self._entity_type.model_validate(record) for record in records]

    def create(self, entity: EntityT) -> EntityT:
        """Persist and return a new entity."""
        entity_id = getattr(entity, "id", None)
        if entity_id is None:
            raise ValueError("Entity must have an id before it can be persisted.")

        record = self._record_type(**entity.model_dump())
        self._session.add(record)
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise RepositoryConflictError from error
        self._session.refresh(record)
        return self._entity_type.model_validate(record)

    def update(self, entity_id: UUID, entity: EntityT) -> EntityT | None:
        """Replace an existing entity, or return None when it does not exist."""
        record = self._session.get(self._record_type, entity_id)
        if record is None:
            return None

        for field, value in entity.model_dump(exclude={"id"}).items():
            setattr(record, field, value)

        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise
        self._session.refresh(record)
        return self._entity_type.model_validate(record)

    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity and report whether it existed."""
        record = self._session.get(self._record_type, entity_id)
        if record is None:
            return False
        self._session.delete(record)
        self._session.commit()
        return True
