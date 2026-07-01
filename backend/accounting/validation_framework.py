"""
Validation framework for accounting metadata engine.

This module provides tools for validating extraction accuracy against
ground truth data and calculating precision, recall, and F1 scores.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import date
from accounting.accounting_extractor import AccountingMetadataExtractor, ExtractedAccountingField


@dataclass
class GroundTruth:
    """Ground truth for a document."""

    document_type: str  # Tax Invoice, Purchase Invoice, Credit Note, etc.
    invoice_number: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    customer_name: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[date] = None
    amount: Optional[float] = None
    taxable_amount: Optional[float] = None
    cgst: Optional[float] = None
    sgst: Optional[float] = None
    igst: Optional[float] = None
    currency: Optional[str] = None
    hsn_sac: Optional[str] = None
    po_number: Optional[str] = None
    ref_number: Optional[str] = None
    document_title: Optional[str] = None


@dataclass
class ExtractionMetrics:
    """Metrics for a single field extraction."""

    field_name: str
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    extraction_errors: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Complete validation report."""

    total_documents: int = 0
    document_types: Dict[str, int] = field(default_factory=dict)
    field_metrics: Dict[str, ExtractionMetrics] = field(default_factory=dict)
    overall_success_rate: float = 0.0
    success_cases: List[str] = field(default_factory=list)
    failure_cases: List[str] = field(default_factory=list)
    common_errors: Dict[str, int] = field(default_factory=dict)


class ValidationFramework:
    """Framework for validating accounting metadata extraction."""

    def __init__(self):
        """Initialize validation framework."""
        self.extractor = AccountingMetadataExtractor()
        self.supported_fields = [
            "invoice_number",
            "gstin",
            "pan",
            "customer_name",
            "vendor_name",
            "invoice_date",
            "amount",
            "taxable_amount",
            "cgst",
            "sgst",
            "igst",
        ]

    def calculate_metrics(
        self,
        extracted: Optional[ExtractedAccountingField],
        ground_truth: Optional[Any],
        field_name: str,
    ) -> ExtractionMetrics:
        """
        Calculate precision, recall, and F1 score for a field.

        Args:
            extracted: Extracted field
            ground_truth: Ground truth value
            field_name: Name of the field

        Returns:
            ExtractionMetrics with calculated metrics
        """
        metrics = ExtractionMetrics(field_name=field_name)

        # Determine true positives, false positives, false negatives
        if extracted is not None and ground_truth is not None:
            # Both present - check if match
            if self._values_match(extracted.value, ground_truth, field_name):
                metrics.true_positives = 1
            else:
                metrics.false_positives = 1
                metrics.extraction_errors.append(
                    f"Value mismatch: extracted={extracted.value}, ground_truth={ground_truth}"
                )
        elif extracted is not None and ground_truth is None:
            # Extracted but not in ground truth - false positive
            metrics.false_positives = 1
            metrics.extraction_errors.append(f"False positive: extracted={extracted.value}")
        elif extracted is None and ground_truth is not None:
            # Not extracted but in ground truth - false negative
            metrics.false_negatives = 1
            metrics.extraction_errors.append(f"False negative: ground_truth={ground_truth}")
        # Both None - no error

        # Calculate precision, recall, F1
        total_predicted = metrics.true_positives + metrics.false_positives
        total_actual = metrics.true_positives + metrics.false_negatives

        if total_predicted > 0:
            metrics.precision = metrics.true_positives / total_predicted
        if total_actual > 0:
            metrics.recall = metrics.true_positives / total_actual
        if metrics.precision + metrics.recall > 0:
            metrics.f1_score = (
                2 * metrics.precision * metrics.recall / (metrics.precision + metrics.recall)
            )

        return metrics

    def _values_match(self, extracted: Any, ground_truth: Any, field_name: str) -> bool:
        """Check if extracted value matches ground truth."""
        if field_name in ["invoice_date"]:
            # Date comparison
            if isinstance(extracted, date) and isinstance(ground_truth, date):
                return extracted == ground_truth
            return str(extracted) == str(ground_truth)
        elif field_name in ["amount", "taxable_amount", "cgst", "sgst", "igst"]:
            # Numeric comparison with tolerance
            try:
                extracted_val = float(extracted) if extracted else 0.0
                ground_truth_val = float(ground_truth) if ground_truth else 0.0
                return abs(extracted_val - ground_truth_val) < 0.01
            except (ValueError, TypeError):
                return str(extracted) == str(ground_truth)
        else:
            # String comparison
            return str(extracted).strip() == str(ground_truth).strip()

    def validate_document(
        self, text: str, ground_truth: GroundTruth
    ) -> Dict[str, ExtractionMetrics]:
        """
        Validate extraction against ground truth for a single document.

        Args:
            text: Document text
            ground_truth: Ground truth data

        Returns:
            Dictionary of field_name -> ExtractionMetrics
        """
        # Extract all fields
        extracted_fields = self.extractor.extract_all(text)

        # Calculate metrics for each field
        metrics = {}
        for field_name in self.supported_fields:
            extracted = extracted_fields.get(field_name)
            ground_truth_value = getattr(ground_truth, field_name, None)
            metrics[field_name] = self.calculate_metrics(extracted, ground_truth_value, field_name)

        return metrics

    def validate_batch(self, documents: List[tuple[str, GroundTruth]]) -> ValidationReport:
        """
        Validate extraction against ground truth for a batch of documents.

        Args:
            documents: List of (text, ground_truth) tuples

        Returns:
            ValidationReport with aggregated metrics
        """
        report = ValidationReport(total_documents=len(documents))

        # Aggregate metrics across all documents
        for text, ground_truth in documents:
            document_type = ground_truth.document_type
            report.document_types[document_type] = report.document_types.get(document_type, 0) + 1

            # Validate document
            document_metrics = self.validate_document(text, ground_truth)

            # Aggregate metrics
            for field_name, metrics in document_metrics.items():
                if field_name not in report.field_metrics:
                    report.field_metrics[field_name] = ExtractionMetrics(field_name=field_name)

                aggregate = report.field_metrics[field_name]
                aggregate.true_positives += metrics.true_positives
                aggregate.false_positives += metrics.false_positives
                aggregate.false_negatives += metrics.false_negatives
                aggregate.extraction_errors.extend(metrics.extraction_errors)

        # Calculate final metrics for each field
        for field_name, metrics in report.field_metrics.items():
            total_predicted = metrics.true_positives + metrics.false_positives
            total_actual = metrics.true_positives + metrics.false_negatives

            if total_predicted > 0:
                metrics.precision = metrics.true_positives / total_predicted
            if total_actual > 0:
                metrics.recall = metrics.true_positives / total_actual
            if metrics.precision + metrics.recall > 0:
                metrics.f1_score = (
                    2 * metrics.precision * metrics.recall / (metrics.precision + metrics.recall)
                )

        # Calculate overall success rate
        total_fields = len(report.field_metrics) * report.total_documents
        total_fp = sum(m.false_positives for m in report.field_metrics.values())
        total_fn = sum(m.false_negatives for m in report.field_metrics.values())
        total_errors = total_fp + total_fn
        report.overall_success_rate = (
            1.0 - (total_errors / total_fields) if total_fields > 0 else 0.0
        )

        # Identify common errors
        for metrics in report.field_metrics.values():
            for error in metrics.extraction_errors:
                report.common_errors[error] = report.common_errors.get(error, 0) + 1

        return report

    def print_report(self, report: ValidationReport):
        """Print validation report to console."""
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)
        print(f"\nTotal Documents: {report.total_documents}")
        print("Document Types:")
        for doc_type, count in report.document_types.items():
            print(f"  {doc_type}: {count}")
        print(f"\nOverall Success Rate: {report.overall_success_rate:.2%}")

        print("\n" + "-" * 80)
        print("FIELD METRICS")
        print("-" * 80)
        print(f"{'Field':<20} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
        print("-" * 80)

        for field_name, metrics in sorted(report.field_metrics.items()):
            print(
                f"{field_name:<20} {metrics.precision:<12.2%} "
                f"{metrics.recall:<12.2%} {metrics.f1_score:<12.2%}"
            )

        print("\n" + "-" * 80)
        print("COMMON ERRORS")
        print("-" * 80)
        for error, count in sorted(report.common_errors.items(), key=lambda x: -x[1])[:10]:
            print(f"  {count}x: {error}")

        print("\n" + "=" * 80)
