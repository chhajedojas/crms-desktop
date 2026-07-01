"""
Accounting metadata extraction package.

This package provides production-grade extraction of accounting fields
with validation, confidence scoring, and cross-field validation.
"""

from accounting.accounting_extractor import (
    AccountingMetadataExtractor,
    ExtractedAccountingField,
    ValidationStatus,
    ExtractionMethod,
    RegexPatterns,
    ValidationRules,
    ConfidenceScoring,
    CrossFieldValidator,
)
from accounting.synthetic_generator import SyntheticInvoiceGenerator, InvoiceGroundTruth
from accounting.validation_framework import (
    ValidationFramework,
    GroundTruth,
    ExtractionMetrics,
    ValidationReport,
)

__all__ = [
    "AccountingMetadataExtractor",
    "ExtractedAccountingField",
    "ValidationStatus",
    "ExtractionMethod",
    "RegexPatterns",
    "ValidationRules",
    "ConfidenceScoring",
    "CrossFieldValidator",
    "SyntheticInvoiceGenerator",
    "InvoiceGroundTruth",
    "ValidationFramework",
    "GroundTruth",
    "ExtractionMetrics",
    "ValidationReport",
]
