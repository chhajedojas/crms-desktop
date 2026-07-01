"""
Repository package for CRMS.

This package contains repository interfaces and implementations.
Application layer should depend on interfaces, not concrete implementations.
"""

from repositories.interfaces import (
    DocumentRepositoryInterface,
    MetadataRepositoryInterface,
    RelationshipRepositoryInterface,
    AuditLogRepositoryInterface,
    VersionLogRepositoryInterface,
)
from repositories.unit_of_work import UnitOfWork

# Concrete implementations are NOT exported
# Application layer should use interfaces for dependency injection

__all__ = [
    # Interfaces for dependency injection
    "DocumentRepositoryInterface",
    "MetadataRepositoryInterface",
    "RelationshipRepositoryInterface",
    "AuditLogRepositoryInterface",
    "VersionLogRepositoryInterface",
    # Unit of Work for transaction management
    "UnitOfWork",
]
