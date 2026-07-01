"""
Metadata extraction data structures.

This module defines the data structures for extracted metadata,
including confidence scores and source information.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum


class ConfidenceSource(Enum):
    """Source of extracted value."""

    REGEX = "regex"
    STRUCTURED = "structured"
    HEURISTIC = "heuristic"
    METADATA = "metadata"
    MANUAL = "manual"


class ExtractionStatus(Enum):
    """Status of extraction operation."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ENCRYPTED = "encrypted"
    PASSWORD_PROTECTED = "password_protected"
    CORRUPTED = "corrupted"
    UNSUPPORTED = "unsupported"
    TIMEOUT = "timeout"


@dataclass
class ExtractedField:
    """Single extracted field with confidence."""

    value: Any
    confidence: float  # 0.0 to 1.0
    source: ConfidenceSource
    raw_text: Optional[str] = None  # Original text from document

    def __post_init__(self):
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class CommonMetadata:
    """Common metadata for all documents."""

    filename: str
    extension: str
    file_size: int
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    page_count: Optional[int] = None
    mime_type: Optional[str] = None


@dataclass
class BusinessMetadata:
    """Business-specific metadata extracted from documents."""

    document_type: Optional[ExtractedField] = None
    invoice_number: Optional[ExtractedField] = None
    quotation_number: Optional[ExtractedField] = None
    customer_name: Optional[ExtractedField] = None
    vendor_name: Optional[ExtractedField] = None
    gstin: Optional[ExtractedField] = None
    pan: Optional[ExtractedField] = None
    amount: Optional[ExtractedField] = None
    taxable_amount: Optional[ExtractedField] = None
    gst_amount: Optional[ExtractedField] = None
    invoice_date: Optional[ExtractedField] = None
    due_date: Optional[ExtractedField] = None
    financial_year: Optional[ExtractedField] = None
    currency: Optional[ExtractedField] = None


@dataclass
class ExtractionResult:
    """Result of metadata extraction."""

    status: ExtractionStatus
    common_metadata: CommonMetadata
    business_metadata: BusinessMetadata
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    extraction_time: float = 0.0  # seconds
    raw_text: Optional[str] = None  # Full extracted text for debugging
