"""
Synthetic invoice generator for testing accounting metadata extraction.

This module generates synthetic invoices with known ground truth values
for testing extraction accuracy.
"""

import random
from datetime import date, timedelta
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class InvoiceGroundTruth:
    """Ground truth for a synthetic invoice."""

    invoice_number: str
    customer_name: str
    vendor_name: str
    gstin: str
    pan: str
    invoice_date: date
    financial_year: str
    amount: float
    taxable_amount: float
    cgst: float
    sgst: float
    igst: float
    total_tax: float
    currency: str
    hsn_sac: str
    po_number: str
    ref_number: str
    document_title: str


class SyntheticInvoiceGenerator:
    """Generator for synthetic invoices."""

    def __init__(self):
        """Initialize synthetic invoice generator."""
        self.customer_names = [
            "Acme Corporation",
            "Global Tech Solutions",
            "Prime Logistics",
            "Stellar Industries",
            "Nexus Enterprises",
            "Quantum Systems",
            "Apex Innovations",
            "Vertex Technologies",
            "Pinnacle Services",
            "Summit Holdings",
        ]

        self.vendor_names = [
            "Supply Chain Partners",
            "Industrial Supplies Ltd",
            "Business Essentials Inc",
            "Professional Services Group",
            "Manufacturing Excellence",
        ]

        self.currencies = ["INR", "USD", "EUR", "GBP"]

    def generate_gstin(self) -> str:
        """Generate a valid GSTIN format (15 chars)."""
        # State code (01-37) = 2 chars
        state_code = f"{random.randint(1, 37):02d}"

        # PAN-like part (5 letters + 4 digits + 1 letter) = 10 chars
        pan_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pan_part = (
            "".join(random.choice(pan_chars) for _ in range(5))
            + f"{random.randint(1000, 9999)}"
            + random.choice(pan_chars)
        )

        # Generate random suffix (Z + 2 chars) = 3 chars
        suffix = "Z" + "".join(
            random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(2)
        )

        return state_code + pan_part + suffix  # 2 + 10 + 3 = 15

    def generate_pan(self) -> str:
        """Generate a valid PAN format."""
        pan_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        return (
            "".join(random.choice(pan_chars) for _ in range(5))
            + f"{random.randint(1000, 9999)}"
            + random.choice(pan_chars)
        )

    def generate_invoice_number(self, document_type: str = "Tax Invoice") -> str:
        """Generate an invoice number based on document type."""
        prefixes = {
            "Tax Invoice": ["INV", "INV-", "INV/", "BILL", "BILL-", "INVOICE", "Invoice"],
            "Credit Note": ["CN", "CN-", "CN/", "CREDIT", "CREDIT-", "CREDIT NOTE"],
            "Debit Note": ["DN", "DN-", "DN/", "DEBIT", "DEBIT-", "DEBIT NOTE"],
            "Quotation": ["QUOT", "QUOT-", "QUOT/", "QUOTATION", "QUOT-", "QUOTATION"],
            "Purchase Invoice": ["PO", "PO-", "PO/", "PURCHASE", "PURCHASE-", "PURCHASE ORDER"],
            "Bank Statement": ["STM", "STM-", "STM/", "STATEMENT", "STATEMENT-"],
        }

        valid_prefixes = prefixes.get(document_type, prefixes["Tax Invoice"])
        prefix = random.choice(valid_prefixes)
        number = random.randint(1000, 999999)
        return f"{prefix}{number}"

    def generate_date(self) -> date:
        """Generate a random invoice date within last 2 years."""
        days_ago = random.randint(0, 730)
        return date.today() - timedelta(days=days_ago)

    def calculate_financial_year(self, invoice_date: date) -> str:
        """Calculate financial year from invoice date."""
        if invoice_date.month >= 4:
            return f"{invoice_date.year}-{str(invoice_date.year + 1)[2:]}"
        else:
            return f"{invoice_date.year - 1}-{str(invoice_date.year)[2:]}"

    def generate_amount(self) -> float:
        """Generate a random amount."""
        return round(random.uniform(1000, 100000), 2)

    def generate_hsn_sac(self) -> str:
        """Generate a random HSN/SAC code."""
        return str(random.randint(1000, 9999))

    def generate_po_number(self) -> str:
        """Generate a purchase order number."""
        prefixes = ["PO", "PO-", "PO/", "PO#", "PURCHASE"]
        prefix = random.choice(prefixes)
        number = random.randint(1000, 99999)
        return f"{prefix}{number}"

    def generate_ref_number(self) -> str:
        """Generate a reference number."""
        prefixes = ["REF", "REF-", "REF/", "REF#", "REFERENCE"]
        prefix = random.choice(prefixes)
        number = random.randint(1000, 99999)
        return f"{prefix}{number}"

    def generate_invoice_text(self, ground_truth: InvoiceGroundTruth) -> str:
        """Generate invoice text from ground truth."""
        lines = [
            "INVOICE",
            f"Document Title: {ground_truth.document_title}",
            f"Invoice No: {ground_truth.invoice_number}",
            f"Invoice Date: {ground_truth.invoice_date.strftime('%d-%m-%Y')}",
            f"Customer: {ground_truth.customer_name}",
            f"Vendor: {ground_truth.vendor_name}",
            f"GSTIN: {ground_truth.gstin}",
            f"PAN: {ground_truth.pan}",
            f"Currency: {ground_truth.currency}",
            f"HSN/SAC: {ground_truth.hsn_sac}",
            f"PO Number: {ground_truth.po_number}",
            f"Reference: {ground_truth.ref_number}",
            f"Financial Year: {ground_truth.financial_year}",
            f"Taxable Amount: ₹{ground_truth.taxable_amount:.2f}",
            f"CGST: ₹{ground_truth.cgst:.2f}",
            f"SGST: ₹{ground_truth.sgst:.2f}",
            f"IGST: ₹{ground_truth.igst:.2f}",
            f"Total Tax: ₹{ground_truth.total_tax:.2f}",
            f"Total Amount: ₹{ground_truth.amount:.2f}",
        ]

        return "\n".join(lines)

    def generate_invoice(self, document_type: str = "Tax Invoice") -> Tuple[InvoiceGroundTruth, str]:
        """Generate a complete synthetic invoice."""
        invoice_date = self.generate_date()
        taxable_amount = self.generate_amount()

        # Calculate taxes (18% GST)
        cgst = taxable_amount * 0.09
        sgst = taxable_amount * 0.09
        igst = 0.0  # Intra-state
        total_tax = cgst + sgst
        amount = taxable_amount + total_tax

        ground_truth = InvoiceGroundTruth(
            invoice_number=self.generate_invoice_number(document_type),
            customer_name=random.choice(self.customer_names),
            vendor_name=random.choice(self.vendor_names),
            gstin=self.generate_gstin(),
            pan=self.generate_pan(),
            invoice_date=invoice_date,
            financial_year=self.calculate_financial_year(invoice_date),
            amount=amount,
            taxable_amount=taxable_amount,
            cgst=cgst,
            sgst=sgst,
            igst=igst,
            total_tax=total_tax,
            currency=random.choice(self.currencies),
            hsn_sac=self.generate_hsn_sac(),
            po_number=self.generate_po_number(),
            ref_number=self.generate_ref_number(),
            document_title=document_type,
        )

        text = self.generate_invoice_text(ground_truth)

        return ground_truth, text

    def generate_batch(self, count: int) -> List[Tuple[InvoiceGroundTruth, str]]:
        """Generate a batch of synthetic invoices."""
        return [self.generate_invoice() for _ in range(count)]
