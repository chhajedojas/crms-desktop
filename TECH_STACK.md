# Technology Stack

This document outlines the complete technology stack used in CRMS (Company Records Management System).

## Backend

### Core Language
- **Python 3.11+**
  - Type hints for better code quality
  - Async support for future concurrency
  - Extensive library ecosystem

### Frameworks & Libraries

#### Configuration
- **Pydantic 2.5.0** - Data validation and settings management
- **pydantic-settings 2.1.0** - Environment variable configuration

#### Database
- **SQLite 3** - Embedded operational database
  - FTS5 for full-text search
  - ACID compliant
  - Zero configuration
- **SQLAlchemy 2.0.23** - ORM (planned for future use)
- **aiosqlite 0.19.0** - Async SQLite driver (planned)

#### Document Processing
- **PyPDF2 3.0.1** - PDF text extraction
- **pdfplumber 0.10.3** - Advanced PDF processing
- **openpyxl 3.1.2** - Excel file processing
- **pandas 2.1.3** - Data manipulation and analysis
- **python-docx 1.1.0** - Word document processing
- **Pillow 10.1.0** - Image processing

#### OCR
- **pytesseract 0.3.10** - Tesseract OCR wrapper
- **pyocr 0.8** - Multi-engine OCR interface
- **Tesseract OCR** - System package for OCR engine

#### Classification & ML
- **scikit-learn 1.3.2** - Machine learning library
- **numpy 1.26.2** - Numerical computing

#### Job Queue
- **Celery 5.3.4** - Distributed task queue
- **redis 5.0.1** - Message broker and cache

#### Reporting
- **xlsxwriter 3.1.9** - Excel report generation

#### Plugin System
- **pluggy 1.3.0** - Plugin framework

#### Utilities
- **python-multipart 0.0.6** - Multipart form data
- **python-dateutil 2.8.2** - Date/time utilities
- **pytz 2023.3** - Timezone support

#### Logging
- **loguru 0.7.2** - Structured logging

#### Configuration
- **python-dotenv 1.0.0** - Environment variable loading

### Testing
- **pytest 7.4.3** - Testing framework
- **pytest-asyncio 0.21.1** - Async test support
- **pytest-cov 4.1.0** - Coverage reporting
- **httpx 0.25.2** - HTTP client for testing

### Code Quality
- **black 23.11.0** - Code formatter
- **flake8 6.1.0** - Linter
- **isort 5.12.0** - Import sorter
- **mypy 1.7.1** - Static type checker
- **types-python-dateutil 2.8.19.14** - Type stubs

### Development Tools
- **pre-commit** - Git hooks for quality checks

## Frontend

### Core Framework
- **React 18.2.0** - UI library
- **TypeScript 5.2.2** - Type-safe JavaScript
- **Vite 5.0.0** - Build tool and dev server

### Electron
- **Electron** - Desktop application framework
  - Main process: Node.js
  - Renderer process: Chromium

### State Management
- **Redux Toolkit** (planned) - State management
- **React Query** (planned) - Server state management

### UI Components
- **React 18** - Component library
- Custom components (planned)

### Build Tools
- **@vitejs/plugin-react 4.2.0** - Vite React plugin
- **Vite 5.0.0** - Build tool

### Code Quality
- **ESLint 8.53.0** - Linter
- **@typescript-eslint/eslint-plugin 6.10.0** - TypeScript linting
- **@typescript-eslint/parser 6.10.0** - TypeScript parser
- **eslint-plugin-react-hooks 4.6.0** - React hooks linting
- **eslint-plugin-react-refresh 0.4.4** - React refresh linting
- **Prettier 3.1.0** - Code formatter

### Testing
- **Vitest 1.0.0** - Unit testing framework
- **React Testing Library** (planned) - Component testing

## Database

### Operational Database
- **SQLite 3**
  - Version: Latest stable
  - Features:
    - FTS5 full-text search
    - Foreign key constraints
    - Triggers for automatic updates
    - WAL mode for performance
    - Size: < 500 MB for 10,000 documents

### Analytical Database
- **DuckDB** (planned for v0.5)
  - Columnar storage for analytics
  - SQL-compatible
  - Excellent for aggregations

## Integration

### IPC (Inter-Process Communication)
- **stdin/stdout** - Primary IPC method
- **PyBridge protocol** (to be designed) - Structured communication

### File System
- **Pathlib** - Cross-platform path handling
- **shutil** - File operations
- **watchdog** (planned) - File system watching

## Packaging

### Electron Packaging
- **electron-builder** - Cross-platform packaging
  - Windows: NSIS installer
  - macOS: DMG
  - Linux: AppImage, deb, rpm

### Python Packaging
- **setuptools** - Python packaging
- **wheel** - Binary distribution format

## Development Environment

### Required Software
- **Python 3.11+**
- **Node.js 18+**
- **Git**
- **Tesseract OCR** (system package)

### IDE Support
- **VS Code** - Recommended
  - Python extension
  - TypeScript/JavaScript extension
  - ESLint extension
  - Prettier extension

### Operating Systems
- **Windows 10/11**
- **macOS 10.15+**
- **Linux** (Ubuntu 20.04+, Debian 11+, Fedora 35+)

## DevOps

### Version Control
- **Git** - Version control
- **GitHub** - Code hosting and CI/CD

### CI/CD
- **GitHub Actions** (planned) - Automated testing and deployment

### Code Quality Automation
- **pre-commit hooks** - Local quality checks
- **GitHub Actions** (planned) - CI/CD pipeline

## Security

### Dependencies
- All packages > 7 days old (security best practice)
- Regular security updates
- Vulnerability scanning (planned)

### Security Tools
- **bandit** (planned) - Python security linter
- **npm audit** - Node.js security audit

## Performance

### Profiling
- **cProfile** - Python profiling
- **React DevTools** - React performance profiling

### Monitoring
- **loguru** - Structured logging
- Custom metrics (planned)

## Documentation

### Documentation Tools
- **Markdown** - Documentation format
- **GitHub** - Documentation hosting
- **Sphinx** (planned) - API documentation

## Architecture Patterns

### Design Patterns
- **Dependency Injection** - Loose coupling
- **Repository Pattern** - Data access abstraction
- **Factory Pattern** - Object creation
- **Strategy Pattern** - Interchangeable algorithms
- **Observer Pattern** - Event-driven updates

### Architectural Principles
- **SOLID** - Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **DRY** - Don't repeat yourself
- **KISS** - Keep it simple, stupid
- **YAGNI** - You aren't gonna need it

## Future Additions

### Potential Technologies
- **FastAPI** - If web API needed later
- **PostgreSQL** - If scale exceeds SQLite
- **Redis** - Caching and job queue
- **Celery Beat** - Scheduled tasks
- **GraphQL** - If flexible API needed
- **Material-UI** - If component library needed
- **Plotly** - Data visualization
- **TensorFlow/PyTorch** - Advanced ML features

### Evaluation Criteria
Before adding new technologies:
- Offline capability
- Cross-platform support
- Active maintenance
- Community support
- Documentation quality
- License compatibility (MIT/BSD preferred)

## Technology Rationale

### Why Python?
- Excellent libraries for data processing
- Strong type support with 3.11+
- Extensive ML ecosystem
- Easy to learn and maintain
- Cross-platform compatibility

### Why React + TypeScript?
- Component-based architecture
- Strong type safety
- Excellent developer experience
- Large ecosystem
- Easy to test

### Why Electron?
- True offline capability
- Cross-platform from single codebase
- Access to native APIs
- Web technology familiarity
- Excellent documentation

### Why SQLite?
- Zero configuration
- Embedded (no external server)
- ACID compliant
- Excellent performance for our scale
- FTS5 for full-text search

### Why Pydantic?
- Type-safe configuration
- Automatic validation
- Excellent IDE support
- Environment variable support
- Active development

## Version Policy

### Python
- Minimum: 3.11
- Recommended: Latest stable (3.12+)
- Update frequency: Monthly

### Node.js
- Minimum: 18
- Recommended: Latest LTS
- Update frequency: Quarterly

### Dependencies
- Update policy: Monthly security updates
- Breaking changes: Major version bumps only
- Deprecation: 6-month notice minimum

## License

All open-source libraries used are compatible with MIT license:
- Permissive licenses (MIT, BSD, Apache 2.0)
- No GPL or AGPL dependencies
- No copyleft restrictions

---

**Last Updated:** 2024-01-01
**Next Review:** Before v0.2 release
