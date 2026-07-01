# Architectural Decision Records (ADR)

This document records important architectural decisions made in the CRMS (Company Records Management System) project. Each decision follows the standard ADR format to provide context, rationale, and future impact.

---

# ADR-001: Electron + React Desktop Application

**Date:** 2024-01-01
**Status:** Accepted

## Context
The CRMS system needs to be an offline desktop application that can process thousands of documents locally without requiring internet connectivity. The application needs a modern, responsive UI for document management, search, and visualization of business intelligence.

## Decision
Use Electron as the desktop framework with React for the frontend UI.

## Rationale
- **Offline-first**: Electron enables true offline functionality with no external dependencies
- **Cross-platform**: Single codebase supports Windows, macOS, and Linux
- **Web technologies**: React ecosystem provides excellent component libraries and developer experience
- **IPC capability**: Electron's IPC system allows direct communication with Python backend
- **Mature ecosystem**: Both Electron and React have extensive community support and documentation
- **Packaging**: Electron-builder simplifies creating installers for all platforms

## Alternatives Considered
- **Tauri**: Newer, lighter weight, but less mature ecosystem and Rust learning curve
- **Qt with Python**: Powerful but complex licensing and steeper learning curve
- **Web-based with PWA**: Cannot guarantee offline functionality and has limited file system access
- **Pure Python UI (Tkinter/PyQt)**: Lacks modern UI components and responsive design

## Advantages
- True offline operation with full file system access
- Modern, responsive UI with React component ecosystem
- Cross-platform deployment from single codebase
- Hot reloading during development
- Access to Node.js ecosystem for build tools

## Disadvantages
- Larger application bundle size (~100-200MB)
- Higher memory footprint compared to native applications
- Requires JavaScript/TypeScript knowledge for frontend development

## Future Impact
- Frontend and backend can be developed independently
- Easy to add web-based admin interface later (shared React components)
- Electron updates need to be managed for security patches

## Related Files
- `frontend/package.json`
- `frontend/electron/main.ts`
- `frontend/electron/preload.ts`
- `electron-builder.yml`

---

# ADR-002: Python Backend with Direct IPC

**Date:** 2024-01-01
**Status:** Accepted

## Context
The backend needs to process documents, manage databases, and perform OCR/classification operations. The system must handle heavy computation while keeping the UI responsive. Communication between Electron (JavaScript) and Python needs to be efficient and reliable.

## Decision
Use Python 3.11+ for backend with direct IPC (stdin/stdout) communication instead of HTTP/REST API.

## Rationale
- **Reduced overhead**: Direct IPC avoids HTTP protocol overhead in an offline desktop app
- **Simpler deployment**: No need to manage web server process or port binding
- **Better performance**: Binary IPC is faster than JSON over HTTP for local communication
- **Security**: No network exposure since communication is local only
- **Simpler error handling**: Process-level communication is easier to debug than HTTP errors
- **Offline-first**: No assumption of network availability

## Alternatives Considered
- **FastAPI with HTTP**: Unnecessary overhead for local communication, requires port management
- **gRPC**: Overkill for local IPC, adds complexity with proto files
- **ZeroMQ**: Additional dependency, more complex than needed
- **Named pipes**: Platform-specific, harder to implement cross-platform

## Advantages
- Minimal latency for local communication
- No need to manage HTTP server lifecycle
- Simpler deployment (single process)
- Easier to implement offline-first guarantees
- Lower memory footprint (no HTTP server overhead)

## Disadvantages
- Tighter coupling between frontend and backend
- Harder to test backend independently without IPC mock
- Cannot easily expose web API for remote access later
- Debugging IPC messages requires special tooling

## Future Impact
- Backend can be tested independently by creating IPC test harness
- If web API needed later, can add FastAPI alongside IPC
- IPC protocol must be versioned carefully for backward compatibility

## Related Files
- `backend/core/config.py` (IPCConfig)
- `frontend/electron/preload.ts`
- `backend/core/__init__.py` (IPCConfig export)

---

# ADR-003: SQLite as Primary Database

**Date:** 2024-01-01
**Status:** Accepted

## Context
The application needs to store document metadata, file hashes, search indexes, and audit trails. It must handle thousands of documents with full-text search capability while remaining completely offline. The database must be embedded (no external server) and support ACID transactions.

## Decision
Use SQLite as the primary operational database with FTS5 for full-text search.

## Rationale
- **Embedded**: No external database server required, true offline operation
- **Zero configuration**: Works out of the box with no setup
- **ACID compliant**: Guarantees data integrity during file operations
- **FTS5 support**: Built-in full-text search with excellent performance
- **Single file database**: Easy backup and portability
- **Mature and stable**: Widely used, well-tested, excellent Python support
- **Cross-platform**: Works identically on Windows, macOS, and Linux
- **Suitable scale**: Can handle millions of records efficiently

## Alternatives Considered
- **PostgreSQL**: Requires external server, too heavy for offline desktop app
- **MySQL/MariaDB**: Same issues as PostgreSQL
- **MongoDB**: Overkill, requires external server, less strict schema validation
- **DuckDB only**: Good for analytics but lacks some operational features
- **Flat files**: No ACID guarantees, poor query performance, no relationships

## Advantages
- True offline operation with zero external dependencies
- Excellent performance for document metadata (thousands of records)
- Built-in full-text search with FTS5
- Single file backup and portability
- Strong data integrity with ACID transactions
- Easy migration and versioning with schema files
- Excellent Python support (sqlite3 built-in, SQLAlchemy, aiosqlite)

## Disadvantages
- Limited write concurrency (single writer, multiple readers)
- Not ideal for very high write throughput (not a concern for this use case)
- Limited analytical query capabilities (addressed by DuckDB in v0.5)

## Future Impact
- Database file can be backed up with simple file copy
- Schema migrations must be carefully managed (reversible migrations required)
- If scale exceeds SQLite capacity, can migrate to PostgreSQL with minimal code changes (SQLAlchemy ORM)

## Related Files
- `backend/database/schema.sql`
- `backend/database/connection.py`
- `backend/core/config.py` (DatabaseConfig)

---

# ADR-004: DuckDB for Analytics (Deferred to v0.5)

**Date:** 2024-01-01
**Status:** Accepted (Implementation Deferred)

## Context
The application needs to generate complex analytical reports, perform aggregations, and create dashboards showing trends over time. SQLite is excellent for operational data but has limitations for complex analytical queries and aggregations.

## Decision
Use DuckDB as an analytical database alongside SQLite for complex reporting and dashboards.

## Rationale
- **Columnar storage**: Optimized for analytical queries and aggregations
- **SQL compatibility**: Uses standard SQL, easy to learn
- **Embedded**: No external server required
- **Excellent performance**: Fast aggregations on large datasets
- **Python integration**: First-class Python support
- **Separation of concerns**: SQLite for operations, DuckDB for analytics
- **Can import from SQLite**: Easy to sync data between databases

## Alternatives Considered
- **SQLite only**: Limited analytical performance, complex queries slow
- **PostgreSQL**: Requires external server, overkill for desktop app
- **Pandas in-memory**: Limited by RAM, not persistent, no SQL interface
- **ClickHouse**: Overkill, requires external server
- **No analytical DB**: Rely on application-level aggregation (slow, complex)

## Advantages
- Excellent performance for analytical queries
- Separation of operational and analytical workloads
- Can import/export data from SQLite easily
- Embedded, no external dependencies
- Modern, actively developed

## Disadvantages
- Additional dependency and complexity
- Requires data synchronization between SQLite and DuckDB
- Build issues on some platforms (temporarily disabled in v0.1)
- Learning curve for team unfamiliar with DuckDB

## Future Impact
- Need to implement data sync strategy (ETL from SQLite to DuckDB)
- Additional storage requirements (DuckDB database file)
- Testing complexity increases (two databases to manage)
- Can be added in v0.5 without affecting SQLite implementation

## Related Files
- `backend/requirements.txt` (duckdb temporarily disabled)
- `backend/database/connection.py` (optional DuckDB support)
- `backend/core/config.py` (AnalyticsConfig)

---

# ADR-005: Pydantic for Configuration Management

**Date:** 2024-01-01
**Status:** Accepted

## Context
The application has numerous configuration options across multiple domains (database, IPC, OCR, classification, etc.). Configuration needs to be type-safe, validated, and loaded from environment variables or config files.

## Decision
Use Pydantic with pydantic-settings for configuration management.

## Rationale
- **Type safety**: Automatic type checking and conversion
- **Validation**: Built-in validators for common patterns (ports, URLs, enums)
- **Environment variables**: Native support with `pydantic-settings`
- **Nested configs**: Support for complex, nested configuration structures
- **IDE support**: Excellent autocomplete and type hints
- **Documentation**: Can generate config documentation from schemas
- **Singleton pattern**: Easy to implement with lru_cache
- **Default values**: Clear default values for all settings

## Alternatives Considered
- **Python configparser**: No type safety, no validation, cumbersome
- **YAML/JSON files**: No type safety, validation requires custom code
- **os.environ directly**: No type safety, no validation, scattered throughout code
- **Custom config class**: Reinventing the wheel, less robust
- **django-settings style**: Too tightly coupled to Django patterns

## Advantages
- Type-safe configuration with IDE autocomplete
- Automatic validation on startup (fail fast)
- Environment variable support out of the box
- Clear default values for all settings
- Easy to extend with new configuration sections
- Excellent documentation generation

## Disadvantages
- Additional dependency
- Learning curve for team unfamiliar with Pydantic
- Validation errors can be cryptic for complex nested configs

## Future Impact
- Easy to add new configuration sections as features grow
- Type safety prevents configuration errors
- Can generate config documentation automatically
- Environment variable support simplifies deployment variations

## Related Files
- `backend/core/config.py`
- `backend/core/__init__.py`
- `backend/.env.example`

---

# ADR-006: Loguru for Structured Logging

**Date:** 2024-01-01
**Status:** Accepted

## Context
The application needs comprehensive logging for debugging, auditing, and monitoring. Logs need to be structured, rotated, and have different levels for different audiences (developers vs users). The logging system must be easy to configure and performant.

## Decision
Use Loguru for structured logging with rotation and multiple handlers.

## Rationale
- **Simpler API**: More intuitive than Python's built-in logging
- **Structured logging**: Built-in support for structured log formats
- **Rotation**: Built-in log rotation and compression
- **Multiple handlers**: Easy to configure console, file, and error handlers
- **Context binding**: Easy to add context to log messages
- **Performance**: Faster than standard logging
- **Pretty printing**: Excellent console output with colors
- **No boilerplate**: Minimal setup required

## Alternatives Considered
- **Python logging**: Verbose, complex configuration, no rotation out of the box
- **structlog**: Powerful but more complex setup
- **print statements**: No structure, no rotation, no levels
- **Custom logging solution**: Reinventing the wheel

## Advantages
- Simple, intuitive API
- Built-in rotation and compression
- Excellent console output with colors
- Easy to add context to log messages
- Performant
- Minimal boilerplate

## Disadvantages
- Additional dependency
- Less familiar to developers used to standard logging
- Less ecosystem integration than standard logging

## Future Impact
- Logging configuration is centralized and easy to modify
- Easy to add log aggregation later if needed
- Structured logs enable better search and analysis
- Multiple handlers support different use cases (dev vs production)

## Related Files
- `backend/core/logging.py`
- `backend/core/config.py` (LoggingConfig)

---

# ADR-007: Job Queue with Celery (Architecture Only)

**Date:** 2024-01-01
**Status:** Accepted (Implementation Pending)

## Context
Document processing is CPU-intensive and time-consuming (OCR, classification, indexing). The UI must remain responsive during processing. Failed jobs should be retried automatically. Processing should be resumable after application restart.

## Decision
Design job queue architecture using Celery with Redis as broker (to be implemented in v0.2+).

## Rationale
- **Background processing**: Keeps UI responsive during heavy operations
- **Automatic retries**: Built-in retry logic with exponential backoff
- **Progress tracking**: Celery provides task status and progress
- **Resumable**: Tasks can be queued and resumed after restart
- **Scalable**: Can scale workers if needed (though single-worker for desktop)
- **Mature**: Well-tested, extensively used in production
- **Monitoring**: Built-in monitoring and debugging tools

## Alternatives Considered
- **ThreadPoolExecutor**: Simpler but no persistence, no retry logic
- **asyncio + queue**: Complex, no built-in retry or monitoring
- **Custom job queue**: Reinventing the wheel, less robust
- **No job queue**: Process synchronously (blocks UI, no retry)

## Advantages
- Proven, robust solution
- Built-in retry and error handling
- Task status and progress tracking
- Easy to monitor and debug
- Can be disabled for simple deployments

## Disadvantages
- Requires Redis (additional dependency)
- More complex than simple threading
- Overhead for simple use cases
- Redis adds to application footprint

## Future Impact
- Redis must be bundled with application
- Need to handle Redis startup/shutdown
- Can simplify to in-memory queue if Redis proves too heavy
- Job queue enables parallel processing improvements

## Related Files
- `backend/pipeline/job_queue.py` (placeholder)
- `backend/core/config.py` (JobQueueConfig)
- `backend/requirements.txt` (celery, redis)

---

# ADR-008: Non-Destructive File Operations

**Date:** 2024-01-01
**Status:** Accepted

## Context
The application must never modify original documents. All reorganization operations must be undoable. Users must be able to recover from mistakes. File operations must be atomic to prevent corruption.

## Decision
Implement non-destructive file operations with copy-on-write pattern and undo log.

## Rationale
- **Data safety**: Original files never modified
- **Reversible**: Every operation can be undone
- **Atomic**: Write to temp, then rename (no partial states)
- **Audit trail**: All operations logged for compliance
- **User confidence**: Users can experiment without fear
- **Compliance**: Audit trail required for business documents

## Alternatives Considered
- **Direct modification**: Dangerous, no undo capability
- **In-place rename**: Risk of data loss during operations
- **No undo log**: Users cannot recover from mistakes
- **Copy without temp**: Risk of corruption during operation

## Advantages
- Complete data safety
- Full undo capability
- Atomic operations prevent corruption
- Audit trail for compliance
- User confidence and trust

## Disadvantages
- Additional disk space for copies
- Slower operations (copy vs move)
- More complex implementation
- Undo log storage overhead

## Future Impact
- Need to implement undo system with rollback
- Storage management required (cleanup old copies)
- All file operations must use this pattern
- Audit log grows over time (needs cleanup strategy)

## Related Files
- `backend/database/schema.sql` (audit_log, undo_log tables)
- `README.md` (Engineering Rules section)

---

# ADR-009: Full-Text Search with SQLite FTS5

**Date:** 2024-01-01
**Status:** Accepted

## Context
Users need to search across thousands of documents by content, filename, metadata, and extracted fields. Search must be fast (<100ms) and support ranking/relevance. The search must work completely offline.

## Decision
Use SQLite FTS5 (Full-Text Search) extension for search functionality.

## Rationale
- **Built-in**: FTS5 is part of SQLite, no external dependency
- **Fast**: Optimized for full-text search with BM25 ranking
- **Offline**: Works completely offline
- **Triggers**: Automatic sync with document updates
- **Ranking**: Built-in relevance ranking
- **Tokenization**: Unicode support for Indian languages
- **Low overhead**: Minimal storage overhead
- **Mature**: Well-tested, extensively used

## Alternatives Considered
- **Elasticsearch**: Requires external server, overkill for desktop
- **Whoosh**: Less mature, fewer features
- **Application-level search**: Slow, complex to implement ranking
- **DuckDB search**: Not optimized for full-text search
- **No search**: Major UX limitation

## Advantages
- Built into SQLite, no extra dependency
- Fast with excellent ranking
- Automatic sync via triggers
- Unicode support for Indian languages
- Low storage overhead
- Mature and stable

## Disadvantages
- Limited to SQLite scale (acceptable for this use case)
- Fewer advanced features than Elasticsearch
- Custom ranking requires more work

## Future Impact
- Search index maintained automatically via triggers
- Can add custom ranking functions if needed
- If scale exceeds SQLite, can migrate to Elasticsearch
- FTS5 configuration may need tuning for performance

## Related Files
- `backend/database/schema.sql` (fts_documents table and triggers)

---

# ADR-010: Pluggy for Plugin System

**Date:** 2024-01-01
**Status:** Accepted (Implementation Pending)

## Context
The application needs an extensible architecture for document extractors, classifiers, and validators. Users may want to add custom extractors for proprietary formats. The plugin system must be simple, well-documented, and type-safe.

## Decision
Use Pluggy framework for plugin system (to be implemented in v0.3+).

## Rationale
- **Proven**: Used by pytest, well-tested
- **Simple**: Easy to understand and implement
- **Hook-based**: Clear hook specification
- **Type-safe**: Can be combined with type hints
- **Discovery**: Automatic plugin discovery
- **Documentation**: Well-documented with examples
- **Lightweight**: Minimal overhead

## Alternatives Considered
- **Custom plugin system**: Reinventing the wheel
- **Entry points**: More complex, less flexible
- **Dynamic imports**: No structure, hard to document
- **No plugin system**: No extensibility

## Advantages
- Proven, well-tested solution
- Simple hook-based API
- Automatic plugin discovery
- Easy to document
- Lightweight

## Disadvantages
- Additional dependency
- Hook naming must be carefully designed
- Plugin errors can be hard to debug

## Future Impact
- Need to design hook specifications carefully
- Plugin documentation critical for usability
- Need plugin testing strategy
- Can add plugin marketplace later

## Related Files
- `backend/plugins/__init__.py` (placeholder)
- `backend/core/base.py` (BasePlugin)
- `backend/requirements.txt` (pluggy)

---

# ADR-011: TypeScript Strict Mode

**Date:** 2024-01-01
**Status:** Accepted

## Context
The frontend is written in TypeScript to catch errors at compile time. The application is complex with many components and interactions. Type safety is critical for preventing runtime errors.

## Decision
Enable TypeScript strict mode with comprehensive type definitions.

## Rationale
- **Type safety**: Catches errors at compile time
- **Better IDE support**: Excellent autocomplete and refactoring
- **Self-documenting**: Types serve as documentation
- **Refactoring confidence**: Can safely rename and refactor
- **Fewer runtime errors**: Many bugs caught at compile time
- **Better collaboration**: Types serve as contract between components

## Alternatives Considered
- **JavaScript**: No type safety, more runtime errors
- **TypeScript with loose mode**: Less type safety, defeats purpose
- **JSDoc**: Less powerful, harder to maintain
- **Flow**: Less popular, harder to hire developers

## Advantages
- Maximum type safety
- Excellent IDE support
- Self-documenting code
- Refactoring confidence
- Fewer runtime errors

## Disadvantages
- Learning curve for team unfamiliar with TypeScript
- More verbose code
- Longer compile times
- Some JavaScript libraries lack type definitions

## Future Impact
- All new code must include type definitions
- Need to maintain type definitions for all modules
- Refactoring is safer and easier
- Onboarding requires TypeScript knowledge

## Related Files
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`
- `frontend/src/vite-env.d.ts`

---

# ADR-012: Black, Flake8, Mypy, isort for Python Quality

**Date:** 2024-01-01
**Status:** Accepted

## Context
The Python backend must maintain high code quality across multiple contributors. Code should be consistently formatted, linted, and type-checked. These tools should be integrated into the development workflow.

## Decision
Use Black for formatting, Flake8 for linting, Mypy for type checking, and isort for import sorting.

## Rationale
- **Black**: Uncompromising code formatter, no style debates
- **Flake8**: Comprehensive linting with many plugins
- **Mypy**: Static type checking for Python
- **isort**: Consistent import ordering
- **Pre-commit hooks**: Automatic quality checks before commit
- **Industry standard**: Widely used and well-understood
- **IDE integration**: Excellent support in all major IDEs

## Alternatives Considered
- **Autopep8**: Less strict, more configurable (more debates)
- **Pylint**: More complex, slower
- **No type checking**: More runtime errors
- **Manual formatting**: Inconsistent, time-consuming
- **Custom tools**: Reinventing the wheel

## Advantages
- Consistent code style across project
- Automatic quality checks
- Type safety catches errors early
- No style debates (Black is opinionated)
- Pre-commit hooks enforce quality
- Industry-standard tools

## Disadvantages
- Additional dependencies
- Build time increased (type checking)
- Learning curve for team
- Some false positives in linting

## Future Impact
- All code must pass these tools
- Pre-commit hooks enforce quality
- CI/CD should run these checks
- Team must learn these tools
- Code reviews focus on logic, not style

## Related Files
- `backend/pyproject.toml` (tool configurations)
- `backend/.flake8`
- `backend/.mypy.ini`
- `.pre-commit-config.yaml`

---

# ADR-013: Pytest with Coverage for Testing

**Date:** 2024-01-01
**Status:** Accepted

## Context
The application requires comprehensive testing to ensure reliability. Tests should be easy to write, run, and maintain. Coverage metrics help ensure critical paths are tested.

## Decision
Use Pytest with pytest-cov for testing and coverage measurement.

## Rationale
- **Simple**: Intuitive API, less boilerplate than unittest
- **Powerful**: fixtures, parametrization, plugins
- **Coverage**: Built-in coverage measurement
- **Async support**: pytest-asyncio for async tests
- **Discovery**: Automatic test discovery
- **Plugins**: Extensive plugin ecosystem
- **Industry standard**: Widely used, well-documented

## Alternatives Considered
- **unittest**: More verbose, less powerful
- **nose2**: Less maintained, fewer features
- **doctest**: Limited to simple tests
- **No testing**: Unacceptable for production code

## Advantages
- Simple, intuitive API
- Powerful fixtures and parametrization
- Built-in coverage measurement
- Excellent async support
- Extensive plugin ecosystem
- Industry standard

## Disadvantages
- Additional dependency
- Learning curve for team unfamiliar with pytest
- Plugin ecosystem can be overwhelming

## Future Impact
- All features must have tests
- Coverage targets enforced in CI/CD
- Test structure must be maintained
- Fixtures should be shared and reused

## Related Files
- `backend/pyproject.toml` (pytest configuration)
- `backend/tests/conftest.py`
- `backend/tests/test_config.py`

---

# ADR-014: Vite for Frontend Build System

**Date:** 2024-01-01
**Status:** Accepted

## Context
The React frontend needs a fast development server, optimized production builds, and support for TypeScript. The build system should be modern, fast, and well-maintained.

## Decision
Use Vite as the frontend build system.

## Rationale
- **Fast**: Native ES modules, instant HMR
- **Modern**: Built on modern web standards
- **TypeScript support**: First-class TypeScript support
- **Optimized builds**: Excellent production optimization
- **Plugin ecosystem**: Extensive plugin support
- **Simple configuration**: Minimal config required
- **Industry trend**: Increasingly popular, replacing Webpack

## Alternatives Considered
- **Webpack**: Slower, more complex configuration
- **Parcel**: Less flexible, fewer plugins
- **Rollup**: Lower-level, more complex
- **No build system**: Not feasible for TypeScript/React

## Advantages
- Fast development server with HMR
- Excellent TypeScript support
- Optimized production builds
- Simple configuration
- Extensive plugin ecosystem
- Modern and actively developed

## Disadvantages
- Newer than Webpack (less battle-tested)
- Fewer learning resources than Webpack
- Some plugins not yet available

## Future Impact
- Build configuration is simple and maintainable
- Fast development cycle
- Easy to add plugins as needed
- May need to migrate plugins if ecosystem changes

## Related Files
- `frontend/vite.config.ts`
- `frontend/package.json`
- `frontend/tsconfig.json`

---

# ADR-015: Confidence Scores for All Extracted Data

**Date:** 2024-01-01
**Status:** Accepted

## Context
Document extraction (OCR, AI, pattern matching) is never 100% accurate. Users need to know which data is reliable and which requires manual review. Low-confidence data should be flagged for human verification.

## Decision
Include confidence scores (0.0-1.0) for all extracted metadata fields.

## Rationale
- **Transparency**: Users know data reliability
- **Review workflow**: Low-confidence data flagged for review
- **Thresholds**: Can set confidence thresholds for automation
- **AI explainability**: Users understand system decisions
- **Quality improvement**: Can measure and improve extraction accuracy
- **Compliance**: Audit trail includes confidence levels

## Alternatives Considered
- **Binary reliable/unreliable**: Too coarse, loses nuance
- **No confidence scores**: Users can't judge reliability
- **Confidence only for AI**: Inconsistent, all extraction should have it
- **Manual review only**: Too time-consuming for all data

## Advantages
- Users understand data reliability
- Enables automated review workflows
- Supports confidence-based automation
- Improves system transparency
- Enables quality measurement

## Disadvantages
- Additional storage for confidence values
- More complex extraction logic
- UI must display confidence scores
- Need to define confidence calculation methods

## Future Impact
- All extractors must return confidence scores
- Database schema includes confidence column
- UI must display confidence information
- Need to define review thresholds
- Can use confidence for model improvement

## Related Files
- `backend/database/schema.sql` (metadata.confidence column)
- `backend/core/base.py` (BaseResult)
- `README.md` (AI/ML Guidelines section)

---

# ADR-016: Reversible Database Migrations

**Date:** 2024-01-01
**Status**: Accepted

## Context
The database schema will evolve over time. Migrations must be safe, reversible, and tested. Users may need to downgrade versions. Migration failures must not corrupt data.

## Decision
Implement reversible database migrations with rollback support.

## Rationale
- **Safety**: Migrations can be rolled back if they fail
- **Testing**: Can test rollback procedures
- **Version control**: Users can upgrade and downgrade
- **No data loss**: Rollback ensures data integrity
- **Compliance**: Audit trail requires version control
- **Production safety**: Ability to revert bad migrations

## Alternatives Considered
- **Irreversible migrations**: Risk of data loss, no rollback
- **Manual SQL scripts**: Error-prone, no rollback support
- **No migrations**: Cannot evolve schema safely
- **External migration tools**: Additional complexity

## Advantages
- Safe schema evolution
- Rollback capability
- Version control for database
- Data integrity guarantees
- Production safety

## Disadvantages
- More complex migration logic
- Additional testing required
- Some schema changes are inherently irreversible
- Slower migration process

## Future Impact
- All schema changes need migration
- Must test both upgrade and rollback
- Some changes may be irreversible (acknowledge in migration)
- Migration scripts must be carefully maintained

## Related Files
- `backend/database/migrations/` (structure)
- `backend/database/schema.sql` (initial schema)
- `README.md` (Engineering Rules section)

---

# ADR-017: PyBridge IPC Protocol (To Be Designed)

**Date:** 2024-01-01
**Status**: Accepted (Protocol Design Pending)

## Context
Communication between Electron (JavaScript) and Python must be reliable, type-safe, and versioned. The protocol must handle different message types (commands, responses, progress updates, errors).

## Decision
Design PyBridge IPC protocol with message type safety and versioning (to be implemented in v0.2).

## Rationale
- **Type safety**: Messages validated on both sides
- **Versioning**: Protocol can evolve without breaking
- **Reliability**: Error handling and acknowledgment
- **Performance**: Binary serialization for efficiency
- **Debugging**: Easy to log and inspect messages
- **Testing**: Can mock protocol for testing

## Alternatives Considered
- **JSON strings**: No type safety, parsing overhead
- **Custom binary protocol**: Complex, error-prone
- **gRPC**: Overkill for local IPC
- **No protocol**: Informal, error-prone

## Advantages
- Type-safe communication
- Protocol versioning
- Easy to debug
- Good performance
- Testable

## Disadvantages
- Protocol design complexity
- Versioning adds complexity
- Need to maintain protocol docs
- Both sides must implement protocol

## Future Impact
- Protocol must be carefully designed
- Versioning strategy critical
- Need protocol documentation
- Breaking changes require careful handling

## Related Files
- `frontend/electron/preload.ts` (IPC placeholder)
- `backend/core/config.py` (IPCConfig)

---

# ADR-018: Module-Based Folder Structure

**Date:** 2024-01-01
**Status**: Accepted

## Context
The backend has many distinct components (scanner, extractor, classifier, etc.). The folder structure must support clear separation of concerns, easy navigation, and independent module compilation.

## Decision
Use module-based folder structure with clear separation of concerns.

## Rationale
- **Separation of concerns**: Each module has single responsibility
- **Independent compilation**: No circular dependencies
- **Easy navigation**: Clear structure for developers
- **Scalable**: Easy to add new modules
- **Testing**: Each module can be tested independently
- **Onboarding**: New developers can understand structure quickly

## Alternatives Considered
- **Layered architecture**: More complex, harder to navigate
- **Feature-based folders**: Can lead to code duplication
- **Monolithic structure**: Hard to maintain and scale
- **No structure**: Unmaintainable

## Advantages
- Clear separation of concerns
- Easy to navigate and understand
- Independent module compilation
- Scalable and maintainable
- Easy to test individual modules

## Disadvantages
- More folders to navigate
- Need to enforce boundaries
- Can lead to over-engineering
- More imports across modules

## Future Impact
- Must enforce module boundaries
- New features should fit existing structure
- Avoid circular dependencies
- Structure may need refactoring as project grows

## Related Files
- `PROJECT_STRUCTURE.md`
- Backend folder structure (core, scanner, extractor, classifier, etc.)

---

# ADR-019: Environment-Based Configuration

**Date:** 2024-01-01
**Status**: Accepted

## Context
Configuration varies between development, testing, and production. Some settings are sensitive (database paths, API keys) and should not be committed. Configuration must be easy to change without code changes.

## Decision
Use environment variables and .env files for configuration management.

## Rationale
- **Security**: Sensitive data not in code
- **Flexibility**: Easy to change without code changes
- **Environments**: Different configs for dev/test/prod
- **No commits**: .env in .gitignore
- **Standard**: Industry-standard practice
- **Easy deployment**: Config changes don't require rebuild

## Alternatives Considered
- **Hard-coded values**: Security risk, inflexible
- **Config files in repo**: Security risk, hard to manage environments
- **Command-line args**: Hard to manage many settings
- **Database config**: Overkill for simple config

## Advantages
- Sensitive data not in code
- Easy to change without code changes
- Environment-specific configs
- Industry standard
- Easy deployment

## Disadvantages
- Need to document all env variables
- .env files must be created manually
- Harder to debug missing env vars
- Some IDEs don't auto-complete env vars

## Future Impact
- Must document all environment variables
- .env.example must be kept up to date
- New settings should use env vars
- Need to validate env vars on startup

## Related Files
- `backend/.env.example`
- `backend/core/config.py`
- `frontend/.env.example`

---

# ADR-020: OCR Strategy (Deferred to v0.2)

**Date:** 2024-01-01
**Status**: Accepted (Implementation Deferred)

## Context
Scanned documents and images require OCR to extract text. OCR is CPU-intensive and may have varying accuracy for different languages and document types. The system needs to handle OCR failures gracefully.

## Decision
Use Tesseract OCR with confidence scoring and fallback strategies (to be implemented in v0.2).

## Rationale
- **Open source**: Tesseract is free and widely used
- **Multi-language**: Supports Indian languages (Hindi, Tamil, etc.)
- **Mature**: Well-tested, extensively used
- **Confidence scores**: Can assess OCR quality
- **Offline**: Works completely offline
- **Extensible**: Can add alternative OCR engines later

## Alternatives Considered
- **Cloud OCR (AWS, Google)**: Requires internet, not offline
- **ABBYY**: Commercial, expensive
- **No OCR**: Cannot process scanned documents
- **Custom OCR**: Too complex, reinventing wheel

## Advantages
- Open source and free
- Multi-language support
- Confidence scoring
- Offline operation
- Mature and stable

## Disadvantages
- Accuracy varies by document type
- CPU-intensive
- Requires Tesseract installation
- May need language packs

## Future Impact
- Need to handle OCR failures gracefully
- Confidence threshold for manual review
- May need alternative OCR engines
- Language pack management
- Performance optimization may be needed

## Related Files
- `backend/core/config.py` (OCRConfig)
- `backend/requirements.txt` (pytesseract, pyocr)
- `README.md` (OCR strategy section)

---

# Open Decisions

The following architectural decisions have NOT been finalized and will be made in future milestones:

## OCR-001: Alternative OCR Engines
**Status**: Pending (v0.2)
**Options**: Tesseract only, Tesseract + EasyOCR, Tesseract + cloud OCR fallback
**Decision Point**: When implementing OCR in v0.2

## AI-001: AI/ML Integration Strategy
**Status**: Pending (v0.2-v0.5)
**Options**: scikit-learn only, PyTorch, TensorFlow, ONNX, no ML (rule-based only)
**Decision Point**: When implementing classification in v0.2

## SEARCH-001: Search Ranking Algorithm
**Status**: Pending (v0.2)
**Options**: BM25 only, BM25 + custom ranking, ML-based ranking, user feedback loop
**Decision Point**: When implementing search UI in v0.2

## INDEX-001: Incremental Indexing Strategy
**Status**: Pending (v0.2)
**Options**: File system watching, periodic re-scan, hash-based change detection, hybrid
**Decision Point**: When implementing scanner in v0.2

## DB-001: Database Optimization Strategy
**Status**: Pending (v0.3)
**Options**: SQLite only, SQLite + DuckDB, SQLite + PostgreSQL, SQLite + materialized views
**Decision Point**: When performance issues arise (v0.3+)

## PLUGIN-001: Plugin Distribution Strategy
**Status**: Pending (v0.3)
**Options**: Local plugins only, plugin marketplace, npm-style registry, custom repository
**Decision Point**: When implementing plugin system in v0.3

## AUTH-001: Authentication Strategy (If Ever Added)
**Status**: Pending (v1.0+)
**Options**: No auth, local file-based auth, LDAP integration, OAuth, custom auth
**Decision Point**: If multi-user support is added (v1.0+)

## UPDATE-001: Update Mechanism
**Status**: Pending (v1.0)
**Options**: Manual download, auto-update with electron-updater, differential updates, no auto-update
**Decision Point**: When preparing for production release (v1.0)

## PACKAGE-001: Cross-Platform Packaging Details
**Status**: Pending (v1.0)
**Options**: Single installer per platform, universal binary, container-based, app store distribution
**Decision Point**: When preparing for production release (v1.0)

## VALIDATION-001: GST Validation Data Source
**Status**: Pending (v0.4)
**Options**: No validation, offline GSTIN database, online GST portal API, hybrid approach
**Decision Point**: When implementing GST validation in v0.4

## PERF-001: Large File Processing Strategy
**Status**: Pending (v0.2)
**Options**: Load entire file, stream processing, chunked processing, memory-mapped files
**Decision Point**: When implementing document processing in v0.2

---

# Decision Revisit Roadmap

The following milestones may require revisiting existing decisions:

## v0.2 - Intelligence
- **Revisit ADR-017**: Finalize PyBridge IPC protocol design
- **Revisit ADR-007**: Implement and evaluate Celery job queue
- **Revisit ADR-020**: Implement OCR and evaluate accuracy
- **Finalize OPEN-001 through OPEN-005**: OCR, AI, search, indexing decisions
- **Revisit ADR-021**: Verify security improvements with persistence layer
- **Implement HIGH-001 through HIGH-012**: Security improvements with Repository pattern

## v0.3 - Organization
- **Revisit ADR-010**: Implement and evaluate plugin system
- **Finalize OPEN-006**: Plugin distribution strategy
- **Revisit ADR-008**: Implement undo system and evaluate storage impact

## v0.4 - Validation
- **Revisit ADR-004**: Implement DuckDB and evaluate performance
- **Finalize OPEN-009**: GST validation data source
- **Revisit ADR-009**: Evaluate FTS5 performance for large datasets

## v0.5 - Analytics
- **Revisit ADR-004**: Full DuckDB integration and evaluation
- **Revisit ADR-003**: Evaluate SQLite performance for operational queries
- **Finalize OPEN-007**: Database optimization strategy

## v1.0 - Platform
- **Revisit ADR-001**: Evaluate Electron performance and consider alternatives
- **Finalize OPEN-008 through OPEN-010**: Auth, update, packaging decisions
- **Revisit all major ADRs**: Final evaluation before production release

---

# ADR-021: Security Improvements Based on Red Team Review

**Date:** 2024-01-01
**Status:** Accepted

## Context
A comprehensive Red Team security review identified 8 critical, 12 high, 15 medium, and 8 low security vulnerabilities in the v0.1 foundation. The review covered authentication, IPC communication, database operations, file system access, input validation, logging, dependencies, error handling, and frontend security.

## Decision
Implement 4 critical security improvements immediately and document architectural trade-offs for rejected recommendations. Defer remaining improvements to future milestones when relevant functionality is added.

## Rationale
### Implemented Improvements
1. **Path Traversal Protection**: Replaced string prefix matching with proper path validation using `Path.relative_to()`, symlink detection, and parent directory reference detection. This prevents symlink attacks and path escape attempts.
2. **SQL Injection Prevention**: Added schema SQL validation to block dangerous statements (ATTACH DATABASE, LOAD EXTENSION, etc.) while allowing safe statements for initial schema. Added transaction with rollback for atomicity.
3. **IPC Schema Validation**: Implemented Pydantic models for IPC commands and responses with type checking, size limits, and field validation. Prevents type confusion attacks and memory exhaustion.
4. **IPC Channel Allow-Listing**: Restricted Electron IPC channels to an explicit allowlist, preventing renderer process from accessing system-level channels or arbitrary operations.

### Rejected Recommendations
1. **IPC Authentication**: Rejected because CRMS is a single-user desktop application with local IPC. An attacker with local access already has full system access. Authentication adds complexity without security benefit for this threat model.
2. **IPC Rate Limiting**: Rejected because the backend serves a single Electron frontend. Rate limiting is designed for multi-client scenarios and adds overhead for a single-client system.
3. **Database Encryption**: Postponed to commercial releases (v1.0+). For single-user offline desktop application, encryption provides marginal benefit and adds complexity. Will be required for commercial releases.
4. **Secrets Management**: Rejected because the current architecture has no secrets (no API keys, passwords, or tokens). Environment variables are sufficient for non-sensitive configuration. Will be added when external APIs are integrated.

### Deferred Recommendations
- HIGH-001 through HIGH-012: Deferred to Milestone 2 when relevant functionality (Repository pattern, Unit of Work, file operations, etc.) is implemented.
- MEDIUM and LOW findings: Deferred to future milestones when relevant features are added.

## Alternatives Considered
- **Implement all critical findings**: Would delay Milestone 2 for features that are architectural trade-offs (authentication, rate limiting, encryption, secrets management)
- **Implement no security improvements**: Would leave critical vulnerabilities unaddressed
- **Implement all findings immediately**: Would add significant complexity and dependencies premature for v0.1 foundation

## Advantages
- Addresses most critical vulnerabilities for current threat model
- Documents architectural trade-offs with clear reasoning
- Provides clear roadmap for future security improvements
- Maintains development velocity for Milestone 2
- Security score improved from 5.5/10 to 6.5/10

## Disadvantages
- Some critical findings rejected (authentication, rate limiting) based on architectural assumptions
- Database encryption postponed (may affect commercial release timeline)
- Security improvements fragmented across milestones

## Future Impact
- Security improvements will be implemented incrementally with each milestone
- Database encryption must be implemented before commercial release (v1.0)
- Authentication and rate limiting must be added if application becomes multi-user or network-accessible
- Secrets management must be added when external APIs are integrated
- Security review should be repeated after each milestone

## Security Score Update
- **Before:** 5.5/10 (8 critical, 12 high, 15 medium, 8 low)
- **After:** 6.5/10 (4 critical rejected, 12 high deferred, 15 medium deferred, 8 low deferred)
- **Acceptable for v0.1 foundation:** ✅

## Related Files
- `SECURITY_DECISIONS.md` - Detailed security decisions and reasoning
- `RED_TEAM_SECURITY_REVIEW.md` - Original security review findings
- `backend/database/connection.py` - Path traversal and SQL injection fixes
- `backend/main.py` - IPC schema validation
- `frontend/electron/preload.ts` - IPC channel allow-listing

---

# Appendix: Decision Categories

## Architecture Decisions
- ADR-001: Electron + React Desktop Application
- ADR-002: Python Backend with Direct IPC
- ADR-003: SQLite as Primary Database
- ADR-004: DuckDB for Analytics
- ADR-007: Job Queue with Celery
- ADR-018: Module-Based Folder Structure

## Data Decisions
- ADR-008: Non-Destructive File Operations
- ADR-009: Full-Text Search with SQLite FTS5
- ADR-015: Confidence Scores for All Extracted Data
- ADR-016: Reversible Database Migrations

## Development Decisions
- ADR-005: Pydantic for Configuration Management
- ADR-006: Loguru for Structured Logging
- ADR-011: TypeScript Strict Mode
- ADR-012: Black, Flake8, Mypy, isort for Python Quality
- ADR-013: Pytest with Coverage for Testing
- ADR-014: Vite for Frontend Build System
- ADR-019: Environment-Based Configuration

## Communication Decisions
- ADR-017: PyBridge IPC Protocol

## Security Decisions
- ADR-021: Security Improvements Based on Red Team Review

## Extensibility Decisions
- ADR-010: Pluggy for Plugin System

## Processing Decisions
- ADR-020: OCR Strategy

---

This document is a living record of architectural decisions. New ADRs should be added as decisions are made, and existing ADRs should be updated if decisions are revised.
