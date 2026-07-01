"""
Domain entities for CRMS.

This module contains pure Python domain entities that represent
the business objects in the system. These are separate from
the SQLAlchemy ORM models to maintain clean separation between
domain and persistence layers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    INDEXED = "indexed"
    PROCESSING = "processing"
    ERROR = "error"
    ARCHIVED = "archived"


class ChangeType(str, Enum):
    """Version log change type."""
    NEW = "new"
    MODIFIED = "modified"
    DELETED = "deleted"


class RelationshipType(str, Enum):
    """Document relationship types."""
    INVOICE_TO_PAYMENT = "invoice_to_payment"
    INVOICE_TO_DELIVERY = "invoice_to_delivery"
    DELIVERY_TO_LEDGER = "delivery_to_ledger"
    PAYMENT_TO_LEDGER = "payment_to_ledger"
    QUOTATION_TO_INVOICE = "quotation_to_invoice"
    REFERENCE = "reference"


@dataclass
class Document:
    """Document domain entity."""
    id: Optional[int] = None
    file_path: str = ""
    original_path: str = ""
    file_name: str = ""
    file_size: int = 0
    file_hash: str = ""
    file_type: str = ""
    mime_type: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    indexed_date: Optional[datetime] = None
    is_duplicate: bool = False
    duplicate_of_id: Optional[int] = None
    reorganized_path: Optional[str] = None
    financial_year: Optional[str] = None
    document_type: Optional[str] = None
    status: DocumentStatus = DocumentStatus.INDEXED
    content_extracted: bool = False
    ocr_processed: bool = False

    def __post_init__(self):
        """Validate document entity."""
        if not self.file_path:
            raise ValueError("file_path is required")
        if not self.file_name:
            raise ValueError("file_name is required")
        if not self.file_hash:
            raise ValueError("file_hash is required")
        if not self.file_type:
            raise ValueError("file_type is required")
        if self.file_size < 0:
            raise ValueError("file_size must be non-negative")


@dataclass
class Metadata:
    """Metadata domain entity."""
    id: Optional[int] = None
    document_id: int = 0
    key: str = ""
    value: Optional[str] = None
    confidence: float = 1.0
    extraction_method: Optional[str] = None
    needs_review: bool = False
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate metadata entity."""
        if not self.document_id:
            raise ValueError("document_id is required")
        if not self.key:
            raise ValueError("key is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class Relationship:
    """Relationship domain entity."""
    id: Optional[int] = None
    source_document_id: int = 0
    target_document_id: int = 0
    relationship_type: RelationshipType = RelationshipType.REFERENCE
    confidence: float = 1.0
    created_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate relationship entity."""
        if not self.source_document_id:
            raise ValueError("source_document_id is required")
        if not self.target_document_id:
            raise ValueError("target_document_id is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class AuditLog:
    """Audit log domain entity."""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None
    action: str = ""
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None

    def __post_init__(self):
        """Validate audit log entity."""
        if not self.action:
            raise ValueError("action is required")


@dataclass
class VersionLog:
    """Version log domain entity."""
    id: Optional[int] = None
    document_id: int = 0
    version_number: int = 0
    file_hash: str = ""
    file_size: int = 0
    modified_date: Optional[datetime] = None
    change_type: ChangeType = ChangeType.NEW
    previous_version_id: Optional[int] = None
    created_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate version log entity."""
        if not self.document_id:
            raise ValueError("document_id is required")
        if not self.file_hash:
            raise ValueError("file_hash is required")
        if self.file_size < 0:
            raise ValueError("file_size must be non-negative")
