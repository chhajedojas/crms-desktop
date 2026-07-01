"""
Base extractor class for metadata extraction.

All document extractors inherit from this base class.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from extractor.data_structures import ExtractionResult, CommonMetadata
from core import get_logger


class ExtractionError(Exception):
    """Base exception for extraction errors."""

    pass


class EncryptedDocumentError(ExtractionError):
    """Raised when document is encrypted."""

    pass


class CorruptedDocumentError(ExtractionError):
    """Raised when document is corrupted."""

    pass


class UnsupportedFormatError(ExtractionError):
    """Raised when document format is not supported."""

    pass


class PasswordProtectedError(ExtractionError):
    """Raised when document is password protected."""

    pass


class BaseExtractor(ABC):
    """Base class for document metadata extractors."""

    def __init__(self):
        """Initialize base extractor."""
        self.logger = get_logger(__name__)

    @abstractmethod
    def can_extract(self, file_path: Path) -> bool:
        """
        Check if this extractor can handle the given file.

        Args:
            file_path: Path to file

        Returns:
            True if this extractor can handle the file
        """
        pass

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extract metadata from document.

        Args:
            file_path: Path to document

        Returns:
            ExtractionResult with extracted metadata
        """
        pass

    def _extract_common_metadata(self, file_path: Path) -> CommonMetadata:
        """
        Extract common metadata from file.

        Args:
            file_path: Path to file

        Returns:
            CommonMetadata object
        """
        try:
            if not file_path.exists():
                raise ExtractionError(f"File not found: {file_path}")
            stat = file_path.stat()
            return CommonMetadata(
                filename=file_path.name,
                extension=file_path.suffix.lower(),
                file_size=stat.st_size,
                creation_date=None,  # Will be set by subclasses
                modification_date=None,  # Will be set by subclasses
                page_count=None,  # Will be set by subclasses
                mime_type=None,  # Will be set by subclasses
            )
        except ExtractionError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to extract common metadata: {str(e)}")
            raise ExtractionError(f"Failed to extract common metadata: {str(e)}")
