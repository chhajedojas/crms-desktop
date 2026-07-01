"""
SQLAlchemy ORM models for CRMS database.

This module contains SQLAlchemy ORM models that map to the database schema.
These are separate from the domain entities to maintain clean separation
between domain and persistence layers.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from core import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Document(Base):
    """Document ORM model."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False, unique=True)
    original_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    created_date = Column(DateTime, nullable=True)
    modified_date = Column(DateTime, nullable=True)
    indexed_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_duplicate = Column(Boolean, nullable=False, default=False)
    duplicate_of_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    reorganized_path = Column(String, nullable=True)
    financial_year = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    status = Column(String, nullable=False, default="indexed")
    content_extracted = Column(Boolean, nullable=False, default=False)
    ocr_processed = Column(Boolean, nullable=False, default=False)

    # Relationships
    duplicate_of = relationship("Document", remote_side=[id], backref="duplicates")
    metadata_items = relationship("Metadata", back_populates="document", cascade="all, delete-orphan")
    version_logs = relationship("VersionLog", back_populates="document", cascade="all, delete-orphan")
    source_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.source_document_id",
        back_populates="source_document",
        cascade="all, delete-orphan",
    )
    target_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.target_document_id",
        back_populates="target_document",
        cascade="all, delete-orphan",
    )
    gst_validations = relationship("GSTValidation", back_populates="document", cascade="all, delete-orphan")
    sequences = relationship("Sequence", back_populates="document", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_documents_file_hash", "file_hash"),
        Index("idx_documents_file_type", "file_type"),
        Index("idx_documents_financial_year", "financial_year"),
        Index("idx_documents_document_type", "document_type"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_is_duplicate", "is_duplicate"),
    )


class Metadata(Base):
    """Metadata ORM model."""
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)
    extraction_method = Column(String, nullable=True)
    needs_review = Column(Boolean, nullable=False, default=False)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="metadata_items")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_metadata_document_id", "document_id"),
        Index("idx_metadata_key", "key"),
        Index("idx_metadata_value", "value"),
        Index("idx_metadata_confidence", "confidence"),
        Index("idx_metadata_needs_review", "needs_review"),
        UniqueConstraint("document_id", "key", name="uq_document_key"),
    )


class Relationship(Base):
    """Relationship ORM model."""
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    target_document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    source_document = relationship("Document", foreign_keys=[source_document_id], back_populates="source_relationships")
    target_document = relationship("Document", foreign_keys=[target_document_id], back_populates="target_relationships")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_relationships_source", "source_document_id"),
        Index("idx_relationships_target", "target_document_id"),
        Index("idx_relationships_type", "relationship_type"),
        UniqueConstraint("source_document_id", "target_document_id", "relationship_type", name="uq_source_target_type"),
    )


class AuditLog(Base):
    """Audit log ORM model."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_audit_log_timestamp", "timestamp"),
        Index("idx_audit_log_action", "action"),
        Index("idx_audit_log_entity_type", "entity_type"),
    )


class VersionLog(Base):
    """Version log ORM model."""
    __tablename__ = "version_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_hash = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    modified_date = Column(DateTime, nullable=True)
    change_type = Column(String, nullable=False)
    previous_version_id = Column(Integer, ForeignKey("version_log.id"), nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="version_logs")
    previous_version = relationship("VersionLog", remote_side=[id], backref="next_versions")

    # Indexes
    __table_args__ = (
        Index("idx_version_log_document_id", "document_id"),
        Index("idx_version_log_file_hash", "file_hash"),
        Index("idx_version_log_change_type", "change_type"),
    )


class GSTValidation(Base):
    """GST validation ORM model."""
    __tablename__ = "gst_validations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    gstin = Column(String, nullable=False)
    validation_type = Column(String, nullable=False)
    is_valid = Column(Boolean, nullable=False, default=False)
    error_message = Column(Text, nullable=True)
    reference_gstin = Column(String, nullable=True)
    reference_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="gst_validations")

    # Indexes
    __table_args__ = (
        Index("idx_gst_validations_document_id", "document_id"),
        Index("idx_gst_validations_gstin", "gstin"),
        Index("idx_gst_validations_type", "validation_type"),
        Index("idx_gst_validations_is_valid", "is_valid"),
    )


class Sequence(Base):
    """Sequence detection ORM model."""
    __tablename__ = "sequences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    sequence_type = Column(String, nullable=False)
    sequence_value = Column(String, nullable=False)
    expected_value = Column(String, nullable=True)
    is_missing = Column(Boolean, nullable=False, default=False)
    gap_start = Column(String, nullable=True)
    gap_end = Column(String, nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="sequences")

    # Indexes
    __table_args__ = (
        Index("idx_sequences_document_id", "document_id"),
        Index("idx_sequences_type", "sequence_type"),
        Index("idx_sequences_value", "sequence_value"),
        Index("idx_sequences_is_missing", "is_missing"),
    )
