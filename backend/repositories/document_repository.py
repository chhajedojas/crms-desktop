"""
Document repository implementation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from repositories.base import BaseRepository
from repositories.interfaces import DocumentRepositoryInterface
from database.models import Document as DocumentModel
from database.mappers import DocumentMapper
from domain import Document
from database.exceptions import EntityNotFoundError, InvalidEntityError
from core import get_logger


class DocumentRepository(BaseRepository[Document, DocumentModel], DocumentRepositoryInterface):
    """Repository for Document entity."""

    def __init__(self, session: Session):
        """Initialize Document repository with session, model, and mapper."""
        super().__init__(session, DocumentModel, DocumentMapper)
        self.logger = get_logger(__name__)

    def get_by_file_path(self, file_path: str) -> Optional[Document]:
        """
        Get document by file path.

        Args:
            file_path: File path

        Returns:
            Document domain entity if found, None otherwise
        """
        try:
            self.logger.debug(f"Getting document by file path: {file_path}")
            stmt = select(DocumentModel).where(DocumentModel.file_path == file_path)
            orm_entity = self.session.execute(stmt).scalar_one_or_none()
            if orm_entity:
                return self.mapper.to_domain(orm_entity)
            return None
        except Exception as e:
            self.logger.error(f"Error getting document by file path: {str(e)}", exc_info=True)
            raise

    def get_by_file_hash(self, file_hash: str) -> List[Document]:
        """
        Get documents by file hash (for duplicate detection).

        Args:
            file_hash: File hash

        Returns:
            List of Document domain entities with matching hash
        """
        try:
            self.logger.debug(f"Getting documents by file hash: {file_hash}")
            stmt = select(DocumentModel).where(DocumentModel.file_hash == file_hash)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting documents by file hash: {str(e)}", exc_info=True)
            raise

    def get_by_financial_year(self, financial_year: str) -> List[Document]:
        """
        Get documents by financial year.

        Args:
            financial_year: Financial year (e.g., "2023-2024")

        Returns:
            List of Document domain entities for the financial year
        """
        try:
            self.logger.debug(f"Getting documents by financial year: {financial_year}")
            stmt = select(DocumentModel).where(DocumentModel.financial_year == financial_year)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting documents by financial year: {str(e)}", exc_info=True)
            raise

    def get_by_document_type(self, document_type: str) -> List[Document]:
        """
        Get documents by document type.

        Args:
            document_type: Document type (e.g., "Tax Invoice", "Bank Statement")

        Returns:
            List of Document domain entities of the specified type
        """
        try:
            self.logger.debug(f"Getting documents by type: {document_type}")
            stmt = select(DocumentModel).where(DocumentModel.document_type == document_type)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting documents by type: {str(e)}", exc_info=True)
            raise

    def get_duplicates(self) -> List[Document]:
        """
        Get all duplicate documents.

        Returns:
            List of Document domain entities that are duplicates
        """
        try:
            self.logger.debug("Getting duplicate documents")
            stmt = select(DocumentModel).where(DocumentModel.is_duplicate == True)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting duplicate documents: {str(e)}", exc_info=True)
            raise

    def search_by_name(self, name_pattern: str) -> List[Document]:
        """
        Search documents by file name pattern.

        Args:
            name_pattern: File name pattern (SQL LIKE pattern)

        Returns:
            List of Document domain entities matching the pattern
        """
        try:
            self.logger.debug(f"Searching documents by name pattern: {name_pattern}")
            stmt = select(DocumentModel).where(DocumentModel.file_name.like(name_pattern))
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error searching documents by name: {str(e)}", exc_info=True)
            raise

    def get_unprocessed(self) -> List[Document]:
        """
        Get documents that haven't been processed yet.

        Returns:
            List of Document domain entities that are unprocessed
        """
        try:
            self.logger.debug("Getting unprocessed documents")
            stmt = select(DocumentModel).where(
                and_(
                    DocumentModel.content_extracted == False,
                    DocumentModel.ocr_processed == False,
                )
            )
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting unprocessed documents: {str(e)}", exc_info=True)
            raise
