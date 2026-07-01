"""
Version log repository implementation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from repositories.base import BaseRepository
from repositories.interfaces import VersionLogRepositoryInterface
from database.models import VersionLog as VersionLogModel
from database.mappers import VersionLogMapper
from core import get_logger
from domain import VersionLog


class VersionLogRepository(BaseRepository[VersionLog, VersionLogModel], VersionLogRepositoryInterface):
    """Repository for Version Log entity."""

    def __init__(self, session: Session):
        """Initialize Version Log repository with session, model, and mapper."""
        super().__init__(session, VersionLogModel, VersionLogMapper)
        self.logger = get_logger(__name__)

    def get_by_document_id(self, document_id: int) -> List[VersionLog]:
        """
        Get all version logs for a document.

        Args:
            document_id: Document ID

        Returns:
            List of VersionLog domain entities for the document
        """
        try:
            self.logger.debug(f"Getting version logs for document: {document_id}")
            stmt = select(VersionLogModel).where(VersionLogModel.document_id == document_id)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting version logs for document: {str(e)}", exc_info=True)
            raise
