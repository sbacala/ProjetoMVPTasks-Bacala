"""Business operations for users."""

from uuid import UUID, uuid4

from app.models import User
from app.repositories.interfaces import IRepository
from app.services.exceptions import EntityAlreadyExistsError, EntityNotFoundError


class UserService:
    """Coordinate user business rules and user persistence."""

    def __init__(self, repository: IRepository[User]) -> None:
        """Create a user service with its persistence dependency.

        Args:
            repository: Repository used to store and retrieve users.
        """
        self._repository = repository

    def list_users(self) -> list[User]:
        """Return all users.

        Returns:
            The persisted users.
        """
        return self._repository.get_all()

    def create_user(self, user: User) -> User:
        """Create a user and assign a UUID when needed.

        Args:
            user: User data to persist.

        Returns:
            The persisted user.

        Raises:
            EntityAlreadyExistsError: If the user UUID is already in use.
        """
        user_id = user.id or uuid4()
        if self._repository.get_by_id(user_id) is not None:
            raise EntityAlreadyExistsError(
                f"User with id {user_id} already exists."
            )
        return self._repository.create(user.model_copy(update={"id": user_id}))

    def get_user(self, user_id: UUID) -> User:
        """Retrieve a user by UUID.

        Args:
            user_id: UUID of the user to retrieve.

        Returns:
            The matching user.

        Raises:
            EntityNotFoundError: If no user has the requested UUID.
        """
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundError(f"User {user_id} was not found.")
        return user

    def update_user(self, user_id: UUID, user: User) -> User:
        """Replace a user's editable fields while preserving its UUID.

        Args:
            user_id: UUID of the user to update.
            user: Replacement user data.

        Returns:
            The updated user.

        Raises:
            EntityNotFoundError: If no user has the requested UUID.
        """
        self.get_user(user_id)
        updated_user = user.model_copy(update={"id": user_id})
        result = self._repository.update(user_id, updated_user)
        if result is None:
            raise EntityNotFoundError(f"User {user_id} was not found.")
        return result

    def delete_user(self, user_id: UUID) -> None:
        """Delete a user by UUID.

        Args:
            user_id: UUID of the user to delete.

        Raises:
            EntityNotFoundError: If no user has the requested UUID.
        """
        if not self._repository.delete(user_id):
            raise EntityNotFoundError(f"User {user_id} was not found.")
