# Metadata Extraction Architecture

## Overview

The Metadata Extraction Engine is responsible for understanding document contents and extracting structured metadata from various file formats. It receives ScanResult objects from the Scanner and processes them independently with no global state, making it suitable for parallel execution.

## Extractor Hierarchy

```
BaseExtractor (Abstract)
    ├── PdfExtractor
    ├── ExcelExtractor
    ├── WordExtractor
    └── ImageExtractor

ExtractorFactory (Strategy Pattern)
    └── Selects appropriate extractor based on file extension
```

## Architecture

### Strategy Pattern

The ExtractorFactory uses the Strategy Pattern to select the appropriate extractor based on file extension:

```python
factory = ExtractorFactory()
extractor = factory.get_extractor(file_path)  # Returns appropriate extractor
result = extractor.extract(file_path)  # Extracts metadata
```

### No Global State

Each extractor maintains no global state:
- All state is local to the extraction operation
- Extractors can be instantiated multiple times
- Suitable for parallel execution in worker pools
- Thread-safe by design

### Extractor Responsibilities

**BaseExtractor:**
- Abstract base class defining the interface
- Common metadata extraction (filename, size, dates)
- Error handling framework

**PdfExtractor:**
- PDF text extraction using pypdf/PyPDF2
- Page count extraction
- PDF metadata (creation/modification dates)
- Encrypted PDF detection
- Corrupted PDF handling

**ExcelExtractor:**
- Sheet count extraction
- Core properties extraction
- Password-protected Excel handling
- Workbook metadata

**WordExtractor:**
- Core properties extraction
- Document metadata
- Password-protected Word handling

**ImageExtractor:**
- EXIF metadata extraction
- Image dimensions
- Camera information
- Timestamp extraction

## Confidence Model

Every extracted field includes:

- **value**: The extracted value
- **confidence**: Float from 0.0 to 1.0
- **source**: Source of extraction (REGEX, STRUCTURED, HEURISTIC, METADATA, MANUAL)
- **raw_text**: Original text from document (for debugging)

```python
ExtractedField(
    value="INV-1054",
    confidence=0.98,
    source=ConfidenceSource.REGEX,
    raw_text="Invoice Number: INV-1054"
)
```

### Confidence Sources

- **REGEX**: Extracted using regular expression patterns
- **STRUCTURED**: Extracted from structured document properties
- **HEURISTIC**: Extracted using heuristic rules
- **METADATA**: Extracted from file metadata
- **MANUAL**: Manually entered by user

### Confidence Ranges

- **0.9 - 1.0**: High confidence (well-formatted, matches pattern)
- **0.7 - 0.9**: Medium-high confidence (likely correct)
- **0.5 - 0.7**: Medium confidence (ambiguous but plausible)
- **0.3 - 0.5**: Low-medium confidence (possible but uncertain)
- **0.0 - 0.3**: Low confidence (guess)

## Field Definitions

### Common Metadata

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| filename | string | filesystem | File name |
| extension | string | filesystem | File extension |
| file_size | int | filesystem | File size in bytes |
| creation_date | datetime | filesystem/metadata | File creation date |
| modification_date | datetime | filesystem/metadata | Last modification date |
| page_count | int | document | Number of pages (PDF/Excel) |
| mime_type | string | heuristics | MIME type |

### Business Metadata

| Field | Type | Confidence Source | Description |
|-------|------|-------------------|-------------|
| document_type | string | HEURISTIC | Type of document (invoice, quotation, etc.) |
| invoice_number | string | REGEX | Invoice number |
| quotation_number | string | REGEX | Quotation number |
| customer_name | string | HEURISTIC | Customer name |
| vendor_name | string | HEURISTIC | Vendor/supplier name |
| gstin | string | REGEX | GST identification number |
| pan | string | REGEX | PAN (tax identification) |
| amount | decimal | HEURISTIC | Total amount |
| taxable_amount | decimal | HEURISTIC | Taxable amount |
| gst_amount | decimal | HEURISTIC | GST amount |
| invoice_date | date | REGEX | Invoice date |
| due_date | date | REGEX | Due date |
| financial_year | string | HEURISTIC | Financial year |
| currency | string | REGEX | Currency code |

## Error Handling

### Error Types

1. **EncryptedDocumentError** - PDF is encrypted (password protected)
2. **CorruptedDocumentError** - File is corrupted or malformed
3. **PasswordProtectedError** - Office document is password protected
4. **UnsupportedFormatError** - File format not supported
5. **ExtractionError** - General extraction error

### Error Scenarios

| Scenario | Status | Behavior |
|----------|--------|----------|
| Encrypted PDF | ENCRYPTED | Returns ENCRYPTED status, no metadata |
| Corrupted PDF | CORRUPTED | Returns CORRUPTED status, error message |
| Password-protected Excel | PASSWORD_PROTECTED | Returns PASSWORD_PROTECTED status |
| Unsupported format | UNSUPPORTED | Returns UNSUPPORTED status, error message |
| Timeout | TIMEOUT | Returns TIMEOUT status, partial results |
| Partial extraction | PARTIAL | Returns PARTIAL status, warnings |

### Graceful Degradation

- All errors are caught and reported in ExtractionResult.errors
- Common metadata is extracted even if business metadata fails
- ExtractionResult.status indicates the overall result
- Partial results are preserved (raw_text, warnings)

## Performance

### Extraction Time Estimates

| File Type | Average Time | Peak Memory |
|-----------|--------------|-------------|
| PDF (1 page) | ~0.1s | ~10MB |
| PDF (10 pages) | ~0.5s | ~50MB |
| Excel (1 sheet) | ~0.2s | ~20MB |
| Word (10 pages) | ~0.3s | ~30MB |
| Image (5MB) | ~0.1s | ~15MB |

### Parallel Execution

- **No global state**: Extractors can be instantiated per-worker
- **Thread-safe**: No shared mutable state
- **I/O-bound**: Can parallelize across workers
- **CPU-bound**: Hash generation (if enabled) is CPU-bound

**Recommended Worker Count:** 4-8 workers depending on I/O vs CPU ratio

## Future OCR Integration

### OCR Status Handling

When PDF text extraction fails:
- Return ExtractionStatus.PARTIAL
- Set ExtractionResult.status to PARTIAL
- Add warning: "Text extraction failed, OCR required"
- Set ExtractionResult.raw_text to None
- Return available metadata (file size, page count, etc.)

### OCR Integration Point

```python
if result.status == ExtractionStatus.PARTIAL and "OCR required" in result.warnings:
    # Queue for OCR processing
    ocr_queue.enqueue(file_path)
```

### OCR Metadata Enhancement

OCR will enhance:
- Image-only PDFs (scanned documents)
- Handwritten text extraction
- Improved confidence scores
- Better business metadata extraction

## Extension Points

### Adding New Extractors

1. Create new extractor class inheriting from BaseExtractor
2. Implement `can_extract()` method
3. Implement `extract()` method
4. Add to ExtractorFactory._extractors list
5. Implement tests

Example:
```python
class PowerPointExtractor(BaseExtractor):
    SUPPORTED_EXTENSIONS = {".pptx"}

    def can_extract(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: Path) -> ExtractionResult:
        # Extract PowerPoint metadata
        pass
```

### Adding New Business Fields

1. Add field to BusinessMetadata dataclass
2. Implement extraction logic in appropriate extractor
3. Add confidence scoring
4. Add tests

### Adding New Confidence Sources

1. Add value to ConfidenceSource enum
2. Update confidence scoring logic
3. Document in METADATA_ARCHITECTURE.md

## Testing Strategy

### Unit Tests

- Test each extractor independently
- Test error handling (encrypted, corrupted, missing files)
- Test confidence validation
- Test edge cases (empty files, malformed files)

### Integration Tests

- Test ExtractorFactory selection
- Test with real sample documents
- Test parallel execution
- Test timeout handling

### Sample Documents Required

- Normal invoices (PDF, Excel, Word)
- GST invoices (with GSTIN)
- Blank PDFs
- Encrypted PDFs
- Malformed Office files
- Files with missing fields
- Multiple invoice layouts
- Unicode text

## Benchmark Results

### Performance Benchmarks (Not Yet Run)

Planned benchmarks:
- 1,000 PDFs
- 1,000 Excel files
- 1,000 Word files

Metrics to collect:
- Average extraction time per file type
- Peak memory usage
- Failure rate
- Confidence statistics

## Limitations

### Current Limitations

1. **Business Metadata**: Regex patterns not yet implemented (placeholder)
2. **OCR**: Not implemented (planned for future milestone)
3. **Complex Layouts**: May require advanced heuristics
4. **Handwritten Text**: Requires OCR
5. **Scanned PDFs**: Requires OCR for text extraction

### Known Issues

1. PyPDF2 deprecation warning (pypdf is preferred)
2. EXIF extraction may fail on some image formats
3. Some Office formats may have incomplete metadata

## Recommendations

### For Production Use

1. **Dependencies**: Install required libraries (pypdf, openpyxl, python-docx, Pillow)
2. **Worker Count**: 4-8 workers for parallel extraction
3. **Timeout**: Set reasonable timeout per file (e.g., 30 seconds)
4. **Retry Logic**: Implement retry for transient failures
5. **Monitoring**: Track extraction success/failure rates

### For Large Files

1. **Memory**: Use streaming for very large files (>100MB)
2. **Timeout**: Increase timeout for large files
3. **Chunking**: Process large files in chunks if possible

### For High Throughput

1. **Disable Logging**: Reduce logging overhead
2. **Disable Raw Text**: Don't store raw_text unless needed
3. **Parallel Workers**: Increase worker count
4. **Caching**: Cache extracted metadata

## Conclusion

The Metadata Extraction Engine provides:
- ✅ Strategy pattern for extensible architecture
- ✅ No global state (suitable for parallel execution)
- ✅ Confidence model for all extracted fields
- ✅ Comprehensive error handling
- ✅ Support for PDF, Excel, Word, Images
- ✅ Extension points for new formats and fields
- ⏳ Business metadata extraction (regex patterns) - placeholder
- ⏳ OCR integration - planned for future milestone

**Production Readiness:** Architecture is production-ready. Business metadata extraction with regex patterns should be implemented before full production deployment.
