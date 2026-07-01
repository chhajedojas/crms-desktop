"""
Excel metadata extractor.

Extracts metadata from Excel documents using openpyxl.
"""

from pathlib import Path
from datetime import datetime, timezone
from extractor.base_extractor import BaseExtractor
from extractor.data_structures import (
    ExtractionResult,
    CommonMetadata,
    BusinessMetadata,
    ExtractionStatus,
)

try:
    import openpyxl

    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ExcelExtractor(BaseExtractor):
    """Extractor for Excel documents."""

    SUPPORTED_EXTENSIONS = {".xlsx", ".xls"}

    def __init__(self):
        """Initialize Excel extractor."""
        super().__init__()
        if not OPENPYXL_AVAILABLE:
            self.logger.warning("openpyxl not available, Excel extraction disabled")

    def can_extract(self, file_path: Path) -> bool:
        """Check if file is an Excel document."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract metadata from Excel document."""
        if not OPENPYXL_AVAILABLE:
            return ExtractionResult(
                status=ExtractionStatus.UNSUPPORTED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=["openpyxl not available"],
            )

        start_time = datetime.now(timezone.utc)
        errors = []
        warnings = []

        try:
            # Load workbook
            workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)

            # Extract common metadata
            common_metadata = self._extract_excel_common_metadata(file_path, workbook)

            # Extract business metadata (placeholder)
            business_metadata = BusinessMetadata()

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()

            return ExtractionResult(
                status=ExtractionStatus.SUCCESS,
                common_metadata=common_metadata,
                business_metadata=business_metadata,
                errors=errors,
                warnings=warnings,
                extraction_time=duration,
            )

        except Exception as e:
            self.logger.error(f"Error extracting Excel metadata: {str(e)}")
            return ExtractionResult(
                status=ExtractionStatus.FAILED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=[str(e)],
                extraction_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )
        finally:
            if "workbook" in locals():
                workbook.close()

    def _extract_excel_common_metadata(self, file_path: Path, workbook) -> CommonMetadata:
        """Extract common metadata from Excel."""
        stat = file_path.stat()

        return CommonMetadata(
            filename=file_path.name,
            extension=file_path.suffix.lower(),
            file_size=stat.st_size,
            creation_date=None,  # Excel doesn't reliably store creation date
            modification_date=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            page_count=len(workbook.sheetnames),  # Number of sheets
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if file_path.suffix.lower() == ".xlsx"
            else "application/vnd.ms-excel",
        )
