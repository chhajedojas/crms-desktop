"""
Abstract repository interfaces for CRMS.

This module defines the interfaces that repositories must implement.
This enables dependency inversion and makes the application layer
independent of concrete repository implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain import Document, Metadata, Relationship, AuditLog, VersionLog


class DocumentRepositoryInterface(ABC):
    """Interface for Document repository."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Document]:
        """Get document by ID."""
        pass

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Document]:
        """Get all documents with optional pagination."""
        pass

    @abstractmethod
    def create(self, entity: Document) -> Document:
        """Create a new document."""
        pass

    @abstractmethod
    def update(self, entity: Document) -> Document:
        """Update an existing document."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete a document by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all documents."""
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if document exists by ID."""
        pass

    @abstractmethod
    def get_by_file_path(self, file_path: str) -> Optional[Document]:
        """Get document by file path."""
        pass

    @abstractmethod
    def get_by_file_hash(self, file_hash: str) -> List[Document]:
        """Get documents by file hash."""
        pass

    @abstractmethod
    def get_by_financial_year(self, financial_year: str) -> List[Document]:
        """Get documents by financial year."""
        pass

    @abstractmethod
    def get_by_document_type(self, document_type: str) -> List[Document]:
        """Get documents by document type."""
        pass

    @abstractmethod
    def get_duplicates(self) -> List[Document]:
        """Get all duplicate documents."""
        pass

    @abstractmethod
    def search_by_name(self, name_pattern: str) -> List[Document]:
        """Search documents by file name pattern."""
        pass

    @abstractmethod
    def get_unprocessed(self) -> List[Document]:
        """Get documents that haven't been processed yet."""
        pass


class MetadataRepositoryInterface(ABC):
    """Interface for Metadata repository."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Metadata]:
        """Get metadata by ID."""
        pass

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Metadata]:
        """Get all metadata with optional pagination."""
        pass

    @abstractmethod
    def create(self, entity: Metadata) -> Metadata:
        """Create new metadata."""
        pass

    @abstractmethod
    def update(self, entity: Metadata) -> Metadata:
        """Update existing metadata."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete metadata by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all metadata."""
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if metadata exists by ID."""
        pass

    @abstractmethod
    def get_by_document_id(self, document_id: int) -> List[Metadata]:
        """Get all metadata for a document."""
        pass

    @abstractmethod
    def get_by_key(self, document_id: int, key: str) -> Optional[Metadata]:
        """Get metadata by document ID and key."""
        pass

    @abstractmethod
    def get_needs_review(self) -> List[Metadata]:
        """Get all metadata that needs review."""
        pass

    @abstractmethod
    def get_low_confidence(self, threshold: float = 0.7) -> List[Metadata]:
        """Get metadata with confidence below threshold."""
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: int) -> int:
        """Delete all metadata for a document."""
        pass


class RelationshipRepositoryInterface(ABC):
    """Interface for Relationship repository."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Relationship]:
        """Get relationship by ID."""
        pass

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Relationship]:
        """Get all relationships with optional pagination."""
        pass

    @abstractmethod
    def create(self, entity: Relationship) -> Relationship:
        """Create a new relationship."""
        pass

    @abstractmethod
    def update(self, entity: Relationship) -> Relationship:
        """Update an existing relationship."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete a relationship by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all relationships."""
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if relationship exists by ID."""
        pass


class AuditLogRepositoryInterface(ABC):
    """Interface for Audit Log repository."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[AuditLog]:
        """Get audit log entry by ID."""
        pass

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[AuditLog]:
        """Get all audit log entries with optional pagination."""
        pass

    @abstractmethod
    def create(self, entity: AuditLog) -> AuditLog:
        """Create a new audit log entry."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all audit log entries."""
        pass


class VersionLogRepositoryInterface(ABC):
    """Interface for Version Log repository."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[VersionLog]:
        """Get version log entry by ID."""
        pass

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[VersionLog]:
        """Get all version log entries with optional pagination."""
        pass

    @abstractmethod
    def create(self, entity: VersionLog) -> VersionLog:
        """Create a new version log entry."""
        pass

    @abstractmethod
    def update(self, entity: VersionLog) -> VersionLog:
        """Update an existing version log entry."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete a version log entry by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all version log entries."""
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if version log entry exists by ID."""
        pass

    @abstractmethod
    def get_by_document_id(self, document_id: int) -> List[VersionLog]:
        """Get all version logs for a document."""
        pass
