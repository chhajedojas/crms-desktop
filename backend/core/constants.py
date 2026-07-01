"""
Application constants for CRMS backend.
Contains all constant values used throughout the application.
"""

from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""

    TAX_INVOICE = "Tax Invoice"
    PURCHASE_BILL = "Purchase Bill"
    DEBIT_NOTE = "Debit Note"
    CREDIT_NOTE = "Credit Note"
    DELIVERY_CHALLAN = "Delivery Challan"
    LEDGER = "Ledger"
    BANK_STATEMENT = "Bank Statement"
    SALARY_SLIP = "Salary Slip"
    GST_RETURN = "GST Return"
    AUDIT_FILE = "Audit File"
    LEGAL_DOCUMENT = "Legal Document"
    BUSY_BACKUP = "Busy Backup"
    UNKNOWN = "Unknown"


class FileExtension(str, Enum):
    """Supported file extensions."""

    PDF = "pdf"
    XLSX = "xlsx"
    XLS = "xls"
    DOCX = "docx"
    DOC = "doc"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    BMP = "bmp"


class ChangeType(str, Enum):
    """File change type enumeration."""

    NEW = "new"
    MODIFIED = "modified"
    DELETED = "deleted"


class RelationshipType(str, Enum):
    """Document relationship type enumeration."""

    INVOICE_TO_PAYMENT = "invoice_to_payment"
    INVOICE_TO_DELIVERY = "invoice_to_delivery"
    DELIVERY_TO_LEDGER = "delivery_to_ledger"
    PAYMENT_TO_BANK = "payment_to_bank"
    GST_RETURN_TO_INVOICE = "gst_return_to_invoice"


class ValidationType(str, Enum):
    """GST validation type enumeration."""

    FORMAT = "format"
    CHECKSUM = "checksum"
    RATE = "rate"
    MISMATCH = "mismatch"


class SequenceType(str, Enum):
    """Sequence type enumeration."""

    INVOICE_NUMBER = "invoice_number"
    CHALLAN_NUMBER = "challan_number"
    RECEIPT_NUMBER = "receipt_number"


class DocumentStatus(str, Enum):
    """Document processing status."""

    INDEXED = "indexed"
    PROCESSING = "processing"
    FAILED = "failed"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"


class ExtractionMethod(str, Enum):
    """Metadata extraction method enumeration."""

    PDF_TEXT = "pdf_text"
    PDF_OCR = "pdf_ocr"
    EXCEL_CELL = "excel_cell"
    WORD_TEXT = "word_text"
    IMAGE_OCR = "image_ocr"
    MANUAL = "manual"
    AI_EXTRACTION = "ai_extraction"


# Confidence thresholds
CONFIDENCE_HIGH = 0.9
CONFIDENCE_MEDIUM = 0.7
CONFIDENCE_LOW = 0.5
CONFIDENCE_MINIMAL = 0.3

# File size limits
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
CHUNK_SIZE = 8192  # 8 KB

# Processing constants
DEFAULT_BATCH_SIZE = 100
DEFAULT_INDEXING_THREADS = 4
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_BACKOFF = 60  # seconds

# Database constants
SQLITE_TIMEOUT = 30  # seconds
DUCKDB_MEMORY_LIMIT = "1GB"

# IPC constants
IPC_BUFFER_SIZE = 65536  # 64 KB
IPC_TIMEOUT = 300  # seconds

# Financial year constants
FINANCIAL_YEAR_START_MONTH = 4  # April
FINANCIAL_YEAR_START_DAY = 1

# Logging constants
LOG_ROTATION_SIZE = "10 MB"
LOG_RETENTION_DAYS = 30

# Cache constants
DEFAULT_CACHE_TTL = 3600  # 1 hour
DEFAULT_CACHE_SIZE = 1000
