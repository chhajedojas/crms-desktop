# Company Records Management System (CRMS) - Project Structure

## Root Directory Structure

```
crms/
├── README.md
├── LICENSE
├── ARCHITECTURE.md
├── DATABASE_SCHEMA.sql
├── PROJECT_STRUCTURE.md
├── .gitignore
├── .env.example
├── package.json
├── requirements.txt
├── pyproject.toml
├── electron-builder.yml
├── tsconfig.json
├── vite.config.ts
├── .eslintrc.js
├── .prettierrc
├── pytest.ini
├── setup.py
└── .github/
    └── workflows/
        ├── build.yml
        ├── test.yml
        └── release.yml
```

## Backend Structure (Python)

```
backend/
├── main.py                      # IPC application entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Python project configuration
├── setup.py                    # Python package setup
├── pytest.ini                  # pytest configuration
├── .env.example                # Environment variables template
├── .python-version             # Python version specification
│
├── core/
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   ├── ipc_handler.py         # IPC communication handler
│   ├── logging.py              # Logging configuration
│   ├── constants.py            # Application constants
│   ├── exceptions.py           # Core exceptions
│   └── base.py                 # Base classes and interfaces
│
├── database/
│   ├── __init__.py
│   ├── connection.py           # Database connection management
│   ├── sqlite_manager.py      # SQLite database manager
│   ├── duckdb_manager.py      # DuckDB analytics manager
│   ├── schema.sql              # Database schema
│   ├── migrations/             # Database migrations
│   │   ├── __init__.py
│   │   └── versions/
│   └── seed.py                 # Seed data
│
├── scanner/
│   ├── __init__.py
│   ├── document_scanner.py     # Document scanning and change detection
│   ├── hash_generator.py      # SHA-256 hash calculation
│   ├── version_manager.py     # Document version tracking
│   └── change_detector.py     # File change detection
│
├── extractor/
│   ├── __init__.py
│   ├── base.py                # Base extractor interface
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── excel_extractor.py     # Excel data extraction
│   ├── word_extractor.py      # Word document extraction
│   ├── image_extractor.py     # Image metadata extraction
│   ├── invoice_extractor.py   # Invoice-specific extraction
│   └── gst_extractor.py       # GST data extraction
│
├── classifier/
│   ├── __init__.py
│   ├── base.py                # Base classifier interface
│   ├── rule_based.py          # Rule-based classifier
│   ├── ml_classifier.py       # ML-based classifier
│   ├── confidence_scorer.py   # Confidence score calculation
│   └── training_data.py       # Training data management
│
├── pipeline/
│   ├── __init__.py
│   ├── job_queue.py           # Job queue management
│   ├── processor.py           # Processing pipeline coordinator
│   ├── retry_handler.py       # Retry logic with exponential backoff
│   ├── progress_tracker.py    # Progress tracking for long operations
│   └── worker.py              # Worker pool management
│
├── validation/
│   ├── __init__.py
│   ├── gst_validator.py      # GST validation and compliance
│   ├── sequence_detector.py   # Invoice sequence detection
│   ├── duplicate_detector.py # Duplicate invoice detection
│   └── format_validator.py   # Document format validation
│
├── analytics/
│   ├── __init__.py
│   ├── relationship_graph.py  # Document relationship mapping
│   ├── bank_reconciler.py     # Bank reconciliation
│   ├── timeline_analyzer.py   # Customer/vendor timeline analysis
│   └── duckdb_queries.py     # DuckDB analytical queries
│
├── search/
│   ├── __init__.py
│   ├── fts_engine.py          # FTS5 search implementation
│   ├── query_builder.py       # Search query builder
│   ├── result_ranker.py       # Search result ranking
│   └── fuzzy_search.py        # Fuzzy search capabilities
│
├── reorganization/
│   ├── __init__.py
│   ├── folder_structure.py   # Folder structure suggestions
│   ├── reorganization_engine.py # Reorganization execution
│   ├── migration_planner.py    # Migration plan generation
│   └── undo_manager.py        # Undo and rollback operations
│
├── reports/
│   ├── __init__.py
│   ├── report_generator.py    # Report generation coordinator
│   ├── excel_generator.py     # Excel report generation
│   ├── templates/             # Report templates
│   │   ├── inventory.py
│   │   ├── duplicates.py
│   │   ├── gst_validation.py
│   │   ├── sequences.py
│   │   └── timelines.py
│   └── schedules.py           # Report scheduling
│
├── plugins/
│   ├── __init__.py
│   ├── plugin_manager.py      # Plugin system manager
│   ├── interfaces.py          # Plugin interfaces
│   ├── builtins/              # Built-in plugins
│   │   ├── __init__.py
│   │   ├── pdf_plugin.py
│   │   ├── excel_plugin.py
│   │   └── word_plugin.py
│   └── registry.py            # Plugin registry
│
├── models/
│   ├── __init__.py
│   ├── document.py            # Document model
│   ├── metadata.py            # Metadata model
│   ├── version_log.py         # Version log model
│   ├── relationship.py        # Relationship model
│   ├── gst_validation.py      # GST validation model
│   ├── sequence.py            # Sequence model
│   ├── audit_log.py           # Audit log model
│   ├── undo_log.py            # Undo log model
│   ├── report.py              # Report model
│   └── schemas.py             # Pydantic schemas
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py          # File utilities
│   ├── hash_utils.py          # Hash calculation
│   ├── date_utils.py          # Date parsing and formatting
│   ├── text_utils.py          # Text processing utilities
│   ├── excel_utils.py         # Excel generation utilities
│   ├── path_utils.py          # Path manipulation utilities
│   ├── confidence_utils.py    # Confidence score utilities
│   └── gst_utils.py           # GST validation utilities
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest configuration
│   ├── test_scanner/           # Scanner tests
│   │   ├── __init__.py
│   │   ├── test_document_scanner.py
│   │   ├── test_hash_generator.py
│   │   └── test_version_manager.py
│   ├── test_extractor/        # Extractor tests
│   │   ├── __init__.py
│   │   ├── test_pdf_extractor.py
│   │   ├── test_excel_extractor.py
│   │   └── test_invoice_extractor.py
│   ├── test_classifier/       # Classifier tests
│   │   ├── __init__.py
│   │   ├── test_rule_based.py
│   │   └── test_ml_classifier.py
│   ├── test_pipeline/         # Pipeline tests
│   │   ├── __init__.py
│   │   ├── test_job_queue.py
│   │   └── test_processor.py
│   ├── test_validation/       # Validation tests
│   │   ├── __init__.py
│   │   ├── test_gst_validator.py
│   │   └── test_sequence_detector.py
│   ├── test_analytics/        # Analytics tests
│   │   ├── __init__.py
│   │   ├── test_relationship_graph.py
│   │   └── test_bank_reconciler.py
│   ├── test_search/           # Search tests
│   │   ├── __init__.py
│   │   └── test_fts_engine.py
│   ├── test_reorganization/   # Reorganization tests
│   │   ├── __init__.py
│   │   └── test_reorganization_engine.py
│   ├── test_reports/          # Report tests
│   │   ├── __init__.py
│   │   └── test_report_generator.py
│   ├── test_plugins/          # Plugin tests
│   │   ├── __init__.py
│   │   └── test_plugin_manager.py
│   └── test_utils/            # Utility tests
│       ├── __init__.py
│       ├── test_file_utils.py
│       └── test_hash_utils.py
│
└── scripts/
    ├── init_db.py             # Database initialization
    ├── seed_data.py           # Seed data script
    ├── migrate.py             # Migration script
    ├── test_ocr.py            # OCR testing script
    └── benchmark.py           # Performance benchmarking
```

## Frontend Structure (React + Electron)

```
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── .eslintrc.js
├── .prettierrc
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── .env.example
├── .env.development
├── .env.production
│
├── electron/
│   ├── main.ts                # Electron main process
│   ├── preload.ts             # Preload script
│   ├── ipc/
│   │   ├── __init__.ts
│   │   ├── bridge.ts          # Python bridge implementation
│   │   ├── channels.ts        # IPC channel definitions
│   │   └── handlers.ts        # IPC request handlers
│   └── utils/
│       ├── __init__.ts
│       ├── path.ts            # Path utilities
│       ├── window.ts          # Window management
│       └── process.ts         # Process management
│
├── src/
│   ├── main.tsx               # React entry point
│   ├── App.tsx                # Root React component
│   ├── index.css              # Global styles
│   │
│   ├── components/
│   │   ├── common/            # Common UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Dialog.tsx
│   │   │   ├── Loading.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── layout/            # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── dashboard/         # Dashboard components
│   │   │   ├── StatCard.tsx
│   │   │   ├── RecentActivity.tsx
│   │   │   ├── QuickActions.tsx
│   │   │   ├── Charts.tsx
│   │   │   └── TimelineView.tsx
│   │   ├── documents/         # Document components
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentCard.tsx
│   │   │   ├── DocumentPreview.tsx
│   │   │   ├── FileTree.tsx
│   │   │   ├── DocumentFilter.tsx
│   │   │   └── MetadataEditor.tsx
│   │   ├── search/            # Search components
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   ├── SearchFilters.tsx
│   │   │   ├── SearchSuggestion.tsx
│   │   │   └── ConfidenceIndicator.tsx
│   │   ├── reorganization/    # Reorganization components
│   │   │   ├── ReorganizationWizard.tsx
│   │   │   ├── FolderPreview.tsx
│   │   │   ├── MigrationPlan.tsx
│   │   │   ├── ProgressTracker.tsx
│   │   │   └── UndoHistory.tsx
│   │   ├── validation/        # Validation components
│   │   │   ├── GSTValidator.tsx
│   │   │   ├── SequenceDetector.tsx
│   │   │   ├── RelationshipGraph.tsx
│   │   │   └── BankReconciler.tsx
│   │   └── reports/           # Report components
│   │       ├── ReportGenerator.tsx
│   │       ├── ReportPreview.tsx
│   │       ├── ReportList.tsx
│   │       └── ReportScheduler.tsx
│   │
│   ├── pages/                 # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Documents.tsx
│   │   ├── Search.tsx
│   │   ├── Reorganization.tsx
│   │   ├── Validation.tsx
│   │   ├── Analytics.tsx
│   │   ├── Reports.tsx
│   │   ├── Settings.tsx
│   │   └── AuditLog.tsx
│   │
│   ├── store/                 # Redux store
│   │   ├── index.ts
│   │   ├── slices/
│   │   │   ├── documentsSlice.ts
│   │   │   ├── searchSlice.ts
│   │   │   ├── reorganizationSlice.ts
│   │   │   ├── validationSlice.ts
│   │   │   ├── analyticsSlice.ts
│   │   │   ├── reportsSlice.ts
│   │   │   ├── pipelineSlice.ts
│   │   │   └── uiSlice.ts
│   │   └── middleware/
│   │       ├── ipcMiddleware.ts
│   │       └── loggerMiddleware.ts
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── useDocuments.ts
│   │   ├── useSearch.ts
│   │   ├── useReorganization.ts
│   │   ├── useValidation.ts
│   │   ├── useAnalytics.ts
│   │   ├── useReports.ts
│   │   ├── usePipeline.ts
│   │   └── useIPC.ts
│   │
│   ├── services/              # IPC services
│   │   ├── ipc.ts             # IPC client
│   │   ├── documents.ts
│   │   ├── search.ts
│   │   ├── reorganization.ts
│   │   ├── validation.ts
│   │   ├── analytics.ts
│   │   └── reports.ts
│   │
│   ├── types/                 # TypeScript types
│   │   ├── document.ts
│   │   ├── metadata.ts
│   │   ├── search.ts
│   │   ├── reorganization.ts
│   │   ├── validation.ts
│   │   ├── analytics.ts
│   │   ├── report.ts
│   │   ├── pipeline.ts
│   │   └── ipc.ts
│   │
│   ├── utils/                 # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   └── confidence.ts
│   │
│   └── assets/                # Static assets
│       ├── images/
│       ├── icons/
│       └── fonts/
│
├── public/                    # Public assets
│   ├── icons/
│   │   ├── icon.ico
│   │   ├── icon.png
│   │   └── icon.icns
│   └── logo.png
│
└── tests/                     # Frontend tests
    ├── setup.ts
    ├── components/
    │   ├── Button.test.tsx
    │   ├── DocumentCard.test.tsx
    │   └── SearchBar.test.tsx
    ├── pages/
    │   └── Dashboard.test.tsx
    ├── hooks/
    │   └── useIPC.test.ts
    └── utils/
        └── formatters.test.ts
```

## Shared Structure

```
shared/
├── types/                     # Shared TypeScript types
│   ├── document.ts
│   ├── metadata.ts
│   └── api.ts
├── constants/                 # Shared constants
│   └── index.ts
└── utils/                     # Shared utilities
    └── formatters.ts
```

## Documentation Structure

```
docs/
├── README.md
├── INSTALLATION.md
├── USER_GUIDE.md
├── DEVELOPER_GUIDE.md
├── API_DOCUMENTATION.md
├── ARCHITECTURE.md
├── DATABASE_SCHEMA.md
├── CONTRIBUTING.md
├── TESTING.md
├── DEPLOYMENT.md
└── CHANGELOG.md
```

## Build and Packaging Structure

```
build/
├── resources/                # Build resources
│   ├── icons/
│   ├── splashscreens/
│   └── certificates/
├── scripts/                  # Build scripts
│   ├── build.sh
│   ├── build.bat
│   └── notarize.sh
└── dist/                     # Build output (gitignored)
```

## Configuration Files

### Root Configuration Files
- `package.json` - Node.js dependencies and scripts
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python project configuration
- `electron-builder.yml` - Electron Builder configuration
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite build configuration
- `.eslintrc.js` - ESLint configuration
- `.prettierrc` - Prettier configuration
- `pytest.ini` - pytest configuration
- `.gitignore` - Git ignore rules
- `.env.example` - Environment variables template

### Backend Configuration Files
- `backend/requirements.txt` - Backend Python dependencies
- `backend/pyproject.toml` - Backend Python configuration
- `backend/.env.example` - Backend environment variables

### Frontend Configuration Files
- `frontend/package.json` - Frontend Node.js dependencies
- `frontend/tsconfig.json` - Frontend TypeScript configuration
- `frontend/vite.config.ts` - Frontend Vite configuration
- `frontend/tailwind.config.js` - Tailwind CSS configuration
- `frontend/.eslintrc.js` - Frontend ESLint configuration
- `frontend/.prettierrc` - Frontend Prettier configuration
- `frontend/.env.example` - Frontend environment variables

## Development Workflow

### File Naming Conventions
- Python files: `snake_case.py`
- TypeScript/React files: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- Test files: `test_<module>.py` for Python, `<Component>.test.tsx` for React
- Configuration files: `kebab-case` or `camelCase`

### Import Conventions
- Absolute imports for internal modules
- Relative imports for local modules
- Group imports: standard library, third-party, local

### Code Organization Principles
- One concern per file
- Clear separation between layers
- Consistent directory structure
- Logical grouping of related functionality

## Summary

This project structure follows best practices for:
- **Modularity**: Clear separation of concerns
- **Scalability**: Easy to add new features
- **Maintainability**: Logical organization
- **Testing**: Comprehensive test structure
- **Documentation**: Clear documentation structure
- **Build**: Automated build and packaging process
