# Company Records Management System (CRMS) - Software Architecture

## 1. System Overview

### 1.1 Purpose
Production-quality offline desktop application for intelligent document management, specifically designed for Indian business documents (tax invoices, GST returns, legal documents, etc.).

### 1.2 Core Principles
- **Offline-First**: All functionality works without internet connectivity
- **Non-Destructive**: Original files are never modified
- **Undo-Capable**: All reorganization operations can be reverted
- **Modular**: Clean separation of concerns with well-defined interfaces
- **Testable**: Comprehensive unit tests for all components
- **Maintainable**: Clean code, clear documentation, sensible defaults
- **Extensible**: Easy to add new document types, extractors, and features

### 1.3 Technology Stack

#### Backend
- **Language**: Python 3.11+
- **IPC Framework**: PyBridge (direct Electron-Python communication via stdio/sockets)
- **Operational Database**: SQLite 3.40+ with FTS5 extension
- **Analytics Database**: DuckDB for complex analytics and reporting
- **Job Queue**: Celery with Redis backend (for processing pipeline)
- **OCR**: Tesseract OCR engine
- **Document Processing**:
  - PyPDF2, pdfplumber (PDF)
  - openpyxl, pandas (Excel)
  - python-docx (Word)
  - Pillow (Images)
- **Excel Generation**: openpyxl, xlsxwriter
- **Hash Calculation**: hashlib (SHA-256)
- **Classification**: scikit-learn (ML classifier)
- **Plugin System**: pluggy for extensible document extractors
- **Logging**: Python logging module with rotation

#### Frontend
- **Framework**: React 18+ with TypeScript
- **Desktop Shell**: Electron 28+
- **UI Library**: Material-UI (MUI) v5+
- **State Management**: Redux Toolkit + RTK Query
- **Build Tool**: Vite
- **IPC Communication**: electron-builder IPC

#### Packaging
- **Packager**: Electron Builder
- **Target**: macOS (DMG), Windows (NSIS/EXE)
- **Updater**: electron-updater (for future automatic updates)

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Desktop App                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   React UI  │  │   Redux     │  │  PyBridge    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Direct IPC (stdio/sockets)
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Python Backend Service                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   IPC       │  │  Business   │  │   Plugin    │          │
│  │   Handler   │  │   Logic     │  │   Manager   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Processing Pipeline                     │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Scan → Hash → Extract → OCR → Classify → Index       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Core Modules                            │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • JobQueueManager   • DocumentScanner               │   │
│  │ • MetadataExtractor • DocumentClassifier           │   │
│  │ • VersionManager    • DuplicateDetector             │   │
│  │ • RelationshipGraph • GSTValidator                   │   │
│  │ • BankReconciler    • SequenceDetector              │   │
│  │ • FolderStructure   • ReorganizationEngine          │   │
│  │ • SearchEngine      • AuditLogger                   │   │
│  │ • ReportGenerator   • UndoManager                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
┌─────────────────────────────┐   ┌─────────────────────────────┐
│    SQLite (Operational)     │   │      DuckDB (Analytics)     │
├─────────────────────────────┤   ├─────────────────────────────┤
│ • documents table          │   │ • Document analytics       │
│ • metadata table           │   │ • Customer timelines       │
│ • fts5 index               │   │ • Vendor timelines          │
│ • audit_log table          │   │ • GST analysis             │
│ • undo_log table           │   │ • Financial reports         │
│ • version_log table        │   │ • Relationship queries      │
│ • relationships table      │   └─────────────────────────────┘
│ • gst_validations table    │
│ • sequences table          │
└─────────────────────────────┘
```

### 2.2 Module Responsibilities

#### Backend Modules

1. **JobQueueManager**
   - Manage processing pipeline job queue
   - Handle job scheduling and prioritization
   - Retry failed jobs with exponential backoff
   - Job status tracking and reporting
   - Parallel job execution with worker pools

2. **DocumentScanner**
   - Scan directory tree recursively
   - Identify supported file types
   - Calculate file hashes (SHA-256)
   - Collect basic file metadata (size, dates, permissions)
   - Detect file changes (new, modified, deleted)

3. **VersionManager**
   - Track document version history
   - Detect file modifications via hash comparison
   - Only reprocess changed files
   - Maintain version log for audit trail
   - Support differential updates

4. **MetadataExtractor**
   - Extract text from PDFs (including OCR for scanned docs)
   - Parse Excel files
   - Parse Word documents
   - Extract metadata from images
   - Identify key fields with confidence scores:
     - Customer (confidence: 0.0-1.0)
     - Vendor (confidence: 0.0-1.0)
     - Invoice Number (confidence: 0.0-1.0)
     - GSTIN (confidence: 0.0-1.0)
     - Date (confidence: 0.0-1.0)
     - Amount (confidence: 0.0-1.0)

5. **DuplicateDetector**
   - Compare file hashes
   - Identify duplicate files
   - Detect duplicate invoice numbers across documents
   - Generate duplicate reports
   - Handle near-duplicates (similar filenames, sizes)

6. **DocumentClassifier**
   - Classify documents by type (Invoice, Bill, Debit Note, etc.)
   - Use rule-based + ML hybrid approach
   - Trainable classifier for custom document types
   - Confidence-based classification with manual review threshold

7. **RelationshipGraph**
   - Build document relationship graph
   - Link invoice ↔ delivery challan ↔ payment ↔ ledger
   - Track document dependencies
   - Support relationship queries and visualization
   - Detect orphaned documents

8. **GSTValidator**
   - Validate GSTIN format and checksum
   - Detect GST mismatches between invoice and purchase
   - Validate GST rates against tax rules
   - Generate GST validation reports
   - Track GST compliance issues

9. **BankReconciler**
   - Match bank statements with payments
   - Identify unmatched transactions
   - Generate reconciliation reports
   - Support manual reconciliation workflow
   - Track reconciliation status

10. **SequenceDetector**
    - Detect missing invoice sequences
    - Identify gaps in invoice numbering
    - Validate sequence continuity
    - Generate sequence reports
    - Support custom sequence patterns

11. **FolderStructure**
    - Analyze document distribution
    - Suggest professional folder structure
    - Configurable templates
    - Handle financial year grouping

12. **ReorganizationEngine**
    - Create reorganized copy of documents
    - Apply folder structure
    - Never modify original files
    - Generate migration plan
    - Support rollback to previous organization

13. **SearchEngine**
    - SQLite FTS5 full-text search
    - Search by multiple fields
    - Fast indexed queries
    - Support boolean operators
    - Fuzzy search capabilities

14. **AuditLogger**
    - Log all user actions
    - Track file operations
    - Maintain audit trail
    - Exportable logs
    - Tamper-evident logging

15. **ReportGenerator**
    - Generate Inventory.xlsx
    - Generate Duplicate_Report.xlsx
    - Generate Migration_Plan.xlsx
    - Generate GST_Validation_Report.xlsx
    - Generate Customer_Timeline.xlsx
    - Generate Vendor_Timeline.xlsx
    - Generate Bank_Reconciliation_Report.xlsx
    - Generate Missing_Sequence_Report.xlsx
    - Custom report templates

16. **UndoManager**
    - Track all reorganization operations
    - Maintain undo stack
    - Rollback to previous state
    - Support multiple undo levels
    - Undo point management

17. **PluginManager**
    - Load and manage document extractor plugins
    - Plugin discovery and registration
    - Plugin lifecycle management
    - Plugin configuration
    - Plugin marketplace support (future)

#### Frontend Modules

1. **MainWindow**
   - Application shell
   - Navigation
   - Status bar

2. **Dashboard**
   - Statistics overview
   - Recent activity
   - Quick actions
   - Charts and visualizations

3. **DocumentBrowser**
   - File tree view
   - Document preview
   - Bulk operations
   - Filter and sort

4. **SearchInterface**
   - Search input
   - Advanced filters
   - Results display
   - Export results

5. **ReorganizationWizard**
   - Step-by-step reorganization
   - Preview changes
   - Confirm and execute
   - Progress tracking

6. **ReportsView**
   - Report generation
   - Report preview
   - Export options
   - Report templates

7. **Settings**
   - Application configuration
   - Folder templates
   - Classification rules
   - OCR settings

## 3. Database Schema

### 3.1 Core Tables

#### documents
```sql
CREATE TABLE documents (
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
    FOREIGN KEY (duplicate_of_id) REFERENCES documents(id)
);

CREATE INDEX idx_documents_file_hash ON documents(file_hash);
CREATE INDEX idx_documents_file_type ON documents(file_type);
CREATE INDEX idx_documents_financial_year ON documents(financial_year);
CREATE INDEX idx_documents_document_type ON documents(document_type);
```

#### metadata
```sql
CREATE TABLE metadata (
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

CREATE INDEX idx_metadata_document_id ON metadata(document_id);
CREATE INDEX idx_metadata_key ON metadata(key);
CREATE INDEX idx_metadata_value ON metadata(value);
CREATE INDEX idx_metadata_confidence ON metadata(confidence);
CREATE INDEX idx_metadata_needs_review ON metadata(needs_review);
```

#### fts_documents (Full-Text Search)
```sql
CREATE VIRTUAL TABLE fts_documents USING fts5(
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

CREATE TRIGGER fts_documents_insert AFTER INSERT ON documents BEGIN
    INSERT INTO fts_documents(
        rowid, file_name, file_path, content, 
        customer, vendor, invoice_number, gstin, document_type, content_rowid
    ) VALUES (
        NEW.id, NEW.file_name, NEW.file_path, '',
        NULL, NULL, NULL, NULL, NEW.document_type, NEW.id
    );
END;
```

#### audit_log
```sql
CREATE TABLE audit_log (
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

CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_action ON audit_log(action);
```

#### undo_log
```sql
CREATE TABLE undo_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operation_type TEXT NOT NULL,
    operation_data TEXT NOT NULL,
    rollback_data TEXT NOT NULL,
    is_executed BOOLEAN DEFAULT 1,
    can_undo BOOLEAN DEFAULT 1
);

CREATE INDEX idx_undo_log_timestamp ON undo_log(timestamp);
```

#### folder_templates
```sql
CREATE TABLE folder_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    structure_json TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### classification_rules
```sql
CREATE TABLE classification_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    document_type TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    pattern TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);
```

#### config
```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string',
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### version_log
```sql
CREATE TABLE version_log (
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

CREATE INDEX idx_version_log_document_id ON version_log(document_id);
CREATE INDEX idx_version_log_file_hash ON version_log(file_hash);
CREATE INDEX idx_version_log_change_type ON version_log(change_type);
```

#### relationships
```sql
CREATE TABLE relationships (
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

CREATE INDEX idx_relationships_source ON relationships(source_document_id);
CREATE INDEX idx_relationships_target ON relationships(target_document_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
```

#### gst_validations
```sql
CREATE TABLE gst_validations (
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

CREATE INDEX idx_gst_validations_document_id ON gst_validations(document_id);
CREATE INDEX idx_gst_validations_gstin ON gst_validations(gstin);
CREATE INDEX idx_gst_validations_type ON gst_validations(validation_type);
CREATE INDEX idx_gst_validations_is_valid ON gst_validations(is_valid);
```

#### sequences
```sql
CREATE TABLE sequences (
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

CREATE INDEX idx_sequences_document_id ON sequences(document_id);
CREATE INDEX idx_sequences_type ON sequences(sequence_type);
CREATE INDEX idx_sequences_value ON sequences(sequence_value);
CREATE INDEX idx_sequences_is_missing ON sequences(is_missing);
```

## 4. IPC Communication Design

### 4.1 IPC Channels (Electron ↔ Python)

#### Document Management
- `documents:scan` - Scan directory for documents
- `documents:list` - List documents with pagination
- `documents:get` - Get document details
- `documents:getMetadata` - Get document metadata
- `documents:updateMetadata` - Update document metadata
- `documents:delete` - Remove document from index
- `documents:getVersion` - Get document version history
- `documents:rescan` - Rescan for changes (incremental)

#### Processing Pipeline
- `pipeline:start` - Start processing pipeline
- `pipeline:status` - Get pipeline status
- `pipeline:pause` - Pause processing
- `pipeline:resume` - Resume processing
- `pipeline:cancel` - Cancel processing
- `pipeline:retry` - Retry failed jobs

#### Search
- `search:query` - Full-text search
- `search:suggest` - Search suggestions
- `search:advanced` - Advanced search with filters

#### Reorganization
- `reorganization:analyze` - Analyze and suggest structure
- `reorganization:preview` - Preview reorganization
- `reorganization:execute` - Execute reorganization
- `reorganization:undo` - Undo last reorganization
- `reorganization:rollback` - Rollback to specific version

#### Reports
- `reports:generate` - Generate report (specify type)
- `reports:status` - Get report generation status
- `reports:download` - Download generated report
- `reports:list` - List available reports

#### Validation & Analysis
- `validation:gst` - Validate GST information
- `validation:sequences` - Check invoice sequences
- `validation:duplicates` - Check for duplicate invoice numbers
- `analysis:relationships` - Get document relationships
- `analysis:timeline` - Get customer/vendor timeline
- `analysis:reconciliation` - Bank reconciliation analysis

#### System
- `system:status` - System status
- `system:stats` - System statistics
- `system:auditLog` - Get audit log
- `system:config` - Get/set configuration
- `system:plugins` - Plugin management
- `system:version` - Get version information

### 4.2 Message Format

All IPC messages follow this structure:

**Request:**
```json
{
  "id": "unique-request-id",
  "channel": "channel-name",
  "payload": { /* channel-specific data */ },
  "timestamp": "ISO-8601-timestamp"
}
```

**Response:**
```json
{
  "id": "unique-request-id",
  "success": true/false,
  "data": { /* response data */ },
  "error": { /* error details if failed */ },
  "timestamp": "ISO-8601-timestamp"
}
```

**Progress Updates (for long-running operations):**
```json
{
  "id": "unique-request-id",
  "type": "progress",
  "data": {
    "current": 150,
    "total": 1000,
    "percentage": 15,
    "message": "Processing documents..."
  },
  "timestamp": "ISO-8601-timestamp"
}
```

## 5. Security Considerations

### 5.1 Data Security
- All file paths are validated and sanitized
- SQL injection prevention via parameterized queries
- Input validation on all API endpoints
- No external network calls (offline-first)

### 5.2 File System Safety
- Original files are never modified
- All operations work on copies
- Write operations are atomic where possible
- File permissions are preserved

### 5.3 Audit Trail
- All user actions are logged
- Administrative actions are tracked
- Logs are tamper-evident

## 6. Performance Considerations

### 6.1 Database Optimization
- Proper indexing on all frequently queried columns
- FTS5 for fast full-text search
- Connection pooling
- Prepared statements
- Periodic VACUUM and ANALYZE

### 6.2 File Processing
- Parallel processing for document scanning
- Batch operations for metadata extraction
- Lazy loading for large file sets
- Caching of frequently accessed data

### 6.3 Memory Management
- Stream processing for large files
- Efficient data structures
- Memory limits on OCR operations
- Garbage collection optimization

## 7. Error Handling

### 7.1 Error Categories
- File system errors (permissions, missing files)
- Database errors (corruption, constraints)
- Parsing errors (invalid file formats)
- OCR errors (unrecognized text)
- Reorganization errors (disk space, conflicts)

### 7.2 Error Recovery
- Graceful degradation
- Retry mechanisms for transient errors
- User-friendly error messages
- Detailed error logging
- Recovery suggestions

## 8. Testing Strategy

### 8.1 Unit Tests
- Each module tested in isolation
- Mock external dependencies
- Edge case coverage
- Boundary condition testing

### 8.2 Integration Tests
- Module interaction testing
- Database integration
- API endpoint testing
- End-to-end workflows

### 8.3 Performance Tests
- Large dataset handling (4000+ files)
- Search performance
- Reorganization speed
- Memory usage profiling

### 8.4 UI Tests
- Component testing
- User workflow testing
- Cross-platform testing

## 9. Deployment Strategy

### 9.1 Packaging
- Electron Builder for cross-platform packaging
- Code signing for macOS and Windows
- Embedded Python runtime
- Embedded Tesseract OCR

### 9.2 Installation
- Simple installer wizard
- Default configuration
- Optional custom paths
- Desktop shortcut creation

### 9.3 Updates
- electron-updater for automatic updates
- Delta updates for efficiency
- User notification system
- Rollback capability

## 10. Development Workflow

### 10.1 Phased Implementation
1. **Phase 1**: Core infrastructure (database, basic scanning)
2. **Phase 2**: Metadata extraction and indexing
3. **Phase 3**: Search and basic UI
4. **Phase 4**: Classification and reorganization
5. **Phase 5**: Advanced features (OCR, undo, reports)
6. **Phase 6**: Polish and packaging

### 10.2 Quality Gates
- All tests must pass before merging
- Code review required
- Linting and formatting checks
- Documentation updates

## 11. Future Extensibility

### 11.1 Planned Features
- Cloud sync (optional)
- Mobile companion app
- Advanced ML classification
- Custom document templates
- API for third-party integrations
- Multi-user support

### 11.2 Extension Points
- Plugin system for document extractors
- Custom classification models
- Additional report templates
- Alternative storage backends
- Different OCR engines
