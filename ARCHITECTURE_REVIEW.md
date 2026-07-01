# Architecture Review

**Date:** 2024-01-01
**Version:** v0.1 - Foundation
**Status:** Ready for External Review

---

## Table of Contents

1. [Complete Project Tree](#complete-project-tree)
2. [Top-Level Directory Explanations](#top-level-directory-explanations)
3. [Dependency Graph](#dependency-graph)
4. [Database Architecture](#database-architecture)
5. [Backend Module Dependencies](#backend-module-dependencies)
6. [Frontend Architecture](#frontend-architecture)
7. [Build Flow](#build-flow)
8. [Startup Sequence](#startup-sequence)
9. [Configuration Loading Sequence](#configuration-loading-sequence)
10. [Logging Flow](#logging-flow)
11. [Error Handling Flow](#error-handling-flow)
12. [Remaining Technical Debt](#remaining-technical-debt)
13. [Files with TODOs](#files-with-todos)
14. [Public APIs](#public-apis)
15. [Internal APIs](#internal-apis)
16. [Future Extension Points](#future-extension-points)

---

## Complete Project Tree

```
crms/
├── backend/                          # Python backend application
│   ├── classifier/                  # Document classification module
│   │   └── base.py                 # Base classifier interface
│   ├── core/                        # Core infrastructure
│   │   ├── __init__.py             # Core exports
│   │   ├── base.py                 # Base classes (BaseResult, BasePlugin, etc.)
│   │   ├── config.py               # Configuration management (Pydantic)
│   │   ├── constants.py            # Application constants
│   │   ├── exceptions.py           # Custom exception hierarchy
│   │   └── logging.py              # Logging configuration (Loguru)
│   ├── database/                    # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py           # Database connection manager
│   │   ├── migrations/             # Alembic migrations (to be implemented)
│   │   │   └── versions/          # Migration versions
│   │   └── schema.sql              # Database schema definition
│   ├── extractor/                   # Metadata extraction module
│   │   └── base.py                 # Base extractor interface
│   ├── pipeline/                    # Job queue and processing
│   │   └── job_queue.py            # Job queue placeholder
│   ├── plugins/                     # Plugin system
│   │   └── __init__.py
│   ├── scanner/                     # Document scanning module
│   │   ├── document_scanner.py     # Document scanner placeholder
│   │   └── hash_generator.py       # Hash generator placeholder
│   ├── scripts/                     # Utility scripts
│   │   ├── __init__.py
│   │   └── init_db.py              # Database initialization script
│   ├── tests/                       # Test suite
│   │   ├── conftest.py             # Pytest configuration
│   │   ├── test_config.py          # Configuration tests
│   │   ├── test_api/               # API tests (placeholder)
│   │   ├── test_core/              # Core module tests
│   │   ├── test_extractors/        # Extractor tests (placeholder)
│   │   ├── test_services/          # Service tests (placeholder)
│   │   └── test_utils/             # Utility tests (placeholder)
│   ├── validation/                  # Validation module
│   │   └── gst_validator.py        # GST validator placeholder
│   ├── main.py                      # Backend entry point
│   ├── pyproject.toml              # Python project configuration
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   ├── .flake8                     # Flake8 configuration
│   └── .mypy.ini                   # Mypy configuration
│
├── frontend/                         # React + Electron frontend
│   ├── electron/                   # Electron main process
│   │   ├── main.ts                 # Electron main process entry
│   │   ├── ipc/                    # IPC handlers (placeholder)
│   │   └── utils/                  # Electron utilities (placeholder)
│   ├── public/                     # Static assets
│   │   └── icons/                  # Application icons
│   ├── src/                        # React application source
│   │   ├── assets/                 # Static assets
│   │   ├── components/             # Reusable UI components (placeholder)
│   │   ├── hooks/                  # Custom React hooks (placeholder)
│   │   ├── pages/                  # Page-level components (placeholder)
│   │   ├── services/               # API and business logic (placeholder)
│   │   ├── store/                  # Redux store (placeholder)
│   │   ├── types/                  # TypeScript type definitions
│   │   ├── utils/                  # Utility functions (placeholder)
│   │   ├── App.tsx                 # Root React component
│   │   ├── main.tsx                # React entry point
│   │   └── index.css               # Global styles
│   ├── tests/                      # Frontend tests
│   │   ├── components/             # Component tests (placeholder)
│   │   ├── pages/                  # Page tests (placeholder)
│   │   └── utils/                  # Utility tests (placeholder)
│   ├── electron-builder.yml        # Electron packaging configuration
│   ├── index.html                  # HTML template
│   ├── package.json                # Node.js dependencies
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tsconfig.node.json          # TypeScript config for Node
│   ├── vite.config.ts              # Vite build configuration
│   ├── vitest.config.ts            # Vitest configuration
│   ├── .eslintrc.js                # ESLint configuration
│   ├── .prettierrc                 # Prettier configuration
│   ├── .env.example                # Environment variables template
│   └── tests/setup.ts              # Test setup
│
├── build/                           # Build resources
│   ├── resources/                  # Build-time resources
│   │   ├── certificates/           # Code signing certificates
│   │   ├── icons/                  # Application icons
│   │   └── splashscreens/          # Splash screens
│   └── scripts/                    # Build scripts
│
├── docs/                            # Documentation
│   └── diagrams/                   # Architecture diagrams
│       ├── system_architecture.md
│       ├── backend_architecture.md
│       ├── frontend_architecture.md
│       ├── database_relationships.md
│       └── module_dependencies.md
│
├── samples/                         # Sample documents for testing
│   ├── invoices/                   # Sample invoices
│   ├── bank/                       # Sample bank statements
│   ├── gst/                        # Sample GST documents
│   ├── ledger/                     # Sample ledger entries
│   ├── salary/                     # Sample salary slips
│   ├── quotation/                  # Sample quotations
│   ├── purchase/                   # Sample purchase orders
│   ├── delivery_challan/           # Sample delivery challans
│   └── README.md                    # Sample document guidelines
│
├── shared/                          # Shared code between frontend/backend
│   ├── constants/                  # Shared constants (placeholder)
│   ├── types/                      # Shared type definitions (placeholder)
│   └── utils/                      # Shared utilities (placeholder)
│
├── .github/                         # GitHub configuration
│   └── workflows/                  # CI/CD workflows (placeholder)
│
├── .gitignore                       # Git ignore rules
├── .pre-commit-config.yaml          # Pre-commit hooks configuration
├── ARCHITECTURE.md                  # System architecture documentation
├── CHANGELOG.md                     # Version history
├── CODE_OF_CONDUCT.md              # Community guidelines
├── CONTRIBUTING.md                  # Contribution guidelines
├── DATABASE_SCHEMA.sql              # Database schema (duplicate - in backend/)
├── DECISIONS.md                     # Architectural decision records
├── DEVELOPMENT_STATUS.md            # Current development status
├── LICENSE                          # MIT license
├── PACKAGE.json                     # Root package.json (for monorepo tools)
├── PROJECT_STRUCTURE.md             # Project structure documentation
├── README.md                        # Project README
├── ROADMAP.md                       # Development roadmap
├── SECURITY.md                      # Security policy
└── TECH_STACK.md                    # Technology stack documentation
```

---

## Top-Level Directory Explanations

### backend/
**Purpose:** Python backend application containing all server-side logic.

**Contents:**
- `core/` - Core infrastructure (configuration, logging, exceptions, base classes)
- `database/` - Database layer (connection, schema, migrations)
- `scanner/` - Document scanning and change detection
- `extractor/` - Metadata extraction from documents
- `classifier/` - Document classification logic
- `validation/` - Business validation (GST, sequences, etc.)
- `pipeline/` - Job queue and processing pipeline
- `plugins/` - Plugin system for extensibility
- `tests/` - Test suite
- `scripts/` - Utility scripts
- `main.py` - Backend entry point
- Configuration files (pyproject.toml, requirements.txt, etc.)

**Responsibilities:**
- Document processing and indexing
- Database operations
- Business logic
- IPC communication with Electron

### frontend/
**Purpose:** React + Electron frontend application.

**Contents:**
- `electron/` - Electron main process (window management, IPC)
- `src/` - React application source code
- `public/` - Static assets
- `tests/` - Frontend test suite
- Configuration files (package.json, tsconfig, vite.config, etc.)

**Responsibilities:**
- User interface
- User interaction
- Display and visualization
- IPC communication with Python backend

### build/
**Purpose:** Build-time resources and scripts.

**Contents:**
- `resources/` - Icons, certificates, splash screens
- `scripts/` - Build and packaging scripts

**Responsibilities:**
- Application packaging
- Code signing
- Icon generation

### docs/
**Purpose:** Project documentation.

**Contents:**
- `diagrams/` - Architecture diagrams (Mermaid)

**Responsibilities:**
- Architecture documentation
- Design documentation
- Visual diagrams

### samples/
**Purpose:** Sample documents for testing and development.

**Contents:**
- Subdirectories for different document types
- README with sanitization guidelines

**Responsibilities:**
- Test data
- Development examples
- Reference documents

### shared/
**Purpose:** Shared code between frontend and backend.

**Contents:**
- `constants/` - Shared constants
- `types/` - Shared type definitions
- `utils/` - Shared utilities

**Responsibilities:**
- Code reuse
- Type sharing
- Common utilities

**Note:** Currently placeholder, to be populated when needed.

### .github/
**Purpose:** GitHub-specific configuration.

**Contents:**
- `workflows/` - CI/CD workflows

**Responsibilities:**
- GitHub Actions
- Issue templates
- Pull request templates

---

## Dependency Graph

### External Dependencies

#### Backend (Python)
```
pydantic (2.5.0)
├── pydantic-settings (2.1.0)
│   └── python-dotenv (1.0.0)
├── pydantic-core
└── typing-extensions

loguru (0.7.2)
└── colorama

sqlalchemy (2.0.23)
├── typing-extensions
└── greenlet

aiosqlite (0.19.0)
└── sqlite3 (built-in)

celery (5.3.4)
├── kombu
├── billiard
└── click

redis (5.0.1)
└── hiredis

PyPDF2 (3.0.1)
pdfplumber (0.10.3)
├── Pillow (10.1.0)
└── pdfminer.six

openpyxl (3.1.2)
└── et-xmlfile

pandas (2.1.3)
├── numpy (1.26.2)
├── python-dateutil (2.8.2)
└── pytz (2023.3)

python-docx (1.1.0)
└── lxml

pytesseract (0.3.10)
└── Pillow

pyocr (0.8)
└── Pillow

xlsxwriter (3.1.9)

pluggy (1.3.0)

scikit-learn (1.3.2)
├── numpy (1.26.2)
├── scipy
├── joblib
└── threadpoolctl

pytest (7.4.3)
├── pluggy
└── iniconfig

pytest-asyncio (0.21.1)
├── pytest
└── async-timeout

pytest-cov (4.1.0)
├── pytest
└── coverage

httpx (0.25.2)
├── httpcore
├── h11
└── certifi

black (23.11.0)
├── click
└── mypy-extensions

flake8 (6.1.0)
├── pycodestyle
├── pyflakes
└── mccabe

isort (5.12.0)

mypy (1.7.1)
├── mypy-extensions
├── typed-ast
└── typeshed
```

#### Frontend (Node.js)
```
react (18.2.0)
└── react-dom (18.2.0)

typescript (5.2.2)

vite (5.0.0)
├── esbuild
├── postcss
└── rollup

@vitejs/plugin-react (4.2.0)
└── @vitejs/plugin-react-swc

eslint (8.53.0)
├── @typescript-eslint/eslint-plugin (6.10.0)
├── @typescript-eslint/parser (6.10.0)
├── eslint-plugin-react-hooks (4.6.0)
└── eslint-plugin-react-refresh (0.4.4)

prettier (3.1.0)

vitest (1.0.0)
└── @vitest/ui
```

### Internal Module Dependencies

#### Backend
```
main.py
├── core.config
├── core.logging
└── database.connection

database.connection
├── core.config
├── core.logging
└── core.exceptions

scanner.document_scanner
├── core.config
├── core.logging
├── core.exceptions
├── core.base
└── database.connection

scanner.hash_generator
├── core.config
├── core.logging
├── core.exceptions
├── core.base
└── database.connection

extractor.base
├── core.config
├── core.logging
├── core.exceptions
└── core.base

classifier.base
├── core.config
├── core.logging
├── core.exceptions
└── core.base

validation.gst_validator
├── core.config
├── core.logging
├── core.exceptions
└── core.base

pipeline.job_queue
├── core.config
├── core.logging
├── core.exceptions
└── core.base

scripts.init_db
├── core.config
├── core.logging
└── database.connection
```

#### Frontend
```
main.ts (Electron)
├── preload.ts
└── Window management

preload.ts
└── IPC bridge

App.tsx
├── components/
├── pages/
├── hooks/
└── services/
```

---

## Database Architecture

### Database Technology
- **Primary:** SQLite 3 with FTS5 full-text search
- **Analytics:** DuckDB (planned for v0.5, currently disabled)

### Schema Overview

#### Core Tables (9 tables)
1. **documents** - Primary document storage
2. **metadata** - Extracted metadata (key-value pairs)
3. **fts_documents** - FTS5 virtual table for full-text search
4. **audit_log** - System operation tracking
5. **undo_log** - Undo/redo capability
6. **version_log** - Document version history
7. **relationships** - Document relationships
8. **gst_validations** - GST validation results
9. **sequences** - Sequence detection results

#### Configuration Tables (3 tables)
10. **folder_templates** - Folder structure templates
11. **classification_rules** - Classification rules
12. **config** - System configuration

#### Reporting Tables (1 table)
13. **reports** - Generated report information

### Key Relationships

```
documents (1) ----< (N) metadata
documents (1) ----< (N) version_log
documents (1) ----< (N) relationships (as source)
documents (1) ----< (N) relationships (as target)
documents (1) ----< (N) gst_validations
documents (1) ----< (N) sequences
documents (1) ----< (N) audit_log
documents (1) ----< (1) documents (duplicate_of)
version_log (1) ----< (N) version_log (previous_version)
```

### Indexes

#### documents table
- `idx_documents_file_hash` - For duplicate detection
- `idx_documents_file_type` - For filtering by type
- `idx_documents_financial_year` - For filtering by year
- `idx_documents_document_type` - For filtering by document type
- `idx_documents_status` - For filtering by status
- `idx_documents_is_duplicate` - For duplicate queries

#### metadata table
- `idx_metadata_document_id` - For document lookups
- `idx_metadata_key` - For key queries
- `idx_metadata_value` - For value searches
- `idx_metadata_confidence` - For confidence filtering
- `idx_metadata_needs_review` - For review workflow

### Triggers

#### FTS5 Sync Triggers (3 triggers)
1. `fts_documents_insert` - Sync inserts to FTS index
2. `fts_documents_delete` - Sync deletes from FTS index
3. `fts_documents_update` - Sync updates to FTS index

### Views

1. **v_document_stats** - Document statistics (count, size, dates)
2. **v_documents_with_metadata** - Documents with metadata summary
3. **v_duplicate_groups** - Duplicate document groups
4. **v_financial_year_distribution** - Documents by financial year and type

### Default Data

- 1 folder template (Standard Business)
- 11 classification rules (filename patterns)
- 8 configuration entries (system settings)

### See Also
- [Database Relationships Diagram](docs/diagrams/database_relationships.md)
- [DATABASE_SCHEMA.sql](backend/database/schema.sql)

---

## Backend Module Dependencies

### Dependency Hierarchy

```
Level 0 (No Dependencies):
- core.constants
- core.exceptions

Level 1 (Depends on Level 0):
- core.base
- core.logging (depends on core.exceptions)
- core.config (depends on core.exceptions)

Level 2 (Depends on Level 1):
- database.connection (depends on core.config, core.logging, core.exceptions)

Level 3 (Depends on Level 2):
- scanner.document_scanner (depends on core.config, core.logging, core.exceptions, core.base, database.connection)
- scanner.hash_generator (depends on core.config, core.logging, core.exceptions, core.base, database.connection)
- extractor.base (depends on core.config, core.logging, core.exceptions, core.base)
- classifier.base (depends on core.config, core.logging, core.exceptions, core.base)
- validation.gst_validator (depends on core.config, core.logging, core.exceptions, core.base)
- pipeline.job_queue (depends on core.config, core.logging, core.exceptions, core.base)

Level 4 (Entry Points):
- main.py (depends on core.config, core.logging, database.connection)
- scripts.init_db.py (depends on core.config, core.logging, database.connection)
```

### Module Responsibilities

#### core/
- **config.py** - Configuration management with Pydantic
- **logging.py** - Structured logging with Loguru
- **exceptions.py** - Custom exception hierarchy
- **base.py** - Base classes for all modules
- **constants.py** - Application constants

#### database/
- **connection.py** - Database connection management
- **schema.sql** - Database schema definition
- **migrations/** - Alembic migrations (to be implemented)

#### scanner/
- **document_scanner.py** - Document scanning (placeholder)
- **hash_generator.py** - SHA-256 hash generation (placeholder)

#### extractor/
- **base.py** - Base extractor interface (placeholder)

#### classifier/
- **base.py** - Base classifier interface (placeholder)

#### validation/
- **gst_validator.py** - GST validation (placeholder)

#### pipeline/
- **job_queue.py** - Job queue management (placeholder)

#### plugins/
- Plugin system infrastructure (placeholder)

### See Also
- [Module Dependencies Diagram](docs/diagrams/module_dependencies.md)

---

## Frontend Architecture

### Technology Stack
- **Framework:** React 18 with TypeScript
- **Desktop:** Electron
- **Build Tool:** Vite 5.0
- **State Management:** Redux Toolkit (planned)
- **Styling:** CSS (planned to add CSS-in-JS)

### Architecture Layers

#### Electron Main Process
- **main.ts** - Window management, application lifecycle
- **IPC Handlers** - Communication with Python backend (placeholder)

#### Electron Renderer Process
- **preload.ts** - Context bridge for secure IPC

#### React Application
- **Components** - Reusable UI components (placeholder)
- **Pages** - Page-level components (placeholder)
- **Hooks** - Custom React hooks (placeholder)
- **Services** - API client and business logic (placeholder)
- **Store** - Redux state management (placeholder)
- **Types** - TypeScript type definitions
- **Utils** - Utility functions (placeholder)

### Communication Flow

```
React Component
    ↓
Redux Action / API Call
    ↓
IPC Bridge (preload.ts)
    ↓
Electron IPC Handler
    ↓
Python Backend (stdin/stdout)
```

### See Also
- [Frontend Architecture Diagram](docs/diagrams/frontend_architecture.md)

---

## Build Flow

### Backend Build Process

```
1. Source Code (Python)
   ↓
2. Type Checking (mypy)
   ↓
3. Linting (flake8)
   ↓
4. Formatting (black, isort)
   ↓
5. Testing (pytest)
   ↓
6. Packaging (setuptools/wheel)
   ↓
7. Distribution (wheel/sdist)
```

### Frontend Build Process

```
1. Source Code (TypeScript + React)
   ↓
2. Type Checking (tsc)
   ↓
3. Linting (ESLint)
   ↓
4. Formatting (Prettier)
   ↓
5. Testing (Vitest)
   ↓
6. Building (Vite)
   ↓
7. Bundling (Vite + Rollup)
   ↓
8. Electron Packaging (electron-builder)
   ↓
9. Distribution (DMG/EXE/AppImage)
```

### Build Commands

#### Backend
```bash
# Type checking
mypy core/ --ignore-missing-imports

# Linting
flake8 .

# Formatting
black .
isort .

# Testing
pytest tests/ -v --cov

# Build (not yet implemented)
python -m build
```

#### Frontend
```bash
# Type checking
tsc --noEmit

# Linting
npm run lint

# Formatting
npm run format

# Testing
npm test

# Build
npm run build

# Package (Electron)
npm run build:electron
```

---

## Startup Sequence

### Backend Startup

```
1. main.py entry point
   ↓
2. setup_logging() - Configure Loguru
   ↓
3. get_settings() - Load configuration from .env
   ↓
4. DatabaseConnection() - Initialize database connection
   ↓
5. IPCHandler() - Initialize IPC handler
   ↓
6. asyncio.run(main()) - Start async event loop
   ↓
7. IPCHandler.run() - Enter IPC loop
   ↓
8. Ready to receive commands
```

### Frontend Startup

```
1. Electron main process starts
   ↓
2. Create main window
   ↓
3. Load preload script
   ↓
4. Load React application
   ↓
5. Vite dev server (development) or bundled app (production)
   ↓
6. React app initializes
   ↓
7. Redux store initializes (planned)
   ↓
8. API client initializes (planned)
   ↓
9. Ready for user interaction
```

---

## Configuration Loading Sequence

### Backend Configuration Loading

```
1. Application starts
   ↓
2. python-dotenv loads .env file
   ↓
3. Pydantic Settings classes load environment variables
   ↓
4. Field validators run
   ↓
5. get_settings() with lru_cache returns cached instance
   ↓
6. Configuration available throughout application
```

### Configuration Hierarchy

```
Environment Variables (.env)
    ↓
Pydantic Settings Classes
    ├── DatabaseConfig (prefix: DATABASE_)
    ├── IPCConfig (prefix: IPC_)
    ├── OCRConfig (prefix: OCR_)
    ├── FileProcessingConfig (no prefix)
    ├── ClassificationConfig (no prefix)
    ├── ReorganizationConfig (no prefix)
    ├── LoggingConfig (no prefix)
    ├── CacheConfig (no prefix)
    ├── PerformanceConfig (no prefix)
    ├── JobQueueConfig (prefix: JOB_QUEUE_)
    └── AnalyticsConfig (prefix: ANALYTICS_)
    ↓
Settings (root class)
    ↓
Application code
```

### Frontend Configuration Loading

```
1. Application starts
   ↓
2. Vite loads .env file
   ↓
3. Environment variables available via import.meta.env
    ↓
Application code
```

---

## Logging Flow

### Backend Logging

```
1. Application code calls get_logger(__name__)
    ↓
2. Loguru logger returned with module name bound
    ↓
3. Application logs messages
    ↓
4. Loguru handlers process messages
    ├── Console handler (stderr, colored, level-configured)
    ├── File handler (general logs, rotated, compressed)
    └── Error handler (errors only, rotated, compressed)
    ↓
5. Logs written to files
    ├── logs/crms_YYYY-MM-DD.log (general)
    └── logs/crms_errors_YYYY-MM-DD.log (errors)
```

### Log Levels

- **DEBUG** - Detailed diagnostic information
- **INFO** - General informational messages
- **WARNING** - Warning messages
- **ERROR** - Error messages
- **CRITICAL** - Critical errors

### Log Rotation

- **Size:** 10 MB per file
- **Retention:** 30 days
- **Compression:** ZIP compression

---

## Error Handling Flow

### Backend Error Handling

```
1. Exception occurs in application code
    ↓
2. Try-except block catches exception
    ↓
3. Specific exception type caught (sqlite3.Error, IOError, OSError, etc.)
    ↓
4. Logger.error() called with exc_info=True
    ↓
5. Custom exception raised (DatabaseError, ConfigurationError, etc.)
    ↓
6. Exception propagates up call stack
    ↓
7. Top-level handler catches and logs
    ↓
8. User-friendly error message returned
```

### Exception Hierarchy

```
CRMSException (base)
    ├── ConfigurationError
    ├── DatabaseError
    ├── FileProcessingError
    ├── ExtractionError
    ├── ClassificationError
    ├── ValidationError
    └── PluginError
```

### Error Handling Principles

1. **Never silently catch exceptions** - Always log and handle
2. **Use specific exception types** - Avoid broad `except Exception`
3. **Log with context** - Use exc_info=True for debugging
4. **Convert to custom exceptions** - Provide clear error types
5. **User-friendly messages** - Never expose stack traces to users

---

## Remaining Technical Debt

### High Priority

1. **Database Migration System** (Critical)
   - **Issue:** No migration system exists
   - **Impact:** Schema changes risky without rollback
   - **Plan:** Implement Alembic in Milestone 2
   - **Location:** backend/database/migrations/

2. **Global Singleton Usage** (High)
   - **Issue:** Global db_connection instance
   - **Impact:** Violates DI, hard to test
   - **Plan:** Remove in Milestone 2 with DI
   - **Location:** backend/database/connection.py:75

3. **No Electron IPC Implementation** (High)
   - **Issue:** Electron main process is template
   - **Impact:** Frontend cannot communicate with backend
   - **Plan:** Implement in Milestone 2
   - **Location:** frontend/electron/

### Medium Priority

4. **DuckDB Build Issues** (Medium)
   - **Issue:** DuckDB disabled due to build issues on macOS ARM64
   - **Impact:** Analytics features delayed
   - **Plan:** Evaluate in v0.5
   - **Location:** backend/requirements.txt

5. **Low Test Coverage** (Medium)
   - **Issue:** Only 62% coverage, only config tested
   - **Impact:** No tests for core functionality
   - **Plan:** Add tests as modules implemented
   - **Location:** backend/tests/

6. **No Integration Tests** (Medium)
   - **Issue:** No end-to-end tests
   - **Impact:** Integration issues may go undetected
   - **Plan:** Add in Milestone 2
   - **Location:** backend/tests/integration/

7. **Missing Frontend Tests** (Medium)
   - **Issue:** Frontend has test framework but no tests
   - **Impact:** UI bugs may go undetected
   - **Plan:** Add as UI implemented
   - **Location:** frontend/tests/

### Low Priority

8. **Configuration Migration Strategy** (Low)
   - **Issue:** No strategy for config migration between versions
   - **Impact:** Config changes may break installations
   - **Plan:** Document or implement
   - **Location:** backend/core/config.py

9. **No Secrets Management** (Low)
   - **Issue:** No encryption for sensitive config values
   - **Impact:** Limits future security enhancements
   - **Plan:** Acceptable for offline app, evaluate if needed
   - **Location:** backend/core/config.py

10. **Missing Redis Fallback** (Low)
    - **Issue:** Job queue requires Redis, no fallback
    - **Impact:** Users must install Redis
    - **Plan:** Document or implement in-memory queue fallback
    - **Location:** backend/pipeline/job_queue.py

---

## Files with TODOs

### backend/database/connection.py
```python
# Line 140: TODO: Remove global instance in v0.2 when dependency injection is fully implemented
db_connection = DatabaseConnection()
```

### Other TODOs
- **frontend/electron/main.ts** - No TODOs yet (placeholder)
- **frontend/electron/preload.ts** - No TODOs yet (placeholder)
- **backend/scanner/document_scanner.py** - Placeholder TODO (not yet implemented)
- **backend/scanner/hash_generator.py** - Placeholder TODO (not yet implemented)
- **backend/extractor/base.py** - Placeholder TODO (not yet implemented)
- **backend/classifier/base.py** - Placeholder TODO (not yet implemented)
- **backend/pipeline/job_queue.py** - Placeholder TODO (not yet implemented)
- **backend/validation/gst_validator.py** - Placeholder TODO (not yet implemented)

---

## Public APIs

### Backend

#### core/__init__.py
```python
# Configuration
def get_settings() -> Settings
class Settings(BaseSettings)
class DatabaseConfig(BaseSettings)
class IPCConfig(BaseSettings)
class OCRConfig(BaseSettings)
class FileProcessingConfig(BaseSettings)
class ClassificationConfig(BaseSettings)
class ReorganizationConfig(BaseSettings)
class LoggingConfig(BaseSettings)
class CacheConfig(BaseSettings)
class PerformanceConfig(BaseSettings)
class JobQueueConfig(BaseSettings)
class AnalyticsConfig(BaseSettings)

# Exceptions
class CRMSException(Exception)
class ConfigurationError(CRMSException)
class DatabaseError(CRMSException)
class FileProcessingError(CRMSException)
class ExtractionError(CRMSException)
class ClassificationError(CRMSException)
class ValidationError(CRMSException)
class PluginError(CRMSException)

# Base Classes
class BaseResult(BaseModel)
class BaseExtractor(ABC)
class BaseClassifier(ABC)
class BaseValidator(ABC)
class BasePlugin(ABC)

# Logging
def setup_logging(...)
def get_logger(name: str)
```

#### database/connection.py
```python
class DatabaseConnection:
    def __init__(self, settings: Optional[Settings] = None)
    @contextmanager
    def get_sqlite_connection(self) -> Any
    @contextmanager
    def get_duckdb_connection(self) -> Any
    def initialize_sqlite(self, schema_path: str) -> None

# Global instance (to be removed in v0.2)
db_connection = DatabaseConnection()
```

#### main.py
```python
class IPCHandler:
    def __init__(self)
    async def handle_command(self, command: dict) -> dict
    async def run(self)

async def main()
```

### Frontend

#### No public APIs yet (all placeholders)

---

## Internal APIs

### Backend

#### core/config.py
```python
# Internal helpers
def get_default_tesseract_path() -> str
def get_default_tessdata_path() -> str
```

#### core/logging.py
```python
# Internal implementation
logger (Loguru instance)
```

#### database/connection.py
```python
# Internal methods
def _validate_path(self, path: Path) -> Path
```

### Frontend

#### No internal APIs yet (all placeholders)

---

## Future Extension Points

### 1. Repository Pattern (Milestone 2)
**Location:** backend/database/repositories/
**Purpose:** Abstract data access layer
**Extension Points:**
- BaseRepository class
- DocumentRepository
- MetadataRepository
- RelationshipRepository
- Custom repositories per domain

### 2. Unit of Work Pattern (Milestone 2)
**Location:** backend/database/unitOfWork.py
**Purpose:** Transaction management
**Extension Points:**
- UnitOfWork class
- Transaction context manager
- Commit/rollback operations

### 3. Document Processors (Milestone 2)
**Location:** backend/extractor/
**Purpose:** Document-specific extractors
**Extension Points:**
- PDFExtractor
- ExcelExtractor
- WordExtractor
- ImageExtractor
- Custom extractors via plugins

### 4. Classifiers (Milestone 2)
**Location:** backend/classifier/
**Purpose:** Document classification strategies
**Extension Points:**
- RuleBasedClassifier
- MLClassifier
- Custom classifiers via plugins

### 5. Validators (Milestone 4)
**Location:** backend/validation/
**Purpose:** Business validation logic
**Extension Points:**
- GSTValidator
- SequenceValidator
- DuplicateValidator
- Custom validators via plugins

### 6. IPC Channels (Milestone 2)
**Location:** frontend/electron/ipc/
**Purpose:** IPC communication channels
**Extension Points:**
- scan_directory
- extract_metadata
- search_documents
- classify_document
- validate_gst
- reorganize_documents

### 7. Redux Slices (Milestone 2)
**Location:** frontend/src/store/
**Purpose:** State management
**Extension Points:**
- documentsSlice
- metadataSlice
- searchSlice
- uiSlice

### 8. React Hooks (Milestone 2)
**Location:** frontend/src/hooks/
**Purpose:** Custom React hooks
**Extension Points:**
- useDocuments
- useSearch
- useMetadata
- useClassification

### 9. Plugin System (Milestone 3)
**Location:** backend/plugins/
**Purpose:** Extensibility
**Extension Points:**
- Plugin hooks
- Plugin discovery
- Plugin lifecycle management

### 10. Report Generators (Milestone 5)
**Location:** backend/reports/
**Purpose**: Report generation
**Extension Points:**
- ReportGenerator base class
- ExcelReportGenerator
- PDFReportGenerator
- Custom report generators

---

## Diagrams

All architecture diagrams are available in [docs/diagrams/](docs/diagrams/):

- [System Architecture](docs/diagrams/system_architecture.md)
- [Backend Architecture](docs/diagrams/backend_architecture.md)
- [Frontend Architecture](docs/diagrams/frontend_architecture.md)
- [Database Relationships](docs/diagrams/database_relationships.md)
- [Module Dependencies](docs/diagrams/module_dependencies.md)

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture documentation
- [DECISIONS.md](DECISIONS.md) - Architectural decision records
- [TECH_STACK.md](TECH_STACK.md) - Technology stack documentation
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project structure documentation

---

**Document Version:** 1.0
**Last Updated:** 2024-01-01
**Next Review:** After Milestone 2 completion
