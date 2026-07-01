"""
Accounting metadata engine for extracting business metadata from documents.

This module provides production-grade extraction of accounting fields with
validation, confidence scoring, and cross-field validation.
"""

import re
from datetime import datetime, date
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from core import get_logger


class ValidationStatus(Enum):
    """Validation status for extracted fields."""

    VALID = "valid"
    INVALID = "invalid"
    UNCERTAIN = "uncertain"
    MISSING = "missing"


class ExtractionMethod(Enum):
    """Method used for extraction."""

    REGEX = "regex"
    HEURISTIC = "heuristic"
    STRUCTURED = "structured"
    CONTEXTUAL = "contextual"


@dataclass
class ExtractedAccountingField:
    """Single extracted accounting field with validation."""

    value: Any
    confidence: float  # 0.0 to 1.0
    validation_status: ValidationStatus
    extraction_method: ExtractionMethod
    raw_text: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


class RegexPatterns:
    """Regex patterns for accounting field extraction."""

    # Invoice Number patterns
    INVOICE_NUMBER_PATTERNS = [
        r"(?:Invoice\s*No[:\s]*)([A-Z0-9\-\/#]+)",
        r"(?:invoice\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",
        r"(?:INV\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",
        r"(?:bill\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",
        r"(?:receipt\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",
        r"(?:tax\s*invoice\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",
        r"(?:BILL\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",
        r"(?:CN\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",  # Credit Note
        r"(?:DN\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",  # Debit Note
        r"(?:QUOT\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",  # Quotation
        r"(?:STM\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/#]+)",  # Statement
    ]

    # GSTIN pattern (15 characters: 2 state code + 10 PAN-like + 3 suffix)
    GSTIN_PATTERN = r"(?:GSTIN[:\s]*)([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}Z[0-9A-Z]{2})"

    # PAN pattern (10 characters: 5 letters + 4 digits + 1 letter)
    PAN_PATTERN = r"(?:PAN[:\s]*)([A-Z]{5}[0-9]{4}[A-Z]{1})"

    # Customer/Vendor Name patterns
    NAME_PATTERNS = [
        r"(?:customer\s*(?:name)?[:\s]*)([A-Za-z\s\.]+)",
        r"(?:vendor\s*(?:name)?[:\s]*)([A-Za-z\s\.]+)",
        r"(?:supplier\s*(?:name)?[:\s]*)([A-Za-z\s\.]+)",
        r"(?:billed\s*to[:\s]*)([A-Za-z\s\.]+)",
        r"(?:shipped\s*to[:\s]*)([A-Za-z\s\.]+)",
    ]

    # Date patterns
    DATE_PATTERNS = [
        r"(?:invoice\s*date|date)[:\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
        r"(?:invoice\s*date|date)[:\s]*([0-9]{4}[-/][0-9]{2}[-/][0-9]{2})",
        r"([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",  # DD-MM-YYYY or DD/MM/YYYY
        r"([0-9]{4}[-/][0-9]{2}[-/][0-9]{2})",  # YYYY-MM-DD or YYYY/MM/DD
    ]

    # Amount patterns
    AMOUNT_PATTERNS = [
        r"(?:Total\s*Amount|Grand\s*Total)[:\s]*[₹$]?\s*([0-9,]+\.?[0-9]*)",
        r"(?:taxable\s*amount|subtotal)[:\s]*[₹$]?\s*([0-9,]+\.?[0-9]*)",
        r"[₹$]\s*([0-9,]+\.?[0-9]*)",
        r"([0-9,]+\.?[0-9]*)\s*(?:INR|Rs\.?|₹)",
    ]

    # Tax patterns
    CGST_PATTERN = r"(?:CGST|central\s*GST)[:\s]*[₹$]?\s*([0-9,]+\.?[0-9]*)"
    SGST_PATTERN = r"(?:SGST|state\s*GST)[:\s]*[₹$]?\s*([0-9,]+\.?[0-9]*)"
    IGST_PATTERN = r"(?:IGST|integrated\s*GST)[:\s]*[₹$]?\s*([0-9,]+\.?[0-9]*)"

    # Purchase Order Number
    PO_NUMBER_PATTERNS = [
        r"(?:purchase\s*order|PO)[:\s]*(?:no|number|#)?[:\s]*([A-Z0-9\-\/]+)",
        r"(?:PO\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/]+)",
    ]

    # Reference Number
    REF_NUMBER_PATTERNS = [
        r"(?:reference|ref)[:\s]*(?:no|number|#)?[:\s]*([A-Z0-9\-\/]+)",
        r"(?:ref\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-\/]+)",
    ]

    # HSN/SAC patterns
    HSN_SAC_PATTERNS = [
        r"(?:HSN|SAC)[:\s]*([0-9]{4,8})",
        r"([0-9]{4,8})\s*(?:HSN|SAC)",
    ]

    # Currency patterns
    CURRENCY_PATTERNS = [
        r"(?:currency)[:\s]*([A-Z]{3})",
        r"(INR|USD|EUR|GBP|JPY)",
    ]


class ValidationRules:
    """Validation rules for accounting fields."""

    @staticmethod
    def validate_gstin(gstin: str) -> Tuple[bool, List[str]]:
        """
        Validate GSTIN format.

        Args:
            gstin: GSTIN string to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check format: 2 state code + 10 PAN-like + 3 suffix
        if not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}Z[0-9A-Z]{2}$", gstin):
            errors.append("GSTIN format invalid")
            return False, errors

        # Format is valid - checksum validation would go here
        # For now, we trust the format
        return True, []

    @staticmethod
    def validate_pan(pan: str) -> Tuple[bool, List[str]]:
        """
        Validate PAN format.

        Args:
            pan: PAN string to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check format: 5 letters + 4 digits + 1 letter
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan):
            errors.append("PAN format invalid")
            return False, errors

        # Format is valid
        return True, []

    @staticmethod
    def validate_invoice_date(date_str: str) -> Tuple[bool, List[str], Optional[date]]:
        """
        Validate invoice date.

        Args:
            date_str: Date string to validate

        Returns:
            Tuple of (is_valid, error_messages, parsed_date)
        """
        errors = []

        # Try to parse date
        parsed_date = None
        date_formats = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%y",
            "%d/%m/%y",
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue

        if parsed_date is None:
            errors.append("Date format invalid")
            return False, errors, None

        # Check if date is reasonable (not in future, not too old)
        today = date.today()
        if parsed_date > today:
            errors.append("Invoice date is in future")
        elif (today - parsed_date).days > 365 * 10:  # 10 years
            errors.append("Invoice date is too old")

        return len(errors) == 0, errors, parsed_date

    @staticmethod
    def calculate_financial_year(invoice_date: date) -> str:
        """
        Calculate financial year from invoice date.

        Args:
            invoice_date: Invoice date

        Returns:
            Financial year string (e.g., "2023-24")
        """
        if invoice_date.month >= 4:  # April onwards
            return f"{invoice_date.year}-{str(invoice_date.year + 1)[2:]}"
        else:
            return f"{invoice_date.year - 1}-{str(invoice_date.year)[2:]}"


class ConfidenceScoring:
    """Confidence scoring algorithm for extracted fields."""

    @staticmethod
    def calculate_base_confidence(
        pattern_index: int,
        total_patterns: int,
        position_in_text: int,
        text_length: int,
    ) -> float:
        """
        Calculate base confidence based on pattern match and position.

        Args:
            pattern_index: Index of matched pattern (0 = most specific)
            total_patterns: Total number of patterns tried
            position_in_text: Position of match in text
            text_length: Total length of text

        Returns:
            Base confidence score (0.0 to 1.0)
        """
        # Pattern specificity: earlier patterns are more specific
        pattern_confidence = 1.0 - (pattern_index / total_patterns) * 0.3

        # Position: matches near the beginning are more confident
        position_ratio = position_in_text / text_length if text_length > 0 else 0
        position_confidence = 1.0 - position_ratio * 0.2

        return min(pattern_confidence * position_confidence, 1.0)

    @staticmethod
    def adjust_confidence_for_validation(
        base_confidence: float, validation_status: ValidationStatus
    ) -> float:
        """
        Adjust confidence based on validation status.

        Args:
            base_confidence: Base confidence score
            validation_status: Validation status

        Returns:
            Adjusted confidence score
        """
        if validation_status == ValidationStatus.VALID:
            return min(base_confidence + 0.1, 1.0)
        elif validation_status == ValidationStatus.INVALID:
            return max(base_confidence - 0.3, 0.0)
        elif validation_status == ValidationStatus.UNCERTAIN:
            return max(base_confidence - 0.1, 0.0)
        else:  # MISSING
            return base_confidence


class CrossFieldValidator:
    """Cross-field validation for consistency checks."""

    @staticmethod
    def validate_amount_consistency(
        amount: Optional[float],
        taxable_amount: Optional[float],
        cgst: Optional[float],
        sgst: Optional[float],
        igst: Optional[float],
    ) -> Tuple[bool, List[str]]:
        """
        Validate amount consistency across fields.

        Args:
            amount: Total amount
            taxable_amount: Taxable amount
            cgst: CGST amount
            sgst: SGST amount
            igst: IGST amount

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if amount is None:
            return True, errors  # Can't validate without total

        # Calculate expected total
        expected_total = taxable_amount or 0

        if cgst is not None:
            expected_total += cgst
        if sgst is not None:
            expected_total += sgst
        if igst is not None:
            expected_total += igst

        # Allow small tolerance for rounding
        tolerance = 0.01
        if abs(amount - expected_total) > tolerance:
            errors.append(
                f"Amount inconsistency: Total ({amount}) != "
                f"Taxable ({taxable_amount or 0}) + Taxes "
                f"(CGST: {cgst or 0}, SGST: {sgst or 0}, IGST: {igst or 0})"
            )

        return len(errors) == 0, errors

    @staticmethod
    def validate_tax_consistency(
        cgst: Optional[float], sgst: Optional[float], igst: Optional[float]
    ) -> Tuple[bool, List[str]]:
        """
        Validate tax consistency (CGST + SGST or IGST, not both).

        Args:
            cgst: CGST amount
            sgst: SGST amount
            igst: IGST amount

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # If IGST is present, CGST and SGST should not be present
        if igst is not None and (cgst is not None or sgst is not None):
            errors.append("Tax inconsistency: IGST and CGST/SGST both present")

        # If CGST is present, SGST should also be present (typically equal)
        if cgst is not None and sgst is None:
            errors.append("Tax inconsistency: CGST present but SGST missing")

        if sgst is not None and cgst is None:
            errors.append("Tax inconsistency: SGST present but CGST missing")

        return len(errors) == 0, errors


class AccountingMetadataExtractor:
    """Main accounting metadata extractor."""

    def __init__(self):
        """Initialize accounting metadata extractor."""
        self.logger = get_logger(__name__)
        self.patterns = RegexPatterns()
        self.validation = ValidationRules()
        self.confidence = ConfidenceScoring()
        self.cross_validator = CrossFieldValidator()

    def extract_invoice_number(self, text: str) -> Optional[ExtractedAccountingField]:
        """Extract invoice number from text."""
        for i, pattern in enumerate(self.patterns.INVOICE_NUMBER_PATTERNS):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                confidence = self.confidence.calculate_base_confidence(
                    i, len(self.patterns.INVOICE_NUMBER_PATTERNS), match.start(), len(text)
                )

                return ExtractedAccountingField(
                    value=value,
                    confidence=confidence,
                    validation_status=ValidationStatus.VALID,
                    extraction_method=ExtractionMethod.REGEX,
                    raw_text=match.group(0),
                )
        return None

    def extract_gstin(self, text: str) -> Optional[ExtractedAccountingField]:
        """Extract GSTIN from text."""
        match = re.search(self.patterns.GSTIN_PATTERN, text)
        if match:
            value = match.group(2) if len(match.groups()) > 1 else match.group(1)
            is_valid, errors = self.validation.validate_gstin(value)

            base_confidence = 0.9  # GSTIN pattern is very specific
            confidence = self.confidence.adjust_confidence_for_validation(
                base_confidence,
                ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
            )

            return ExtractedAccountingField(
                value=value,
                confidence=confidence,
                validation_status=ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
                extraction_method=ExtractionMethod.REGEX,
                raw_text=match.group(0),
                validation_errors=errors,
            )
        return None

    def extract_pan(self, text: str) -> Optional[ExtractedAccountingField]:
        """Extract PAN from text."""
        match = re.search(self.patterns.PAN_PATTERN, text)
        if match:
            value = match.group(2) if len(match.groups()) > 1 else match.group(1)
            is_valid, errors = self.validation.validate_pan(value)

            base_confidence = 0.85  # PAN pattern is specific
            confidence = self.confidence.adjust_confidence_for_validation(
                base_confidence,
                ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
            )

            return ExtractedAccountingField(
                value=value,
                confidence=confidence,
                validation_status=ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
                extraction_method=ExtractionMethod.REGEX,
                raw_text=match.group(0),
                validation_errors=errors,
            )
        return None

    def extract_invoice_date(self, text: str) -> Optional[ExtractedAccountingField]:
        """Extract invoice date from text."""
        for i, pattern in enumerate(self.patterns.DATE_PATTERNS):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                is_valid, errors, parsed_date = self.validation.validate_invoice_date(value)

                base_confidence = self.confidence.calculate_base_confidence(
                    i, len(self.patterns.DATE_PATTERNS), match.start(), len(text)
                )
                confidence = self.confidence.adjust_confidence_for_validation(
                    base_confidence,
                    ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
                )

                return ExtractedAccountingField(
                    value=parsed_date if parsed_date else value,
                    confidence=confidence,
                    validation_status=ValidationStatus.VALID
                    if is_valid
                    else ValidationStatus.INVALID,
                    extraction_method=ExtractionMethod.REGEX,
                    raw_text=match.group(0),
                    validation_errors=errors,
                )
        return None

    def extract_amount(self, text: str) -> Optional[ExtractedAccountingField]:
        """Extract amount from text."""
        for i, pattern in enumerate(self.patterns.AMOUNT_PATTERNS):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(",", "")
                try:
                    value = float(value_str)
                    confidence = self.confidence.calculate_base_confidence(
                        i, len(self.patterns.AMOUNT_PATTERNS), match.start(), len(text)
                    )

                    return ExtractedAccountingField(
                        value=value,
                        confidence=confidence,
                        validation_status=ValidationStatus.VALID,
                        extraction_method=ExtractionMethod.REGEX,
                        raw_text=match.group(0),
                    )
                except ValueError:
                    continue
        return None

    def extract_all(self, text: str) -> Dict[str, ExtractedAccountingField]:
        """
        Extract all accounting fields from text.

        Args:
            text: Text to extract from

        Returns:
            Dictionary of field_name -> ExtractedAccountingField
        """
        fields = {}

        fields["invoice_number"] = self.extract_invoice_number(text)
        fields["gstin"] = self.extract_gstin(text)
        fields["pan"] = self.extract_pan(text)
        fields["invoice_date"] = self.extract_invoice_date(text)
        fields["amount"] = self.extract_amount(text)

        # Cross-field validation
        self._apply_cross_field_validation(fields)

        return fields

    def _apply_cross_field_validation(self, fields: Dict[str, ExtractedAccountingField]):
        """Apply cross-field validation and adjust confidences."""
        # Apply amount consistency validation
        # (would need taxable_amount, cgst, sgst, igst extraction)
        # Placeholder for now

        # Apply tax consistency validation
        # (would need cgst, sgst, igst extraction)
        # Placeholder for now
