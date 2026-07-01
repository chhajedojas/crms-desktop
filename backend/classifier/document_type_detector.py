"""
Document type detection engine.

This module provides deterministic document type detection using
filename patterns, folder names, keywords, text content, and layout heuristics.
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum


class DocumentType(Enum):
    """Supported document types."""
    TAX_INVOICE = "Tax Invoice"
    PURCHASE_INVOICE = "Purchase Invoice"
    CREDIT_NOTE = "Credit Note"
    DEBIT_NOTE = "Debit Note"
    QUOTATION = "Quotation"
    BANK_STATEMENT = "Bank Statement"
    LEDGER = "Ledger"
    SALARY_SLIP = "Salary Slip"
    DELIVERY_CHALLAN = "Delivery Challan"
    UNKNOWN = "Unknown"


@dataclass
class ClassificationResult:
    """Result of document type classification."""
    document_type: DocumentType
    confidence: float
    reasons: List[str] = field(default_factory=list)

    def __str__(self):
        return f"{self.document_type.value} (Confidence: {self.confidence:.2%})"


class DocumentTypeDetector:
    """Deterministic document type detector."""

    def __init__(self):
        """Initialize document type detector."""
        self.filename_patterns = self._init_filename_patterns()
        self.folder_patterns = self._init_folder_patterns()
        self.keywords = self._init_keywords()
        self.excel_sheet_patterns = self._init_excel_sheet_patterns()

    def _init_filename_patterns(self) -> dict[DocumentType, List[str]]:
        """Initialize filename patterns for each document type."""
        return {
            DocumentType.TAX_INVOICE: [
                r".*[Ii]nvoice.*\.pdf",
                r".*[Ii]nvoice.*\.xlsx",
                r".*[Ii]nvoice.*\.xls",
                r".*[Tt]ax.*[Ii]nvoice.*",
                r"\d{5}.*[Ss]erum.*\.pdf",
                r"\d{5}.*[Ss]erum.*\.xlsx",
            ],
            DocumentType.CREDIT_NOTE: [
                r".*[Cc]redit.*[Nn]ote.*",
                r".*[Cc]n.*",
            ],
            DocumentType.DEBIT_NOTE: [
                r".*[Dd]ebit.*[Nn]ote.*",
                r".*[Dd]n.*",
            ],
            DocumentType.QUOTATION: [
                r".*[Qq]uotation.*",
                r".*[Qq]uot.*",
                r".*[Ee]stimate.*",
            ],
            DocumentType.SALARY_SLIP: [
                r".*[Ss]alary.*[Ss]lip.*",
                r".*[Ss]lip.*",
                r".*-.*-[0-9]{4}\.pdf",
                r".*-.*-[0-9]{4}\.xlsx",
            ],
            DocumentType.BANK_STATEMENT: [
                r".*[Ss]tatement.*",
                r".*[Bb]ank.*",
                r"[A-Z]{3}\s+\d{2}\.pdf",
            ],
            DocumentType.LEDGER: [
                r".*[Ll]edger.*",
                r".*[Ss]ales.*[Ll]edger.*",
            ],
            DocumentType.DELIVERY_CHALLAN: [
                r".*[Cc]hallan.*",
                r".*[Dd]elivery.*",
            ],
        }

    def _init_folder_patterns(self) -> dict[DocumentType, List[str]]:
        """Initialize folder patterns for each document type."""
        return {
            DocumentType.TAX_INVOICE: [
                r".*[Tt]ax.*[Ii]nvoice.*",
                r".*[Ii]nvoice.*",
            ],
            DocumentType.SALARY_SLIP: [
                r".*[Ss]alary.*[Ss]lip.*",
            ],
            DocumentType.BANK_STATEMENT: [
                r".*[Ss]tatement.*",
            ],
            DocumentType.LEDGER: [
                r".*[Ll]edger.*",
            ],
        }

    def _init_keywords(self) -> dict[DocumentType, List[str]]:
        """Initialize keywords for each document type."""
        return {
            DocumentType.TAX_INVOICE: [
                "tax invoice",
                "invoice no",
                "invoice number",
                "gstin",
                "pan",
                "cgst",
                "sgst",
                "igst",
                "total amount",
                "taxable amount",
                "hsn",
                "sac",
            ],
            DocumentType.PURCHASE_INVOICE: [
                "purchase invoice",
                "purchase order",
                "po number",
                "po no",
            ],
            DocumentType.CREDIT_NOTE: [
                "credit note",
                "credit note no",
                "credit no",
            ],
            DocumentType.DEBIT_NOTE: [
                "debit note",
                "debit note no",
                "debit no",
            ],
            DocumentType.QUOTATION: [
                "quotation",
                "quote",
                "estimate",
                "quotation no",
                "quote no",
            ],
            DocumentType.BANK_STATEMENT: [
                "bank statement",
                "statement no",
                "account no",
                "a/c",
                "period",
                "opening balance",
                "closing balance",
            ],
            DocumentType.LEDGER: [
                "ledger",
                "sales ledger",
                "account ledger",
                "ledger account",
            ],
            DocumentType.SALARY_SLIP: [
                "salary slip",
                "payslip",
                "earnings",
                "deductions",
                "net pay",
                "gross pay",
                "designation",
                "employee",
                "employee name",
            ],
            DocumentType.DELIVERY_CHALLAN: [
                "delivery challan",
                "challan",
                "delivery note",
                "consignment",
            ],
        }

    def _init_excel_sheet_patterns(self) -> dict[DocumentType, List[str]]:
        """Initialize Excel sheet name patterns for each document type."""
        return {
            DocumentType.LEDGER: [
                r".*[Ll]edger.*",
                r".*[Ss]ales.*",
            ],
            DocumentType.SALARY_SLIP: [
                r".*[Ss]alary.*",
                r".*[Pp]ayslip.*",
            ],
        }

    def detect_by_filename(self, file_path: str) -> Tuple[Optional[DocumentType], float, List[str]]:
        """Detect document type from filename."""
        filename = os.path.basename(file_path)
        reasons = []

        for doc_type, patterns in self.filename_patterns.items():
            for pattern in patterns:
                if re.match(pattern, filename, re.IGNORECASE):
                    confidence = 0.8
                    reasons.append(f"Filename matches pattern: {pattern}")
                    return doc_type, confidence, reasons

        return None, 0.0, []

    def detect_by_folder(self, file_path: str) -> Tuple[Optional[DocumentType], float, List[str]]:
        """Detect document type from folder name."""
        folder_path = os.path.dirname(file_path)
        folder_name = os.path.basename(folder_path)
        reasons = []

        for doc_type, patterns in self.folder_patterns.items():
            for pattern in patterns:
                if re.match(pattern, folder_name, re.IGNORECASE):
                    confidence = 0.7
                    reasons.append(f"Folder matches pattern: {pattern}")
                    return doc_type, confidence, reasons

        return None, 0.0, []

    def detect_by_keywords(self, text: str) -> Tuple[Optional[DocumentType], float, List[str]]:
        """Detect document type from keywords in text."""
        text_lower = text.lower()
        reasons = []
        scores = {}

        for doc_type, keywords in self.keywords.items():
            match_count = 0
            matched_keywords = []

            for keyword in keywords:
                if keyword in text_lower:
                    match_count += 1
                    matched_keywords.append(keyword)

            if match_count > 0:
                confidence = min(0.6 + (match_count * 0.1), 0.95)
                scores[doc_type] = (confidence, matched_keywords)

        if scores:
            # Return the highest scoring document type
            best_type, (confidence, matched) = max(scores.items(), key=lambda x: x[1][0])
            reasons.append(f"Keywords matched: {', '.join(matched)}")
            return best_type, confidence, reasons

        return None, 0.0, []

    def detect_by_excel_sheets(self, file_path: str) -> Tuple[Optional[DocumentType], float, List[str]]:
        """Detect document type from Excel sheet names."""
        if not file_path.endswith((".xlsx", ".xls")):
            return None, 0.0, []

        try:
            import openpyxl

            wb = openpyxl.load_workbook(file_path, read_only=True)
            sheet_names = wb.worksheets
            reasons = []

            for doc_type, patterns in self.excel_sheet_patterns.items():
                for sheet in sheet_names:
                    sheet_name = sheet.title
                    for pattern in patterns:
                        if re.match(pattern, sheet_name, re.IGNORECASE):
                            confidence = 0.75
                            reasons.append(f"Sheet name matches pattern: {sheet_name}")
                            return doc_type, confidence, reasons

            return None, 0.0, []
        except Exception:
            return None, 0.0, []

    def detect_by_layout(self, text: str) -> Tuple[Optional[DocumentType], float, List[str]]:
        """Detect document type from layout heuristics."""
        reasons = []

        # Check for table-like structure (ledger)
        lines = text.split("\n")
        if len(lines) > 50:
            # Count lines with multiple tab-separated or comma-separated values
            table_lines = 0
            for line in lines:
                if line.count("\t") > 3 or line.count(",") > 3:
                    table_lines += 1

            if table_lines > len(lines) * 0.5:
                confidence = 0.65
                reasons.append("Layout appears to be table-based (ledger)")
                return DocumentType.LEDGER, confidence, reasons

        return None, 0.0, []

    def classify(self, file_path: str, text: str = None) -> ClassificationResult:
        """
        Classify document type using all detection methods.

        Args:
            file_path: Path to the document file
            text: Extracted text content (optional)

        Returns:
            ClassificationResult with document type, confidence, and reasons
        """
        votes = {}
        all_reasons = []

        # Detect by filename (highest priority)
        doc_type, confidence, reasons = self.detect_by_filename(file_path)
        if doc_type:
            votes[doc_type] = votes.get(doc_type, 0) + confidence
            all_reasons.extend(reasons)

        # Detect by folder (high priority)
        doc_type, confidence, reasons = self.detect_by_folder(file_path)
        if doc_type:
            votes[doc_type] = votes.get(doc_type, 0) + confidence
            all_reasons.extend(reasons)

        # Detect by Excel sheets (medium priority)
        doc_type, confidence, reasons = self.detect_by_excel_sheets(file_path)
        if doc_type:
            votes[doc_type] = votes.get(doc_type, 0) + confidence
            all_reasons.extend(reasons)

        # Detect by keywords (lower priority)
        if text:
            doc_type, confidence, reasons = self.detect_by_keywords(text)
            if doc_type:
                # Don't use keywords if filename/folder already matched ledger
                # Ledger files often contain invoice keywords but are not invoices
                if doc_type == DocumentType.TAX_INVOICE and "Ledger" in str(votes.keys()):
                    # Skip invoice keywords for ledger files
                    pass
                else:
                    votes[doc_type] = votes.get(doc_type, 0) + confidence
                    all_reasons.extend(reasons)

            # Detect by layout (lowest priority)
            doc_type, confidence, reasons = self.detect_by_layout(text)
            if doc_type:
                votes[doc_type] = votes.get(doc_type, 0) + confidence
                all_reasons.extend(reasons)

        # Determine final classification
        if votes:
            # Get the document type with the highest vote
            best_type = max(votes.items(), key=lambda x: x[1])[0]
            best_confidence = min(votes[best_type], 1.0)

            # If confidence is below threshold, return UNKNOWN
            if best_confidence < 0.5:
                return ClassificationResult(
                    document_type=DocumentType.UNKNOWN,
                    confidence=best_confidence,
                    reasons=["Confidence below threshold"] + all_reasons,
                )

            return ClassificationResult(
                document_type=best_type,
                confidence=best_confidence,
                reasons=all_reasons,
            )
        else:
            return ClassificationResult(
                document_type=DocumentType.UNKNOWN,
                confidence=0.0,
                reasons=["No detection methods matched"],
            )
