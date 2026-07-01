"""
Core exceptions for CRMS backend.
Defines all custom exceptions used throughout the application.
"""

from typing import Optional


class CRMSException(Exception):
    """Base exception for all CRMS errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(CRMSException):
    """Raised when configuration is invalid or missing."""

    pass


class DatabaseError(CRMSException):
    """Raised when database operations fail."""

    pass


class FileProcessingError(CRMSException):
    """Raised when file processing fails."""

    pass


class DocumentNotFoundError(CRMSException):
    """Raised when a document is not found."""

    pass


class MetadataExtractionError(CRMSException):
    """Raised when metadata extraction fails."""

    pass


class OCRError(CRMSException):
    """Raised when OCR processing fails."""

    pass


class ClassificationError(CRMSException):
    """Raised when document classification fails."""

    pass


class ValidationError(CRMSException):
    """Raised when validation fails."""

    pass


class ReorganizationError(CRMSException):
    """Raised when reorganization fails."""

    pass


class UndoError(CRMSException):
    """Raised when undo operation fails."""

    pass


class SearchError(CRMSException):
    """Raised when search operation fails."""

    pass


class ReportGenerationError(CRMSException):
    """Raised when report generation fails."""

    pass


class IPCError(CRMSException):
    """Raised when IPC communication fails."""

    pass


class PluginError(CRMSException):
    """Raised when plugin operation fails."""

    pass


class JobQueueError(CRMSException):
    """Raised when job queue operation fails."""

    pass


class AnalyticsError(CRMSException):
    """Raised when analytics operation fails."""

    pass
