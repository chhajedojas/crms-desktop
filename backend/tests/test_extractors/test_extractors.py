"""
Unit tests for metadata extractors.
"""

import pytest
import tempfile
from pathlib import Path
from extractor.factory import ExtractorFactory
from extractor.data_structures import ExtractionStatus, ConfidenceSource
from extractor.base_extractor import EncryptedDocumentError, CorruptedDocumentError
import logging

# Disable debug logging for tests
logging.getLogger("extractor").setLevel(logging.WARNING)


class TestExtractorFactory:
    """Tests for ExtractorFactory."""

    def test_init(self):
        """Test factory initialization."""
        factory = ExtractorFactory()
        assert factory is not None
        assert len(factory._extractors) == 4

    def test_get_extractor_pdf(self):
        """Test getting PDF extractor."""
        factory = ExtractorFactory()
        test_file = Path("/tmp/test.pdf")
        extractor = factory.get_extractor(test_file)
        assert extractor is not None
        assert extractor.__class__.__name__ == "PdfExtractor"

    def test_get_extractor_excel(self):
        """Test getting Excel extractor."""
        factory = ExtractorFactory()
        test_file = Path("/tmp/test.xlsx")
        extractor = factory.get_extractor(test_file)
        assert extractor is not None
        assert extractor.__class__.__name__ == "ExcelExtractor"

    def test_get_extractor_word(self):
        """Test getting Word extractor."""
        factory = ExtractorFactory()
        test_file = Path("/tmp/test.docx")
        extractor = factory.get_extractor(test_file)
        assert extractor is not None
        assert extractor.__class__.__name__ == "WordExtractor"

    def test_get_extractor_image(self):
        """Test getting image extractor."""
        factory = ExtractorFactory()
        test_file = Path("/tmp/test.jpg")
        extractor = factory.get_extractor(test_file)
        assert extractor is not None
        assert extractor.__class__.__name__ == "ImageExtractor"

    def test_get_extractor_unsupported(self):
        """Test getting extractor for unsupported format."""
        factory = ExtractorFactory()
        test_file = Path("/tmp/test.xyz")
        extractor = factory.get_extractor(test_file)
        assert extractor is None


class TestExtractedField:
    """Tests for ExtractedField."""

    def test_init(self):
        """Test ExtractedField initialization."""
        from extractor.data_structures import ExtractedField

        field = ExtractedField(value="INV-123", confidence=0.98, source=ConfidenceSource.REGEX)
        assert field.value == "INV-123"
        assert field.confidence == 0.98
        assert field.source == ConfidenceSource.REGEX

    def test_confidence_validation(self):
        """Test confidence validation."""
        from extractor.data_structures import ExtractedField

        with pytest.raises(ValueError):
            ExtractedField(value="test", confidence=1.5, source=ConfidenceSource.REGEX)

        with pytest.raises(ValueError):
            ExtractedField(value="test", confidence=-0.1, source=ConfidenceSource.REGEX)


class TestBaseExtractor:
    """Tests for BaseExtractor."""

    def test_extract_common_metadata(self):
        """Test common metadata extraction."""
        # Skipped - internal method, covered by integration tests
        pytest.skip("Internal method test skipped")


class TestPdfExtractor:
    """Tests for PDF extractor."""

    def test_can_extract_pdf(self):
        """Test PDF extractor can extract PDF files."""
        from extractor.pdf_extractor import PdfExtractor

        extractor = PdfExtractor()
        assert extractor.can_extract(Path("/tmp/test.pdf"))
        assert not extractor.can_extract(Path("/tmp/test.txt"))

    def test_extract_nonexistent_file(self):
        """Test extracting nonexistent file."""
        from extractor.pdf_extractor import PdfExtractor

        extractor = PdfExtractor()
        result = extractor.extract(Path("/tmp/nonexistent.pdf"))

        assert result.status == ExtractionStatus.FAILED
        assert len(result.errors) > 0


class TestExcelExtractor:
    """Tests for Excel extractor."""

    def test_can_extract_excel(self):
        """Test Excel extractor can extract Excel files."""
        from extractor.excel_extractor import ExcelExtractor

        extractor = ExcelExtractor()
        assert extractor.can_extract(Path("/tmp/test.xlsx"))
        assert extractor.can_extract(Path("/tmp/test.xls"))
        assert not extractor.can_extract(Path("/tmp/test.txt"))


class TestWordExtractor:
    """Tests for Word extractor."""

    def test_can_extract_word(self):
        """Test Word extractor can extract Word files."""
        from extractor.word_extractor import WordExtractor

        extractor = WordExtractor()
        assert extractor.can_extract(Path("/tmp/test.docx"))
        assert not extractor.can_extract(Path("/tmp/test.txt"))


class TestImageExtractor:
    """Tests for image extractor."""

    def test_can_extract_image(self):
        """Test image extractor can extract image files."""
        from extractor.image_extractor import ImageExtractor

        extractor = ImageExtractor()
        assert extractor.can_extract(Path("/tmp/test.jpg"))
        assert extractor.can_extract(Path("/tmp/test.png"))
        assert not extractor.can_extract(Path("/tmp/test.txt"))
