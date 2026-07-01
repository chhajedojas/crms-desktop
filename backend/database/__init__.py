"""
Database package for CRMS.

This package contains database-related code including ORM models, mappers,
and connection management. ORM models are implementation details and should
not be exposed outside the persistence layer.
"""

from database.connection import DatabaseConnection
from database.exceptions import (
    RepositoryError,
    EntityNotFoundError,
    DuplicateEntityError,
    InvalidEntityError,
    TransactionError,
    MigrationError,
    QueryError,
)

__all__ = [
    "DatabaseConnection",
    "RepositoryError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "InvalidEntityError",
    "TransactionError",
    "MigrationError",
    "QueryError",
]
