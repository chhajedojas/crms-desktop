"""
Document classification package.

This package provides document type detection and classification.
"""

from classifier.document_type_detector import (
    DocumentType,
    ClassificationResult,
    DocumentTypeDetector,
)

__all__ = [
    "DocumentType",
    "ClassificationResult",
    "DocumentTypeDetector",
]
