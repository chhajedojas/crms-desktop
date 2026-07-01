"""
Persistence-specific exceptions for CRMS.

This module contains custom exceptions for the persistence layer
to provide better error handling and debugging.
"""

from core.exceptions import CRMSException


class RepositoryError(CRMSException):
    """Base exception for repository errors."""
    pass


class EntityNotFoundError(RepositoryError):
    """Raised when an entity is not found in the repository."""
    pass


class DuplicateEntityError(RepositoryError):
    """Raised when attempting to create a duplicate entity."""
    pass


class InvalidEntityError(RepositoryError):
    """Raised when an entity is invalid."""
    pass


class TransactionError(RepositoryError):
    """Raised when a transaction operation fails."""
    pass


class MigrationError(RepositoryError):
    """Raised when a database migration fails."""
    pass


class QueryError(RepositoryError):
    """Raised when a database query fails."""
    pass
