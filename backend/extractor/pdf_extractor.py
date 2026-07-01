"""
PDF metadata extractor.

Extracts metadata from PDF documents using pypdf/PyPDF2.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
from extractor.base_extractor import (
    BaseExtractor,
    ExtractionError,
    EncryptedDocumentError,
    CorruptedDocumentError,
)
from extractor.data_structures import (
    ExtractionResult,
    CommonMetadata,
    BusinessMetadata,
    ExtractedField,
    ConfidenceSource,
    ExtractionStatus,
)
from core import get_logger

try:
    import pypdf

    PDF_LIB = pypdf
    PDF_LIB_NAME = "pypdf"
except ImportError:
    try:
        import PyPDF2

        PDF_LIB = PyPDF2
        PDF_LIB_NAME = "PyPDF2"
    except ImportError:
        PDF_LIB = None
        PDF_LIB_NAME = None


class PdfExtractor(BaseExtractor):
    """Extractor for PDF documents."""

    SUPPORTED_EXTENSIONS = {".pdf"}

    def __init__(self):
        """Initialize PDF extractor."""
        super().__init__()
        if PDF_LIB is None:
            self.logger.warning(
                "No PDF library available (pypdf or PyPDF2), PDF extraction disabled"
            )

    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a PDF."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extract metadata from PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            ExtractionResult with extracted metadata
        """
        if PDF_LIB is None:
            return ExtractionResult(
                status=ExtractionStatus.UNSUPPORTED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=["No PDF library available (pypdf or PyPDF2)"],
            )

        start_time = datetime.now(timezone.utc)
        errors = []
        warnings = []
        raw_text = None

        try:
            # Open PDF
            with open(file_path, "rb") as f:
                pdf_reader = PDF_LIB.PdfReader(f)

                # Check if encrypted
                if pdf_reader.is_encrypted:
                    try:
                        # Try to decrypt with empty password
                        pdf_reader.decrypt("")
                    except Exception:
                        raise EncryptedDocumentError("PDF is encrypted")

                # Extract common metadata
                common_metadata = self._extract_pdf_common_metadata(file_path, pdf_reader)

                # Extract text
                raw_text = self._extract_text(pdf_reader)

                # Extract business metadata
                business_metadata = self._extract_business_metadata(raw_text)

                duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                return ExtractionResult(
                    status=ExtractionStatus.SUCCESS,
                    common_metadata=common_metadata,
                    business_metadata=business_metadata,
                    errors=errors,
                    warnings=warnings,
                    extraction_time=duration,
                    raw_text=raw_text,
                )

        except EncryptedDocumentError as e:
            return ExtractionResult(
                status=ExtractionStatus.ENCRYPTED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=[str(e)],
                extraction_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )
        except CorruptedDocumentError as e:
            return ExtractionResult(
                status=ExtractionStatus.CORRUPTED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=[str(e)],
                extraction_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )
        except FileNotFoundError as e:
            return ExtractionResult(
                status=ExtractionStatus.FAILED,
                common_metadata=CommonMetadata(
                    filename=file_path.name,
                    extension=file_path.suffix.lower(),
                    file_size=0,
                ),
                business_metadata=BusinessMetadata(),
                errors=[f"File not found: {str(e)}"],
                extraction_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )
        except Exception as e:
            self.logger.error(f"Error extracting PDF metadata: {str(e)}")
            return ExtractionResult(
                status=ExtractionStatus.FAILED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=[str(e)],
                extraction_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )

    def _extract_pdf_common_metadata(self, file_path: Path, pdf_reader) -> CommonMetadata:
        """Extract common metadata from PDF."""
        stat = file_path.stat()

        # Get PDF info
        pdf_info = pdf_reader.metadata

        # Extract dates from PDF metadata
        creation_date = None
        modification_date = None

        if pdf_info:
            if "/CreationDate" in pdf_info:
                try:
                    creation_date = self._parse_pdf_date(pdf_info["/CreationDate"])
                except Exception:
                    pass
            if "/ModDate" in pdf_info:
                try:
                    modification_date = self._parse_pdf_date(pdf_info["/ModDate"])
                except Exception:
                    pass

        return CommonMetadata(
            filename=file_path.name,
            extension=file_path.suffix.lower(),
            file_size=stat.st_size,
            creation_date=creation_date,
            modification_date=modification_date,
            page_count=len(pdf_reader.pages),
            mime_type="application/pdf",
        )

    def _parse_pdf_date(self, pdf_date_str: str) -> datetime:
        """Parse PDF date string to datetime."""
        # PDF dates are in format: D:YYYYMMDDHHmmSS
        if pdf_date_str.startswith("D:"):
            pdf_date_str = pdf_date_str[2:]
        try:
            year = int(pdf_date_str[:4])
            month = int(pdf_date_str[4:6])
            day = int(pdf_date_str[6:8])
            hour = int(pdf_date_str[8:10])
            minute = int(pdf_date_str[10:12])
            second = int(pdf_date_str[12:14])
            return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
        except Exception:
            return None

    def _extract_text(self, pdf_reader) -> str:
        """Extract text from all pages."""
        text_parts = []
        for page in pdf_reader.pages:
            try:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            except Exception as e:
                self.logger.warning(f"Error extracting text from page: {str(e)}")
        return "\n".join(text_parts)

    def _extract_business_metadata(self, text: str) -> BusinessMetadata:
        """Extract business metadata from text using heuristics."""
        # Placeholder - will be implemented with regex patterns
        # This is a stub for now
        return BusinessMetadata()
