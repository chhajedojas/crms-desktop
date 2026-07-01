"""
Real-world validation tests for accounting metadata engine.

This module validates extraction accuracy using synthetic data to simulate
real-world validation with ground truth.
"""

from accounting.validation_framework import ValidationFramework, GroundTruth
from accounting.synthetic_generator import SyntheticInvoiceGenerator


def create_realistic_invoice(document_type: str) -> tuple[str, GroundTruth]:
    """Create a realistic invoice with ground truth."""
    generator = SyntheticInvoiceGenerator()
    ground_truth, text = generator.generate_invoice(document_type)

    # Update document type
    ground_truth.document_type = document_type

    return text, ground_truth


def run_validation():
    """Run validation on synthetic documents."""
    framework = ValidationFramework()

    # Generate documents
    documents = []

    # 50 Tax Invoices
    for _ in range(50):
        documents.append(create_realistic_invoice("Tax Invoice"))

    # 20 Purchase Invoices
    for _ in range(20):
        documents.append(create_realistic_invoice("Purchase Invoice"))

    # 10 Credit Notes
    for _ in range(10):
        documents.append(create_realistic_invoice("Credit Note"))

    # 10 Debit Notes
    for _ in range(10):
        documents.append(create_realistic_invoice("Debit Note"))

    # 10 Quotations
    for _ in range(10):
        documents.append(create_realistic_invoice("Quotation"))

    # 10 Bank Statements
    for _ in range(10):
        documents.append(create_realistic_invoice("Bank Statement"))

    # Run validation
    report = framework.validate_batch(documents)

    # Print report
    framework.print_report(report)

    return report


if __name__ == "__main__":
    report = run_validation()
