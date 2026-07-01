"""
Image metadata extractor.

Extracts metadata from images using Pillow.
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
    from PIL import Image

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class ImageExtractor(BaseExtractor):
    """Extractor for image files."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

    def __init__(self):
        """Initialize image extractor."""
        super().__init__()
        if not PILLOW_AVAILABLE:
            self.logger.warning("Pillow not available, image extraction disabled")

    def can_extract(self, file_path: Path) -> bool:
        """Check if file is an image."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract metadata from image."""
        if not PILLOW_AVAILABLE:
            return ExtractionResult(
                status=ExtractionStatus.UNSUPPORTED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=["Pillow not available"],
            )

        start_time = datetime.now(timezone.utc)
        errors = []
        warnings = []

        try:
            # Open image
            with Image.open(file_path) as img:
                # Extract common metadata
                common_metadata = self._extract_image_common_metadata(file_path, img)

                # Extract EXIF data
                exif_data = self._extract_exif(img)

                # Images don't have business metadata
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
            self.logger.error(f"Error extracting image metadata: {str(e)}")
            return ExtractionResult(
                status=ExtractionStatus.FAILED,
                common_metadata=self._extract_common_metadata(file_path),
                business_metadata=BusinessMetadata(),
                errors=[str(e)],
                extraction_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )

    def _extract_image_common_metadata(self, file_path: Path, img) -> CommonMetadata:
        """Extract common metadata from image."""
        stat = file_path.stat()

        return CommonMetadata(
            filename=file_path.name,
            extension=file_path.suffix.lower(),
            file_size=stat.st_size,
            creation_date=None,  # Will be extracted from EXIF if available
            modification_date=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            page_count=None,  # Images don't have pages
            mime_type=f"image/{file_path.suffix.lower()[1:]}",
        )

    def _extract_exif(self, img) -> dict:
        """Extract EXIF data from image."""
        exif_data = {}
        try:
            exif_dict = img.getexif()
            if exif_dict:
                from PIL import ExifTags

                for tag, value in exif_dict.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    exif_data[decoded] = value
        except Exception as e:
            self.logger.warning(f"Error extracting EXIF: {str(e)}")
        return exif_data
