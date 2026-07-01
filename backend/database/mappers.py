"""
Mappers for converting between ORM models and domain entities.

This module provides the anti-corruption layer that separates the persistence
layer (SQLAlchemy ORM models) from the domain layer (pure Python entities).
This ensures the domain layer has no knowledge of infrastructure details.
"""

from typing import Optional, List
from datetime import datetime
from database.models import (
    Document as DocumentModel,
    Metadata as MetadataModel,
    Relationship as RelationshipModel,
    AuditLog as AuditLogModel,
    VersionLog as VersionLogModel,
)
from domain import Document, Metadata, Relationship, AuditLog, VersionLog, DocumentStatus, RelationshipType, ChangeType


class DocumentMapper:
    """Mapper for Document entity."""

    @staticmethod
    def to_domain(model: DocumentModel) -> Document:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy Document model

        Returns:
            Document domain entity
        """
        return Document(
            id=model.id,
            file_path=model.file_path,
            original_path=model.original_path,
            file_name=model.file_name,
            file_size=model.file_size,
            file_hash=model.file_hash,
            file_type=model.file_type,
            mime_type=model.mime_type,
            created_date=model.created_date,
            modified_date=model.modified_date,
            indexed_date=model.indexed_date,
            is_duplicate=model.is_duplicate,
            duplicate_of_id=model.duplicate_of_id,
            reorganized_path=model.reorganized_path,
            financial_year=model.financial_year,
            document_type=model.document_type,
            status=DocumentStatus(model.status) if model.status else DocumentStatus.INDEXED,
            content_extracted=model.content_extracted,
            ocr_processed=model.ocr_processed,
        )

    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: Document domain entity

        Returns:
            SQLAlchemy Document model
        """
        return DocumentModel(
            id=entity.id,
            file_path=entity.file_path,
            original_path=entity.original_path,
            file_name=entity.file_name,
            file_size=entity.file_size,
            file_hash=entity.file_hash,
            file_type=entity.file_type,
            mime_type=entity.mime_type,
            created_date=entity.created_date,
            modified_date=entity.modified_date,
            indexed_date=entity.indexed_date,
            is_duplicate=entity.is_duplicate,
            duplicate_of_id=entity.duplicate_of_id,
            reorganized_path=entity.reorganized_path,
            financial_year=entity.financial_year,
            document_type=entity.document_type,
            status=entity.status.value if isinstance(entity.status, DocumentStatus) else entity.status,
            content_extracted=entity.content_extracted,
            ocr_processed=entity.ocr_processed,
        )

    @staticmethod
    def to_domain_list(models: List[DocumentModel]) -> List[Document]:
        """
        Convert list of ORM models to domain entities.

        Args:
            models: List of SQLAlchemy Document models

        Returns:
            List of Document domain entities
        """
        return [DocumentMapper.to_domain(model) for model in models]


class MetadataMapper:
    """Mapper for Metadata entity."""

    @staticmethod
    def to_domain(model: MetadataModel) -> Metadata:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy Metadata model

        Returns:
            Metadata domain entity
        """
        return Metadata(
            id=model.id,
            document_id=model.document_id,
            key=model.key,
            value=model.value,
            confidence=model.confidence,
            extraction_method=model.extraction_method,
            needs_review=model.needs_review,
            created_date=model.created_date,
            updated_date=model.updated_date,
        )

    @staticmethod
    def to_model(entity: Metadata) -> MetadataModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: Metadata domain entity

        Returns:
            SQLAlchemy Metadata model
        """
        return MetadataModel(
            id=entity.id,
            document_id=entity.document_id,
            key=entity.key,
            value=entity.value,
            confidence=entity.confidence,
            extraction_method=entity.extraction_method,
            needs_review=entity.needs_review,
            created_date=entity.created_date,
            updated_date=entity.updated_date,
        )

    @staticmethod
    def to_domain_list(models: List[MetadataModel]) -> List[Metadata]:
        """
        Convert list of ORM models to domain entities.

        Args:
            models: List of SQLAlchemy Metadata models

        Returns:
            List of Metadata domain entities
        """
        return [MetadataMapper.to_domain(model) for model in models]


class RelationshipMapper:
    """Mapper for Relationship entity."""

    @staticmethod
    def to_domain(model: RelationshipModel) -> Relationship:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy Relationship model

        Returns:
            Relationship domain entity
        """
        return Relationship(
            id=model.id,
            source_document_id=model.source_document_id,
            target_document_id=model.target_document_id,
            relationship_type=RelationshipType(model.relationship_type) if model.relationship_type else RelationshipType.REFERENCE,
            confidence=model.confidence,
            created_date=model.created_date,
        )

    @staticmethod
    def to_model(entity: Relationship) -> RelationshipModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: Relationship domain entity

        Returns:
            SQLAlchemy Relationship model
        """
        return RelationshipModel(
            id=entity.id,
            source_document_id=entity.source_document_id,
            target_document_id=entity.target_document_id,
            relationship_type=entity.relationship_type.value if isinstance(entity.relationship_type, RelationshipType) else entity.relationship_type,
            confidence=entity.confidence,
            created_date=entity.created_date,
        )

    @staticmethod
    def to_domain_list(models: List[RelationshipModel]) -> List[Relationship]:
        """
        Convert list of ORM models to domain entities.

        Args:
            models: List of SQLAlchemy Relationship models

        Returns:
            List of Relationship domain entities
        """
        return [RelationshipMapper.to_domain(model) for model in models]


class AuditLogMapper:
    """Mapper for AuditLog entity."""

    @staticmethod
    def to_domain(model: AuditLogModel) -> AuditLog:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy AuditLog model

        Returns:
            AuditLog domain entity
        """
        return AuditLog(
            id=model.id,
            timestamp=model.timestamp,
            user_id=model.user_id,
            action=model.action,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            details=model.details,
            ip_address=model.ip_address,
        )

    @staticmethod
    def to_model(entity: AuditLog) -> AuditLogModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: AuditLog domain entity

        Returns:
            SQLAlchemy AuditLog model
        """
        return AuditLogModel(
            id=entity.id,
            timestamp=entity.timestamp,
            user_id=entity.user_id,
            action=entity.action,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            details=entity.details,
            ip_address=entity.ip_address,
        )

    @staticmethod
    def to_domain_list(models: List[AuditLogModel]) -> List[AuditLog]:
        """
        Convert list of ORM models to domain entities.

        Args:
            models: List of SQLAlchemy AuditLog models

        Returns:
            List of AuditLog domain entities
        """
        return [AuditLogMapper.to_domain(model) for model in models]


class VersionLogMapper:
    """Mapper for VersionLog entity."""

    @staticmethod
    def to_domain(model: VersionLogModel) -> VersionLog:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy VersionLog model

        Returns:
            VersionLog domain entity
        """
        return VersionLog(
            id=model.id,
            document_id=model.document_id,
            version_number=model.version_number,
            file_hash=model.file_hash,
            file_size=model.file_size,
            modified_date=model.modified_date,
            change_type=ChangeType(model.change_type) if model.change_type else ChangeType.NEW,
            previous_version_id=model.previous_version_id,
            created_date=model.created_date,
        )

    @staticmethod
    def to_model(entity: VersionLog) -> VersionLogModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: VersionLog domain entity

        Returns:
            SQLAlchemy VersionLog model
        """
        return VersionLogModel(
            id=entity.id,
            document_id=entity.document_id,
            version_number=entity.version_number,
            file_hash=entity.file_hash,
            file_size=entity.file_size,
            modified_date=entity.modified_date,
            change_type=entity.change_type.value if isinstance(entity.change_type, ChangeType) else entity.change_type,
            previous_version_id=entity.previous_version_id,
            created_date=entity.created_date,
        )

    @staticmethod
    def to_domain_list(models: List[VersionLogModel]) -> List[VersionLog]:
        """
        Convert list of ORM models to domain entities.

        Args:
            models: List of SQLAlchemy VersionLog models

        Returns:
            List of VersionLog domain entities
        """
        return [VersionLogMapper.to_domain(model) for model in models]
