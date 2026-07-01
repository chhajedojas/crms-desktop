"""
Metadata repository implementation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from repositories.base import BaseRepository
from repositories.interfaces import MetadataRepositoryInterface
from database.models import Metadata as MetadataModel
from database.mappers import MetadataMapper
from domain import Metadata
from core import get_logger


class MetadataRepository(BaseRepository[Metadata, MetadataModel], MetadataRepositoryInterface):
    """Repository for Metadata entity."""

    def __init__(self, session: Session):
        """Initialize Metadata repository with session, model, and mapper."""
        super().__init__(session, MetadataModel, MetadataMapper)
        self.logger = get_logger(__name__)

    def get_by_document_id(self, document_id: int) -> List[Metadata]:
        """
        Get all metadata for a document.

        Args:
            document_id: Document ID

        Returns:
            List of Metadata domain entities for the document
        """
        try:
            self.logger.debug(f"Getting metadata for document: {document_id}")
            stmt = select(MetadataModel).where(MetadataModel.document_id == document_id)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting metadata for document: {str(e)}", exc_info=True)
            raise

    def get_by_key(self, document_id: int, key: str) -> Optional[Metadata]:
        """
        Get metadata by document ID and key.

        Args:
            document_id: Document ID
            key: Metadata key

        Returns:
            Metadata domain entity if found, None otherwise
        """
        try:
            self.logger.debug(f"Getting metadata for document {document_id} with key: {key}")
            stmt = select(MetadataModel).where(
                and_(
                    MetadataModel.document_id == document_id,
                    MetadataModel.key == key,
                )
            )
            orm_entity = self.session.execute(stmt).scalar_one_or_none()
            if orm_entity:
                return self.mapper.to_domain(orm_entity)
            return None
        except Exception as e:
            self.logger.error(f"Error getting metadata by key: {str(e)}", exc_info=True)
            raise

    def get_needs_review(self) -> List[Metadata]:
        """
        Get all metadata that needs review.

        Returns:
            List of Metadata domain entities needing review
        """
        try:
            self.logger.debug("Getting metadata needing review")
            stmt = select(MetadataModel).where(MetadataModel.needs_review == True)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting metadata needing review: {str(e)}", exc_info=True)
            raise

    def get_low_confidence(self, threshold: float = 0.7) -> List[Metadata]:
        """
        Get metadata with confidence below threshold.

        Args:
            threshold: Confidence threshold (default 0.7)

        Returns:
            List of Metadata domain entities with low confidence
        """
        try:
            self.logger.debug(f"Getting metadata with confidence below {threshold}")
            stmt = select(MetadataModel).where(MetadataModel.confidence < threshold)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting low-confidence metadata: {str(e)}", exc_info=True)
            raise

    def delete_by_document_id(self, document_id: int) -> int:
        """
        Delete all metadata for a document.

        Args:
            document_id: Document ID

        Returns:
            Number of deleted metadata items
        """
        try:
            self.logger.debug(f"Deleting metadata for document: {document_id}")
            from sqlalchemy import delete

            stmt = delete(MetadataModel).where(MetadataModel.document_id == document_id)
            result = self.session.execute(stmt)
            return result.rowcount
        except Exception as e:
            self.logger.error(f"Error deleting metadata for document: {str(e)}", exc_info=True)
            raise
