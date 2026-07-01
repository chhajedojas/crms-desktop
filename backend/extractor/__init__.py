"""
Extractor package for CRMS.

This package provides metadata extraction for document files.
"""

from extractor.factory import ExtractorFactory
from extractor.base_extractor import (
    BaseExtractor,
    ExtractionError,
    EncryptedDocumentError,
    CorruptedDocumentError,
    UnsupportedFormatError,
    PasswordProtectedError,
)
from extractor.data_structures import (
    ExtractedField,
    CommonMetadata,
    BusinessMetadata,
    ExtractionResult,
    ConfidenceSource,
    ExtractionStatus,
)
from extractor.pdf_extractor import PdfExtractor
from extractor.excel_extractor import ExcelExtractor
from extractor.word_extractor import WordExtractor
from extractor.image_extractor import ImageExtractor

__all__ = [
    "ExtractorFactory",
    "BaseExtractor",
    "ExtractionError",
    "EncryptedDocumentError",
    "CorruptedDocumentError",
    "UnsupportedFormatError",
    "PasswordProtectedError",
    "ExtractedField",
    "CommonMetadata",
    "BusinessMetadata",
    "ExtractionResult",
    "ConfidenceSource",
    "ExtractionStatus",
    "PdfExtractor",
    "ExcelExtractor",
    "WordExtractor",
    "ImageExtractor",
]
