-- Company Records Management System (CRMS)
-- SQLite Database Schema
-- Version: 1.0

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- =====================================================
-- Core Tables
-- =====================================================

-- Documents table: Stores information about all indexed documents
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    original_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash TEXT NOT NULL,
    file_type TEXT NOT NULL,
    mime_type TEXT,
    created_date TIMESTAMP,
    modified_date TIMESTAMP,
    indexed_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_duplicate BOOLEAN DEFAULT 0,
    duplicate_of_id INTEGER,
    reorganized_path TEXT,
    financial_year TEXT,
    document_type TEXT,
    status TEXT DEFAULT 'indexed',
    content_extracted BOOLEAN DEFAULT 0,
    ocr_processed BOOLEAN DEFAULT 0,
    FOREIGN KEY (duplicate_of_id) REFERENCES documents(id)
);

-- Indexes for documents table
CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);
CREATE INDEX IF NOT EXISTS idx_documents_financial_year ON documents(financial_year);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_is_duplicate ON documents(is_duplicate);

-- Metadata table: Stores extracted metadata for documents
CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    confidence REAL DEFAULT 1.0,
    extraction_method TEXT,
    needs_review BOOLEAN DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, key)
);

-- Indexes for metadata table
CREATE INDEX IF NOT EXISTS idx_metadata_document_id ON metadata(document_id);
CREATE INDEX IF NOT EXISTS idx_metadata_key ON metadata(key);
CREATE INDEX IF NOT EXISTS idx_metadata_value ON metadata(value);
CREATE INDEX IF NOT EXISTS idx_metadata_confidence ON metadata(confidence);
CREATE INDEX IF NOT EXISTS idx_metadata_needs_review ON metadata(needs_review);

-- =====================================================
-- Full-Text Search Tables
-- =====================================================

-- FTS5 virtual table for full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS fts_documents USING fts5(
    file_name,
    file_path,
    content,
    customer,
    vendor,
    invoice_number,
    gstin,
    document_type,
    content_rowid,
    tokenize='porter unicode61'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS fts_documents_insert AFTER INSERT ON documents BEGIN
    INSERT INTO fts_documents(
        rowid, file_name, file_path, content,
        customer, vendor, invoice_number, gstin, document_type, content_rowid
    ) VALUES (
        NEW.id, NEW.file_name, NEW.file_path, '',
        NULL, NULL, NULL, NULL, NEW.document_type, NEW.id
    );
END;

CREATE TRIGGER IF NOT EXISTS fts_documents_delete AFTER DELETE ON documents BEGIN
    DELETE FROM fts_documents WHERE rowid = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS fts_documents_update AFTER UPDATE ON documents BEGIN
    UPDATE fts_documents SET
        file_name = NEW.file_name,
        file_path = NEW.file_path,
        document_type = NEW.document_type
    WHERE rowid = NEW.id;
END;

-- =====================================================
-- Audit and Undo Tables
-- =====================================================

-- Audit log table: Tracks all system operations
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    details TEXT,
    ip_address TEXT,
    FOREIGN KEY (entity_id) REFERENCES documents(id)
);

-- Indexes for audit_log table
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_entity_type ON audit_log(entity_type);

-- Undo log table: Tracks operations that can be undone
CREATE TABLE IF NOT EXISTS undo_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operation_type TEXT NOT NULL,
    operation_data TEXT NOT NULL,
    rollback_data TEXT NOT NULL,
    is_executed BOOLEAN DEFAULT 1,
    can_undo BOOLEAN DEFAULT 1
);

-- Indexes for undo_log table
CREATE INDEX IF NOT EXISTS idx_undo_log_timestamp ON undo_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_undo_log_can_undo ON undo_log(can_undo);

-- =====================================================
-- Configuration Tables
-- =====================================================

-- Folder templates table: Stores folder structure templates
CREATE TABLE IF NOT EXISTS folder_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    structure_json TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classification rules table: Stores document classification rules
CREATE TABLE IF NOT EXISTS classification_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    document_type TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    pattern TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

-- Indexes for classification_rules table
CREATE INDEX IF NOT EXISTS idx_classification_rules_document_type ON classification_rules(document_type);
CREATE INDEX IF NOT EXISTS idx_classification_rules_is_active ON classification_rules(is_active);

-- Configuration table: Stores system configuration
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string',
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Version Tracking Tables
-- =====================================================

-- Version log table: Tracks document version history
CREATE TABLE IF NOT EXISTS version_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    file_hash TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    modified_date TIMESTAMP,
    change_type TEXT NOT NULL, -- 'new', 'modified', 'deleted'
    previous_version_id INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (previous_version_id) REFERENCES version_log(id)
);

-- Indexes for version_log table
CREATE INDEX IF NOT EXISTS idx_version_log_document_id ON version_log(document_id);
CREATE INDEX IF NOT EXISTS idx_version_log_file_hash ON version_log(file_hash);
CREATE INDEX IF NOT EXISTS idx_version_log_change_type ON version_log(change_type);

-- =====================================================
-- Relationship Tracking Tables
-- =====================================================

-- Relationships table: Tracks document relationships
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_document_id INTEGER NOT NULL,
    target_document_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL, -- 'invoice_to_payment', 'invoice_to_delivery', 'delivery_to_ledger', etc.
    confidence REAL DEFAULT 1.0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (target_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(source_document_id, target_document_id, relationship_type)
);

-- Indexes for relationships table
CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_document_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_document_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);

-- =====================================================
-- Validation Tables
-- =====================================================

-- GST validations table: Tracks GST validation results
CREATE TABLE IF NOT EXISTS gst_validations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    gstin TEXT NOT NULL,
    validation_type TEXT NOT NULL, -- 'format', 'checksum', 'rate', 'mismatch'
    is_valid BOOLEAN DEFAULT 0,
    error_message TEXT,
    reference_gstin TEXT, -- For mismatch validation
    reference_document_id INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (reference_document_id) REFERENCES documents(id)
);

-- Indexes for gst_validations table
CREATE INDEX IF NOT EXISTS idx_gst_validations_document_id ON gst_validations(document_id);
CREATE INDEX IF NOT EXISTS idx_gst_validations_gstin ON gst_validations(gstin);
CREATE INDEX IF NOT EXISTS idx_gst_validations_type ON gst_validations(validation_type);
CREATE INDEX IF NOT EXISTS idx_gst_validations_is_valid ON gst_validations(is_valid);

-- Sequences table: Tracks sequence detection results
CREATE TABLE IF NOT EXISTS sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    sequence_type TEXT NOT NULL, -- 'invoice_number', 'challan_number', etc.
    sequence_value TEXT NOT NULL,
    expected_value TEXT,
    is_missing BOOLEAN DEFAULT 0,
    gap_start TEXT,
    gap_end TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Indexes for sequences table
CREATE INDEX IF NOT EXISTS idx_sequences_document_id ON sequences(document_id);
CREATE INDEX IF NOT EXISTS idx_sequences_type ON sequences(sequence_type);
CREATE INDEX IF NOT EXISTS idx_sequences_value ON sequences(sequence_value);
CREATE INDEX IF NOT EXISTS idx_sequences_is_missing ON sequences(is_missing);

-- =====================================================
-- Reports Tables
-- =====================================================

-- Reports table: Stores generated report information
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    report_name TEXT NOT NULL,
    file_path TEXT,
    generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parameters TEXT,
    status TEXT DEFAULT 'completed',
    file_size INTEGER
);

-- Indexes for reports table
CREATE INDEX IF NOT EXISTS idx_reports_report_type ON reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_generation_date ON reports(generation_date);

-- =====================================================
-- Default Data
-- =====================================================

-- Default folder template
INSERT OR IGNORE INTO folder_templates (name, description, structure_json, is_default) VALUES
('Standard Business', 'Standard folder structure for business documents', json_object(
    'structure', json_array(
        json_object('name', 'Financial Year', 'type', 'dynamic', 'key', 'financial_year'),
        json_object('name', 'Document Type', 'type', 'dynamic', 'key', 'document_type'),
        json_object('name', 'Customer/Vendor', 'type', 'dynamic', 'key', 'customer_vendor')
    )
), 1);

-- Default classification rules
INSERT OR IGNORE INTO classification_rules (name, document_type, rule_type, pattern, priority) VALUES
('Tax Invoice Pattern', 'Tax Invoice', 'filename', '(?i)^.*invoice.*$', 10),
('Purchase Bill Pattern', 'Purchase Bill', 'filename', '(?i)^.*purchase.*bill.*$', 10),
('Debit Note Pattern', 'Debit Note', 'filename', '(?i)^.*debit.*note.*$', 10),
('Credit Note Pattern', 'Credit Note', 'filename', '(?i)^.*credit.*note.*$', 10),
('Delivery Challan Pattern', 'Delivery Challan', 'filename', '(?i)^.*delivery.*challan.*$', 10),
('GST Return Pattern', 'GST Return', 'filename', '(?i)^.*gst.*return.*$', 10),
('Bank Statement Pattern', 'Bank Statement', 'filename', '(?i)^.*bank.*statement.*$', 10),
('Salary Slip Pattern', 'Salary Slip', 'filename', '(?i)^.*salary.*slip.*$', 10),
('Audit File Pattern', 'Audit File', 'filename', '(?i)^.*audit.*$', 10),
('Legal Document Pattern', 'Legal Document', 'filename', '(?i)^.*legal.*$', 10),
('Busy Backup Pattern', 'Busy Backup', 'filename', '(?i)^.*busy.*backup.*$', 10);

-- Default configuration
INSERT OR IGNORE INTO config (key, value, value_type) VALUES
('ocr_enabled', 'true', 'boolean'),
('ocr_language', 'eng', 'string'),
('financial_year_start', '04-01', 'string'),
('duplicate_detection_enabled', 'true', 'boolean'),
('auto_classify_enabled', 'true', 'boolean'),
('max_file_size_mb', '100', 'integer'),
('supported_file_types', 'pdf,xlsx,xls,docx,doc,jpg,jpeg,png,tiff,bmp', 'string');

-- =====================================================
-- Views
-- =====================================================

-- View for document statistics
CREATE VIEW IF NOT EXISTS v_document_stats AS
SELECT
    COUNT(*) as total_documents,
    COUNT(CASE WHEN is_duplicate = 1 THEN 1 END) as duplicate_documents,
    COUNT(DISTINCT file_type) as unique_file_types,
    SUM(file_size) as total_size,
    AVG(file_size) as average_size,
    MIN(indexed_date) as first_indexed,
    MAX(indexed_date) as last_indexed
FROM documents;

-- View for documents with metadata
CREATE VIEW IF NOT EXISTS v_documents_with_metadata AS
SELECT
    d.*,
    GROUP_CONCAT(m.key || '=' || m.value, ', ') as metadata_summary
FROM documents d
LEFT JOIN metadata m ON d.id = m.document_id
GROUP BY d.id;

-- View for duplicate groups
CREATE VIEW IF NOT EXISTS v_duplicate_groups AS
SELECT
    file_hash,
    COUNT(*) as duplicate_count,
    GROUP_CONCAT(id) as document_ids,
    GROUP_CONCAT(file_path) as file_paths,
    MIN(id) as original_id
FROM documents
WHERE is_duplicate = 1 OR duplicate_of_id IS NOT NULL
GROUP BY file_hash
HAVING COUNT(*) > 1;

-- View for financial year distribution
CREATE VIEW IF NOT EXISTS v_financial_year_distribution AS
SELECT
    financial_year,
    document_type,
    COUNT(*) as document_count,
    SUM(file_size) as total_size
FROM documents
WHERE financial_year IS NOT NULL
GROUP BY financial_year, document_type
ORDER BY financial_year DESC, document_count DESC;

-- =====================================================
-- Performance Optimization
-- =====================================================

-- Analyze tables for query optimization
ANALYZE;

-- Vacuum to optimize database
VACUUM;
