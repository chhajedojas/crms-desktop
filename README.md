# CRMS - AI-Powered Document Intelligence Platform

An offline AI-powered document intelligence platform for Indian businesses. CRMS helps you find, classify, audit, and understand your business documents with confidence-scored extraction, relationship mapping, and smart reorganization.

## Vision

> Transform chaotic document repositories into intelligent, searchable, and auditable business intelligence systems—completely offline.

## Core Capabilities

- **Document Intelligence**: AI-powered extraction with confidence scores
- **Relationship Mapping**: Link invoices ↔ delivery challans ↔ payments ↔ ledgers
- **GST Validation**: Automated GST compliance checking
- **Sequence Detection**: Identify missing invoice numbers and gaps
- **Bank Reconciliation**: Match bank statements with payments
- **Smart Reorganization**: Professional folder structures with undo support
- **Full-Text Search**: Instant search across 4000+ documents in <100ms
- **Audit Trail**: Complete tamper-evident logging of all operations

## Processing Pipeline

All document processing follows this sequential pipeline:

```
Select Folder
       ↓
    Scanner
   (Detect new/modified/deleted files)
       ↓
  Hash Generator
   (SHA-256 for deduplication)
       ↓
Metadata Extraction
   (With confidence scores)
       ↓
      OCR
   (If text extraction fails)
       ↓
  Classification
   (Document type + confidence)
       ↓
    SQLite
   (Operational database)
       ↓
 DuckDB Analytics
   (Complex queries + reports)
       ↓
  Search Index
   (FTS5 full-text search)
       ↓
    Reports
   (Excel generation)
       ↓
  Dashboard
   (Visualization + UI)
```

**Key Pipeline Features:**
- **Incremental Processing**: Only reprocess changed files
- **Job Queue**: Resumable processing with retry logic
- **Progress Tracking**: Real-time progress updates for long operations
- **Error Recovery**: Failed jobs are retried with exponential backoff
- **Confidence Scoring**: All extracted data includes 0.0-1.0 confidence

## Engineering Rules

### Core Principles (Never Violate)

- **Never modify original documents** - All operations work on copies
- **All reorganization must be undoable** - Every operation must have rollback
- **Every feature must have tests** - No code without test coverage
- **Every module must compile independently** - No circular dependencies
- **Never use hard-coded paths** - All paths must be configurable
- **Use dependency injection** - No direct instantiation of dependencies
- **Every database migration must be reversible** - Always provide rollback
- **Long-running operations must show progress** - Real-time UI updates required
- **All file operations must be atomic** - Write to temp, then rename
- **Never log sensitive data** - No passwords, API keys, or personal info in logs

### Code Quality Standards

- **Type Safety**: All Python code must pass mypy strict mode
- **Formatting**: Use Black for Python, Prettier for TypeScript
- **Linting**: Pass flake8 (Python) and ESLint (TypeScript)
- **Documentation**: Every public function must have docstrings
- **Error Handling**: Never silently catch exceptions - log and handle
- **Resource Management**: Use context managers for file/database operations
- **Thread Safety**: All shared state must be thread-safe
- **Memory Efficiency**: Stream large files, never load entirely into memory

### AI/ML Guidelines

- **Never hallucinate document data** - Only extract what exists in the document
- **Always return source document** - Every AI answer must cite the source
- **Show confidence scores** - All AI outputs must include confidence levels
- **Explain matching logic** - Search results must explain why they matched
- **Keep all AI processing offline** - No external API calls for AI features
- **Manual review threshold** - Confidence < 0.7 requires human review
- **Training data versioning** - All ML models must be versioned

### Performance Targets

- **Scanning**: 5,000 files in under 3 minutes
- **Search Latency**: < 100ms for typical queries
- **Memory Usage**: < 1 GB during normal operation
- **Startup Time**: < 5 seconds to ready state
- **Reorganization**: 1,000 files in under 2 minutes
- **Report Generation**: < 30 seconds for standard reports
- **Database Size**: < 500 MB for 10,000 documents

### Error Handling Standards

- **Corrupted PDFs**: Log error, skip file, continue processing
- **Password-protected Excel**: Prompt user for password, skip if cancelled
- **Missing Permissions**: Log error, show user-friendly message, skip
- **Duplicate Filenames**: Append timestamp, preserve both files
- **Low OCR Confidence**: Flag for manual review, don't auto-classify
- **Database Locks**: Retry with exponential backoff, timeout after 30s
- **Disk Space Full**: Stop operation, show error, cleanup temp files
- **Network Errors**: (Should not occur - offline-first) Log as critical

## Repository Structure

```
crms/
├── backend/
│   ├── core/              # Configuration, constants, base classes
│   ├── scanner/           # Document scanning and change detection
│   ├── extractor/         # Metadata extraction (PDF, Excel, Word, Images)
│   ├── classifier/        # Document classification (rule-based + ML)
│   ├── search/            # FTS5 search implementation
│   ├── reports/           # Report generation (Excel, PDF)
│   ├── reorganization/   # Folder structure and reorganization
│   ├── database/          # SQLite schema, migrations, connection pool
│   ├── pipeline/          # Job queue, processing pipeline
│   ├── validation/        # GST validation, sequence detection
│   ├── analytics/         # DuckDB integration, relationship graph
│   ├── plugins/           # Plugin system and built-in plugins
│   ├── tests/             # Unit tests, integration tests
│   └── scripts/           # Utility scripts (init_db, migrations)
│
├── frontend/
│   ├── electron/          # Electron main process, IPC handlers
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page-level components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── store/         # Redux store, API slices
│   │   ├── services/      # API client, business logic
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── tests/             # Component tests, E2E tests
│   └── public/            # Static assets, icons
│
├── shared/                # Shared types, constants between frontend/backend
├── docs/                  # Documentation
├── build/                 # Build scripts, resources
└── .github/               # CI/CD workflows
```

## Development Workflow

### Getting Started

1. **Prerequisites**
   - Python 3.11+
   - Node.js 18+
   - Tesseract OCR (system package)

2. **Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd crms

   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python scripts/init_db.py

   # Frontend setup
   cd ../frontend
   npm install
   ```

3. **Development**
   ```bash
   # Terminal 1: Backend
   cd backend
   python main.py

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

### Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov

# Frontend tests
cd frontend
npm test

# Full test suite
npm run test:all
```

### Code Quality

```bash
# Backend linting
cd backend
black .
flake8 .
mypy .

# Frontend linting
cd frontend
npm run lint
npm run format
```

## Release Roadmap

### v0.1 - Foundation (Current Sprint)
**Goal**: Basic scanning and inventory
- ✅ Architecture design
- ✅ Database schema
- ✅ Project structure
- ✅ Python backend configuration (pyproject.toml, requirements.txt)
- ✅ Core modules (config, constants, exceptions, base classes, logging)
- ✅ Database connection management (SQLite with optional DuckDB)
- ✅ Testing framework configuration (pytest, coverage)
- ✅ Linting and formatting (black, flake8, mypy, isort)
- ✅ Pre-commit hooks configuration
- ✅ TypeScript and React configuration
- ✅ Placeholder modules for scanner, extractor, classifier, pipeline, validation
- 🔄 Document scanner implementation
- 🔄 Hash generator implementation
- 🔄 Metadata extraction implementation
- 🔄 OCR integration
- 🔄 Classification implementation
- 🔄 Search indexing
- 🔄 Inventory report generation

### v0.2 - Intelligence
**Goal**: Metadata extraction and search
- Metadata extraction (PDF, Excel, Word)
- OCR integration
- Basic classification
- FTS5 search
- Search UI

### v0.3 - Organization
**Goal**: Reorganization and undo
- Folder structure suggestions
- Reorganization engine
- Undo system
- Migration plan generation

### v0.4 - Validation
**Goal**: Business intelligence features
- GST validation
- Sequence detection
- Duplicate invoice detection
- Relationship graph
- Bank reconciliation helper

### v0.5 - Analytics
**Goal**: Advanced reporting and dashboard
- DuckDB integration
- Customer timelines
- Vendor timelines
- Dashboard UI
- Advanced reports

### v1.0 - Platform
**Goal**: Complete AI-powered platform
- ML-based classification
- Plugin system
- Advanced AI features
- Complete documentation
- Production installer

## Performance Benchmarks

Current targets for typical workload (5,000 documents):

| Operation | Target | Actual |
|-----------|--------|--------|
| Initial Scan | < 3 min | TBD |
| Incremental Rescan | < 30 sec | TBD |
| Search Query | < 100 ms | TBD |
| Reorganization | < 2 min | TBD |
| Report Generation | < 30 sec | TBD |
| Memory Usage | < 1 GB | TBD |

## Documentation

- [Architecture](ARCHITECTURE.md) - System architecture and design decisions
- [Database Schema](DATABASE_SCHEMA.sql) - Complete database schema
- [Project Structure](PROJECT_STRUCTURE.md) - Detailed folder structure
- [Installation Guide](docs/INSTALLATION.md) - Installation instructions
- [User Guide](docs/USER_GUIDE.md) - End-user documentation
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Developer documentation
- [API Documentation](docs/API_DOCUMENTATION.md) - IPC channel reference
- [Testing Guide](docs/TESTING.md) - Testing strategy and guidelines

## Contributing

Contributors must follow these rules:

1. **Read the architecture** - Understand the system before making changes
2. **Write tests first** - TDD approach for all new features
3. **Follow engineering rules** - Never violate core principles
4. **Update documentation** - Keep docs in sync with code
5. **Code review required** - All changes must be reviewed
6. **Performance tested** - Verify performance targets are met
7. **Security reviewed** - No security vulnerabilities introduced

## License

Proprietary - All rights reserved

## Support

For development support:
- Architecture questions: Review ARCHITECTURE.md
- Implementation questions: Review DEVELOPER_GUIDE.md
- Bug reports: Create issue with detailed reproduction steps
- Feature requests: Create issue with use case and requirements
