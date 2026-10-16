"""SQLAlchemy repository implementation for users."""

from sqlalchemy.orm import Session

from app.database_models import UserRecord
from app.models import User
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository[User, UserRecord]):
    """Persist users in the configured relational database."""

    def __init__(self, session: Session) -> None:
        """Initialize the user repository.

        Args:
            session: SQLAlchemy session used for persistence.
        """
        super().__init__(session, UserRecord, User)
