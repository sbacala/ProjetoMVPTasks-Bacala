"""Domain exceptions raised by application services."""


class EntityNotFoundError(Exception):
    """Raised when a requested entity does not exist."""


class EntityAlreadyExistsError(Exception):
    """Raised when creating an entity with an existing identifier."""
