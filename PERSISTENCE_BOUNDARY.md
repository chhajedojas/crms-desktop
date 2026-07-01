# Persistence Boundary Documentation

**Date:** 2024-01-01
**Version:** v0.2 - Persistence Layer
**Status:** Clean Architecture Compliant

---

## Overview

This document defines the persistence boundary in the CRMS architecture, ensuring clean separation between the domain layer and the persistence layer. The architecture follows the Dependency Rule: dependencies must only point inward.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
│                  (Electron + React + TypeScript)              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                   Application Layer                       │
│                    (Business Logic - Future)                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                      Domain Layer                          │
│          (Pure Python Entities - No Infrastructure)         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  Persistence Layer                         │
│          (SQLAlchemy ORM + Mappers + Repositories)          │
└─────────────────────────────────────────────────────────┘
```

---

## Dependency Direction

### Critical Rule

**Dependencies must only point inward.**

- **Presentation** → Application → Domain → Persistence
- **Never:** Persistence → Domain → Application → Presentation

### Dependency Graph

```
domain/
    ↓ (imports nothing from infrastructure)
repositories/
    ↓ (imports domain and database.models)
database/
    ↓ (imports SQLAlchemy, sqlite)
infrastructure
```

---

## Domain Layer

### Purpose

The domain layer contains pure Python entities that represent the business model. These entities have no knowledge of infrastructure, databases, or external systems.

### Characteristics

- **Pure Python**: No SQLAlchemy, no database imports, no infrastructure code
- **Dataclasses**: Simple data containers with validation
- **Business Logic**: Contains business rules and validation
- **Independent**: Can be tested without database connection
- **Portable**: Can be used in any context (CLI, API, desktop, web)

### Example

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Document:
    """Document domain entity - pure Python, no database knowledge."""
    id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""
    file_hash: str = ""
    # ... other fields

    def __post_init__(self):
        """Validate business rules."""
        if not self.file_path:
            raise ValueError("file_path is required")
```

### Import Rules

✅ **Allowed:**
- `from dataclasses import dataclass`
- `from datetime import datetime`
- `from typing import Optional, List`
- `from enum import Enum`

❌ **Forbidden:**
- `from sqlalchemy import *`
- `from database.models import *`
- `import sqlite3`
- `import alembic`
- `import fastapi`
- `import electron`

---

## Persistence Layer

### Purpose

The persistence layer handles all database operations using SQLAlchemy ORM. It converts between domain entities and ORM models using mappers.

### Components

#### 1. ORM Models (`database/models.py`)

**Purpose:** SQLAlchemy ORM models that map to database tables.

**Characteristics:**
- Define database schema
- Contain SQLAlchemy-specific code
- Have relationships and constraints
- Are implementation details

**Visibility:** **Internal to persistence layer only**

#### 2. Mappers (`database/mappers.py`)

**Purpose:** Convert between ORM models and domain entities.

**Responsibilities:**
- `to_domain()`: Convert ORM model → Domain entity
- `to_model()`: Convert Domain entity → ORM model
- Handle type conversions (e.g., enum to string)
- Ensure data integrity

**Example:**

```python
class DocumentMapper:
    @staticmethod
    def to_domain(model: DocumentModel) -> Document:
        """Convert ORM to domain - no database knowledge in result."""
        return Document(
            id=model.id,
            file_path=model.file_path,
            # ... other fields
        )

    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        """Convert domain to ORM - for database storage."""
        return DocumentModel(
            id=entity.id,
            file_path=entity.file_path,
            # ... other fields
        )
```

#### 3. Repositories (`repositories/`)

**Purpose:** Provide data access interface using domain entities.

**Critical Rule:** **Repositories must return ONLY domain entities, never ORM models.**

**Why:**
- Business logic should not depend on SQLAlchemy
- Changing database should not affect business logic
- Domain layer remains infrastructure-independent

**Example:**

```python
class DocumentRepository(BaseRepository[Document, DocumentModel]):
    def get_by_id(self, entity_id: int) -> Optional[Document]:
        """Returns Document domain entity, NOT DocumentModel."""
        stmt = select(DocumentModel).where(DocumentModel.id == entity_id)
        orm_entity = self.session.execute(stmt).scalar_one_or_none()
        if orm_entity:
            return self.mapper.to_domain(orm_entity)  # Convert to domain
        return None
```

#### 4. Unit of Work (`repositories/unit_of_work.py`)

**Purpose:** Manage transactions and coordinate repository operations.

**Characteristics:**
- Provides transaction context manager
- Works with repositories that return domain entities
- Ensures atomicity of operations

---

## Anti-Corruption Layer

### What is the Anti-Corruption Layer?

The anti-corruption layer is the mapping layer that prevents the database schema from leaking into the domain model. It ensures that changes to the database or ORM do not affect the domain layer.

### Implementation

```
Domain Entity
    ↓ (to_model)
Mapper
    ↓
ORM Model
    ↓ (SQLAlchemy)
Database
```

And:

```
Database
    ↓ (SQLAlchemy)
ORM Model
    ↓ (to_domain)
Mapper
    ↓
Domain Entity
```

### Benefits

1. **Database Independence:** Changing database schema requires only mapper updates
2. **ORM Flexibility:** Can switch from SQLAlchemy to another ORM with minimal changes
3. **Business Logic Protection:** Domain entities remain pure and unaffected by infrastructure
4. **Testing:** Domain entities can be tested without database setup

---

## Database Portability

### SQLite → PostgreSQL Migration

If we need to change from SQLite to PostgreSQL, **only the persistence layer** changes:

#### What Changes:

1. **Database Connection** (`database/connection.py`)
   ```python
   # Before: SQLite
   db_url = f"sqlite:///{db_path}"
   engine = create_engine(db_url, connect_args={"check_same_thread": False})

   # After: PostgreSQL
   db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
   engine = create_engine(db_url)
   ```

2. **ORM Models** (`database/models.py`)
   - May need PostgreSQL-specific types (e.g., `UUID`, `JSONB`)
   - May need different column types
   - **No domain entities change**

3. **Mappers** (`database/mappers.py`)
   - May need to handle PostgreSQL-specific data types
   - **No domain entities change**

#### What DOES NOT Change:

- ✅ Domain entities (`domain/__init__.py`) - Remain identical
- ✅ Repository interfaces - Remain identical
- ✅ Business logic - Remain identical
- ✅ Application layer - Remain identical
- ✅ Presentation layer - Remain identical

### Verification

To verify database portability, check:

1. **Domain imports:**
   ```bash
   grep -r "sqlalchemy\|alembic\|sqlite\|postgres" domain/
   ```
   Should return nothing.

2. **Repository returns:**
   All repository methods should return domain entities, not ORM models.

3. **Mapper coverage:**
   All ORM models should have corresponding mappers.

---

## Repository Interface

### Public Interface

Repositories expose ONLY domain entities:

```python
# ✅ Correct: Returns domain entity
document = document_repository.get_by_id(1)
print(type(document))  # <class 'domain.Document'>

# ❌ Incorrect: Returns ORM model
document = document_repository.get_by_id(1)
print(type(document))  # <class 'database.models.Document'>
```

### Internal Implementation

Repositories internally use ORM models:

```python
# Internal: Use ORM for database operations
stmt = select(DocumentModel).where(DocumentModel.id == entity_id)
orm_entity = self.session.execute(stmt).scalar_one_or_none()

# External: Return domain entity
return self.mapper.to_domain(orm_entity)
```

---

## Unit of Work

### Purpose

The Unit of Work coordinates multiple repository operations within a single transaction. It works with repositories that return domain entities.

### Usage

```python
with unit_of_work.session_scope() as session:
    doc_repo = DocumentRepository(session)
    metadata_repo = MetadataRepository(session)

    # Create document (returns domain entity)
    document = doc_repo.create(Document(...))

    # Create metadata (returns domain entity)
    metadata = metadata_repo.create(Metadata(...))

    # Transaction commits automatically
```

### Key Point

The Unit of Work does not need to know about ORM models. It only works with repositories that expose domain entities.

---

## Examples

### Reading Data

```python
# Application layer (or wherever business logic lives)
from repositories import DocumentRepository

with db_connection.get_session() as session:
    repo = DocumentRepository(session)
    document = repo.get_by_id(1)  # Returns domain.Document
    # No SQLAlchemy in this code
```

### Writing Data

```python
# Application layer
from repositories import DocumentRepository
from domain import Document

with db_connection.get_session() as session:
    repo = DocumentRepository(session)
    document = Document(file_path="/path/to/file.pdf", ...)
    created = repo.create(document)  # Returns domain.Document
    # No SQLAlchemy in this code
```

---

## Dependency Verification

### Check Domain Layer

```bash
cd backend
grep -r "sqlalchemy\|alembic\|sqlite\|fastapi\|electron" domain/
```

**Expected:** No matches

### Check Repository Returns

```bash
cd backend
grep -A 5 "def get_by_id" repositories/*.py
```

**Expected:** Returns should use `self.mapper.to_domain()`

### Check ORM Model Exposure

```bash
cd backend
cat database/__init__.py
```

**Expected:** Should NOT export ORM models, only DatabaseConnection and exceptions

---

## Benefits of This Architecture

### 1. Database Independence

The domain layer has no knowledge of the database. We can:
- Switch from SQLite to PostgreSQL
- Switch from SQLAlchemy to another ORM
- Change database schema
- All without touching domain entities

### 2. Testability

Domain entities can be tested without database:
```python
def test_document_validation():
    doc = Document(file_path="", file_name="", file_hash="")
    assert doc  # Should raise ValueError
```

### 3. Business Logic Purity

Business logic can use domain entities without knowing about infrastructure:
```python
def process_document(document: Document):
    # Business logic with domain entity
    if document.is_duplicate:
        return "Duplicate"
    return "Process"
```

### 4. Parallel Development

Different teams can work on different layers:
- Domain team: Business rules and validation
- Persistence team: Database optimization
- Presentation team: UI/UX

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Returning ORM Models from Repositories

```python
# Wrong
def get_by_id(self, entity_id: int) -> DocumentModel:
    return self.session.query(DocumentModel).get(entity_id)
```

### ✅ Correct: Return Domain Entities

```python
# Correct
def get_by_id(self, entity_id: int) -> Optional[Document]:
    orm_entity = self.session.query(DocumentModel).get(entity_id)
    return self.mapper.to_domain(orm_entity)
```

### ❌ Mistake 2: Domain Layer Importing Infrastructure

```python
# Wrong
from sqlalchemy import Column, Integer  # In domain/__init__.py
```

### ✅ Correct: Pure Python in Domain

```python
# Correct
from dataclasses import dataclass  # In domain/__init__.py
```

### ❌ Mistake 3: Bypassing Mappers

```python
# Wrong
# Application code using ORM models directly
from database.models import Document
doc = Document(file_path="/path")
```

### ✅ Correct: Use Domain Entities

```python
# Correct
# Application code using domain entities
from domain import Document
doc = Document(file_path="/path")
```

---

## Summary

### Dependency Direction

- **Domain**: Pure Python, no infrastructure dependencies
- **Persistence**: Depends on Domain (uses domain entities)
- **Application**: Depends on Domain (uses domain entities)
- **Presentation**: Depends on Application

### Key Rules

1. ✅ Domain entities are pure Python (no SQLAlchemy, no database imports)
2. ✅ Repositories return domain entities, never ORM models
3. ✅ Mappers convert between ORM and domain entities
4. ✅ ORM models are internal to persistence layer
5. ✅ Unit of Work works with repositories that return domain entities
6. ✅ Changing database requires changes ONLY in persistence layer

### Verification

- ✅ Domain has no infrastructure imports
- ✅ Repositories return domain entities
- ✅ Mappers exist for all ORM models
- ✅ SQLite → PostgreSQL would only change persistence layer

---

**Document Version:** 1.0
**Last Updated:** 2024-01-01
**Next Review:** After any persistence layer changes
