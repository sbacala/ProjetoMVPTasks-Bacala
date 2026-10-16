"""Persistence-layer exceptions exposed to application services."""


class RepositoryConflictError(Exception):
    """Raised when a persistence constraint prevents creating an entity."""
