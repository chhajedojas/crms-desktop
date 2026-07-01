# Changelog

All notable changes to CRMS (Company Records Management System) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- MIT License for open-source distribution

## [0.1.0] - 2024-01-01

### Added
- Complete project foundation and architecture
- Python 3.11+ backend with modular structure
- React + TypeScript + Electron frontend
- SQLite database with comprehensive schema (15+ tables)
- FTS5 full-text search integration
- Configuration management with Pydantic
- Structured logging with Loguru
- Testing infrastructure with pytest
- Code quality tools (black, flake8, mypy, isort)
- Pre-commit hooks configuration
- Architectural Decision Records (20 ADRs)
- Comprehensive documentation (README, ARCHITECTURE, ROADMAP, etc.)
- Database initialization script
- Placeholder modules for scanner, extractor, classifier, pipeline, validation

### Changed
- Migrated from FastAPI to direct IPC for Electron-Python communication
- Used SQLite instead of PostgreSQL for embedded database
- Temporarily disabled DuckDB due to build issues on macOS ARM64

### Security
- No hardcoded secrets or API keys
- Parameterized database queries
- Path validation in configuration
- Proper error handling without sensitive data exposure

### Documentation
- README with engineering rules and performance targets
- ARCHITECTURE.md with system design
- DATABASE_SCHEMA.sql with complete table definitions
- PROJECT_STRUCTURE.md with folder layout
- DECISIONS.md with architectural decisions
- DEVELOPMENT_STATUS.md with current status
- ROADMAP.md with development timeline
- CHANGELOG.md (this file)

### Testing
- 8 configuration tests passing (72% coverage)
- Test infrastructure configured for future growth

## [0.0.0] - 2024-01-01

### Added
- Initial project creation
- Repository structure
- Git initialization

---

## Version Summary

### v0.1.x - Foundation
Focus on establishing production-quality foundation, configuration, and infrastructure.

### v0.2.x - Intelligence
Focus on document scanning, metadata extraction, OCR, classification, and search.

### v0.3.x - Organization
Focus on reorganization, undo system, and plugin architecture.

### v0.4.x - Validation
Focus on GST validation, sequence detection, relationship mapping, and bank reconciliation.

### v0.5.x - Analytics
Focus on DuckDB integration, timelines, dashboard, and advanced reporting.

### v1.0.x - Platform
Focus on AI features, production packaging, and complete documentation.

---

## Categories

The following categories are used in this changelog:

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities or improvements
- **Performance**: Performance improvements
- **Documentation**: Documentation changes
- **Testing**: Test changes
- **Infrastructure**: Build system, CI/CD, dependencies

---

## How to Update This Changelog

When making changes to CRMS:

1. Add entries to the `[Unreleased]` section
2. Use the categories listed above
3. Be specific about what changed
4. Include migration notes if breaking changes
5. When releasing, create a new version section and move entries

### Example Entry

```markdown
## [Unreleased]

### Added
- PDF metadata extractor with confidence scoring
- Support for Excel .xlsx files
- OCR integration with Tesseract

### Changed
- Improved database query performance by adding indexes
- Updated Pydantic to 2.6.0

### Fixed
- Fixed memory leak in document scanner
- Fixed OCR confidence calculation

### Migration Notes
- Database migration required: run `python scripts/migrate.py`
```

---

## Links

- [Repository](https://github.com/chhajedojas/crms-ai-document-intelligence)
- [Issues](https://github.com/chhajedojas/crms-ai-document-intelligence/issues)
- [Releases](https://github.com/chhajedojas/crms-ai-document-intelligence/releases)
