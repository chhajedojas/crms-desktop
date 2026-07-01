"""
Extractor factory using strategy pattern.

Selects appropriate extractor based on file type.
"""

from pathlib import Path
from typing import Optional
from extractor.base_extractor import BaseExtractor
from extractor.pdf_extractor import PdfExtractor
from extractor.excel_extractor import ExcelExtractor
from extractor.word_extractor import WordExtractor
from extractor.image_extractor import ImageExtractor
from extractor.data_structures import (
    ExtractionResult,
    ExtractionStatus,
    CommonMetadata,
    BusinessMetadata,
)
from core import get_logger


class ExtractorFactory:
    """Factory for creating appropriate extractors."""

    def __init__(self):
        """Initialize extractor factory."""
        self.logger = get_logger(__name__)
        self._extractors = [
            PdfExtractor(),
            ExcelExtractor(),
            WordExtractor(),
            ImageExtractor(),
        ]

    def get_extractor(self, file_path: Path) -> Optional[BaseExtractor]:
        """
        Get appropriate extractor for file.

        Args:
            file_path: Path to file

        Returns:
            Extractor instance or None if no suitable extractor found
        """
        for extractor in self._extractors:
            if extractor.can_extract(file_path):
                return extractor
        return None

    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extract metadata from file using appropriate extractor.

        Args:
            file_path: Path to file

        Returns:
            ExtractionResult with extracted metadata
        """
        extractor = self.get_extractor(file_path)
        if extractor is None:
            # No extractor available - return basic info
            stat = file_path.stat()
            common_metadata = CommonMetadata(
                filename=file_path.name,
                extension=file_path.suffix.lower(),
                file_size=stat.st_size,
                creation_date=None,
                modification_date=None,
                page_count=None,
                mime_type=None,
            )
            return ExtractionResult(
                status=ExtractionStatus.UNSUPPORTED,
                common_metadata=common_metadata,
                business_metadata=BusinessMetadata(),
                errors=[f"No extractor available for {file_path.suffix}"],
            )

        return extractor.extract(file_path)
