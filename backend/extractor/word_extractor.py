"""
Word metadata extractor.

Extracts metadata from Word documents using python-docx.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
from extractor.base_extractor import BaseExtractor, ExtractionError
from extractor.data_structures import (
    ExtractionResult,
    CommonMetadata,
    BusinessMetadata,
    ExtractionStatus,
)
from core import get_logger

try:
    import docx

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class WordExtractor(BaseExtractor):
    """Extractor for Word documents."""

    SUPPORTED_EXTENSIONS = {".docx"}

    def __init__(self):
        """Initialize Word extractor."""
        super().__init__()
        if not DOCX_AVAILABLE:
            self.logger.warning("python-docx not available, Word extraction disabled")

    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a Word document."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract metadata from Word document."""
        if not DOCX_AVAILABLE:
            return ExtractionResult(
                status=ExtractionStatus.UNSUPPORTED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=["python-docx not available"],
            )

        start_time = datetime.now(timezone.utc)
        errors = []
        warnings = []

        try:
            # Load document
            doc = docx.Document(file_path)

            # Extract common metadata
            common_metadata = self._extract_word_common_metadata(file_path, doc)

            # Extract business metadata (placeholder)
            business_metadata = BusinessMetadata()

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()

            return ExtractionResult(
                status=ExtractionStatus.SUCCESS,
                common_metadata=common_metadata,
                business_metadata=business_metadata,
                errors=errors,
                warnings=warnings,
                extraction_time=duration,
            )

        except Exception as e:
            self.logger.error(f"Error extracting Word metadata: {str(e)}")
            return ExtractionResult(
                status=ExtractionStatus.FAILED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=[str(e)],
                extraction_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )

    def _extract_word_common_metadata(self, file_path: Path, doc) -> CommonMetadata:
        """Extract common metadata from Word."""
        stat = file_path.stat()

        # Get core properties
        core_props = doc.core_properties

        return CommonMetadata(
            filename=file_path.name,
            extension=file_path.suffix.lower(),
            file_size=stat.st_size,
            creation_date=core_props.created if core_props.created else None,
            modification_date=core_props.modified if core_props.modified else None,
            page_count=None,  # Word doesn't have pages in the same sense
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
