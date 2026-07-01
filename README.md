# CRMS - AI-Powered Document Intelligence Platform

<div align="center">

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-foundation-yellow)

**An offline AI-powered document intelligence platform for Indian businesses**

[Features](#features) • [Installation](#installation) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Overview

CRMS (Company Records Management System) transforms chaotic document repositories into intelligent, searchable, and auditable business intelligence systems—completely offline. Designed for Indian businesses, it handles invoices, delivery challans, bank statements, GST documents, and more with confidence-scored extraction, relationship mapping, and smart reorganization.

![Screenshot Placeholder](#screenshots)

## Features

### Document Intelligence
- **AI-Powered Extraction**: Extract metadata with confidence scores
- **OCR Support**: Process scanned documents and images
- **Multi-Format Support**: PDF, Excel, Word, Images, and more
- **Classification**: Automatic document type classification

### Business Intelligence
- **Relationship Mapping**: Link invoices ↔ delivery challans ↔ payments ↔ ledgers
- **GST Validation**: Automated GST compliance checking
- **Sequence Detection**: Identify missing invoice numbers and gaps
- **Bank Reconciliation**: Match bank statements with payments
- **Duplicate Detection**: Find duplicate invoices and payments

### Organization
- **Smart Reorganization**: Professional folder structures with undo support
- **Migration Plans**: Generate document reorganization plans
- **Undo System**: Complete rollback capability for all operations

### Search & Analytics
- **Full-Text Search**: Instant search across 4000+ documents in <100ms
- **FTS5 Integration**: SQLite FTS5 for fast full-text search
- **Dashboard**: Visual analytics and business insights
- **Reports**: Generate Excel reports for audits and analysis

### Audit & Compliance
- **Audit Trail**: Complete tamper-evident logging of all operations
- **Non-Destructive**: Original documents never modified
- **Offline-First**: Complete offline operation, no internet required

## Technology Stack

### Backend
- **Python 3.11+** with type hints
- **SQLite** with FTS5 for full-text search
- **DuckDB** for analytical queries (v0.5)
- **Pydantic** for configuration management
- **Loguru** for structured logging
- **Celery** for job queue processing

### Frontend
- **React 18** with TypeScript
- **Electron** for desktop application
- **Vite** for build tooling
- **Redux Toolkit** for state management

### Document Processing
- **Tesseract OCR** for text extraction
- **PyPDF2, pdfplumber** for PDF processing
- **openpyxl, pandas** for Excel processing
- **python-docx** for Word processing

For complete technology details, see [TECH_STACK.md](TECH_STACK.md).

## Architecture

CRMS follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Electron Frontend                     │
│              (React + TypeScript + Vite)                 │
└────────────────────┬────────────────────────────────────┘
                     │ IPC (stdin/stdout)
┌────────────────────┴────────────────────────────────────┐
│                    Python Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Scanner    │  │  Extractor   │  │ Classifier   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Search     │  │ Validation   │  │  Pipeline    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │              SQLite + FTS5                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

For detailed architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Installation

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Git**
- **Tesseract OCR** (system package)

#### Installing Tesseract OCR

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**Windows:**
Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/chhajedojas/crms-ai-document-intelligence.git
   cd crms-ai-document-intelligence
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python scripts/init_db.py
   ```

3. **Frontend setup**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Configure environment**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with your settings

   # Frontend
   cd ../frontend
   cp .env.example .env
   # Edit .env with your settings
   ```

## Development

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Testing

**Backend tests:**
```bash
cd backend
pytest tests/ -v --cov
```

**Frontend tests:**
```bash
cd frontend
npm test
```

### Code Quality

**Backend:**
```bash
cd backend
black .      # Format code
flake8 .     # Lint code
mypy core/    # Type checking
```

**Frontend:**
```bash
cd frontend
npm run lint    # Lint code
npm run format  # Format code
```

## Project Structure

```
crms/
├── backend/              # Python backend
│   ├── core/           # Configuration, constants, base classes
│   ├── scanner/        # Document scanning and change detection
│   ├── extractor/      # Metadata extraction
│   ├── classifier/     # Document classification
│   ├── database/       # SQLite schema and migrations
│   ├── pipeline/       # Job queue and processing
│   ├── validation/     # GST validation, sequence detection
│   ├── tests/          # Unit and integration tests
│   └── scripts/        # Utility scripts
├── frontend/           # React + Electron frontend
│   ├── electron/       # Electron main process
│   ├── src/            # React components and logic
│   ├── tests/          # Component tests
│   └── public/         # Static assets
├── samples/            # Sample documents for testing
├── docs/               # Documentation
└── .github/            # CI/CD workflows
```

For detailed structure, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

## Documentation

- [Architecture](ARCHITECTURE.md) - System architecture and design decisions
- [Architecture Review](ARCHITECTURE_REVIEW.md) - Comprehensive architecture review with diagrams
- [Architecture Diagrams](docs/diagrams/) - Mermaid diagrams for system architecture
- [Technology Stack](TECH_STACK.md) - Complete technology overview
- [Database Schema](DATABASE_SCHEMA.sql) - Database schema
- [Roadmap](ROADMAP.md) - Development roadmap
- [Changelog](CHANGELOG.md) - Version history
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines
- [Security](SECURITY.md) - Security policy
- [Development Status](DEVELOPMENT_STATUS.md) - Current development status
- [Architectural Decisions](DECISIONS.md) - ADR documentation

## Roadmap

### v0.1 - Foundation ✅
- Architecture and configuration
- Database schema
- Testing infrastructure
- Code quality tools

### v0.2 - Intelligence (Next)
- Document scanner with change detection
- Metadata extraction (PDF, Excel, Word)
- OCR integration
- Basic classification
- FTS5 search implementation

### v0.3 - Organization
- Reorganization engine
- Undo system
- Plugin system
- Migration plan generation

### v0.4 - Validation
- GST validation
- Sequence detection
- Relationship graph
- Bank reconciliation

### v0.5 - Analytics
- DuckDB integration
- Customer/vendor timelines
- Dashboard UI
- Advanced reports

### v1.0 - Platform
- ML-based classification
- Production packaging
- Complete documentation

See [ROADMAP.md](ROADMAP.md) for details.

## Engineering Rules

CRMS follows strict engineering principles:

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

## Performance Targets

| Operation | Target | Status |
|-----------|--------|--------|
| Initial Scan (5,000 files) | < 3 min | 📋 Planned |
| Incremental Rescan | < 30 sec | 📋 Planned |
| Search Query | < 100 ms | 📋 Planned |
| Reorganization (1,000 files) | < 2 min | 📋 Planned |
| Report Generation | < 30 sec | 📋 Planned |
| Memory Usage | < 1 GB | 📋 Planned |
| Startup Time | < 5 sec | 📋 Planned |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) and [DECISIONS.md](DECISIONS.md)
2. Fork the repository
3. Create a feature branch
4. Write tests for your changes
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See the [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/chhajedojas/crms-ai-document-intelligence/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chhajedojas/crms-ai-document-intelligence/discussions)

## Acknowledgments

- Built with [Python](https://www.python.org/), [React](https://reactjs.org/), and [Electron](https://www.electronjs.org/)
- Document processing powered by [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Database powered by [SQLite](https://www.sqlite.org/) and [DuckDB](https://duckdb.org/)

---

<div align="center">

**Built with ❤️ for Indian businesses**

[⭐ Star](https://github.com/chhajedojas/crms-ai-document-intelligence/stargazers) • [🐛 Report Issue](https://github.com/chhajedojas/crms-ai-document-intelligence/issues) • [📖 Documentation](docs/)

</div>
