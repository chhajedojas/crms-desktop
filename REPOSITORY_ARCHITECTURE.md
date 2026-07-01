# Repository Architecture Documentation

**Date:** 2024-01-01
**Version:** v0.2 - Persistence Layer
**Status:** Dependency Inversion Compliant

---

## Overview

This document explains the repository architecture in CRMS, including the use of abstract interfaces, dependency inversion, and the benefits for testing, database portability, and future cloud storage support.

---

## Why Interfaces Exist

### 1. Dependency Inversion Principle

The Dependency Inversion Principle (DIP) states:

> High-level modules should not depend on low-level modules. Both should depend on abstractions.

In CRMS:
- **High-level modules:** Application layer (business logic)
- **Low-level modules:** Persistence layer (database implementations)
- **Abstractions:** Repository interfaces

### 2. Decoupling

Without interfaces, the application layer depends directly on concrete repository implementations:

```python
# ❌ Without interfaces - tight coupling
from repositories.document_repository import DocumentRepository

class DocumentService:
    def __init__(self):
        self.doc_repo = DocumentRepository(session)  # Concrete dependency
```

With interfaces, the application layer depends on abstractions:

```python
# ✅ With interfaces - loose coupling
from repositories.interfaces import DocumentRepositoryInterface

class DocumentService:
    def __init__(self, doc_repo: DocumentRepositoryInterface):
        self.doc_repo = doc_repo  # Abstract dependency
```

### 3. Multiple Implementations

Interfaces allow multiple implementations:
- SQLRepository (current SQLAlchemy implementation)
- PostgreSQLRepository (future PostgreSQL implementation)
- CloudStorageRepository (future cloud storage implementation)
- InMemoryRepository (for testing)

All implement the same interface, so the application layer doesn't change.

---

## Dependency Inversion

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                       │
│                  (Business Logic)                         │
│                      ↓                                    │
│              Depends on Interfaces                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                Repository Interfaces                       │
│              (Abstract Definitions)                       │
│                      ↓                                    │
│              Concrete Implementations                      │
└─────────────────────────────────────────────────────────┘
```

### Dependency Direction

**Before (No Interfaces):**
```
Application → Concrete Repository → SQLAlchemy → Database
```

**After (With Interfaces):**
```
Application → Interface ← Concrete Repository → SQLAlchemy → Database
```

The concrete repository depends on the interface, and the application depends on the interface. This is the Dependency Inversion Principle in action.

### Code Example

**Interface Definition:**
```python
class DocumentRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Document]:
        pass

    @abstractmethod
    def create(self, entity: Document) -> Document:
        pass
```

**Concrete Implementation:**
```python
class DocumentRepository(DocumentRepositoryInterface):
    def get_by_id(self, entity_id: int) -> Optional[Document]:
        # SQLAlchemy implementation
        pass

    def create(self, entity: Document) -> Document:
        # SQLAlchemy implementation
        pass
```

**Application Usage:**
```python
class DocumentService:
    def __init__(self, doc_repo: DocumentRepositoryInterface):
        self.doc_repo = doc_repo  # Depends on interface

    def process_document(self, doc_id: int):
        document = self.doc_repo.get_by_id(doc_id)
        # Business logic
```

---

## Testing Advantages

### 1. Mock Implementations

Interfaces allow easy mocking for unit tests:

```python
class MockDocumentRepository(DocumentRepositoryInterface):
    def __init__(self):
        self.documents = []

    def get_by_id(self, entity_id: int) -> Optional[Document]:
        return next((d for d in self.documents if d.id == entity_id), None)

    def create(self, entity: Document) -> Document:
        self.documents.append(entity)
        return entity
```

### 2. Test Without Database

Tests can run without a database connection:

```python
def test_document_service():
    # Use mock repository
    mock_repo = MockDocumentRepository()
    service = DocumentService(mock_repo)

    # Test business logic
    result = service.process_document(1)
    assert result.success
```

### 3. Faster Tests

- No database setup/teardown
- No transaction management
- No connection pooling
- Tests run in milliseconds instead of seconds

### 4. Isolated Tests

Each test is isolated:
- No shared database state
- No test pollution
- Reliable test results

### 5. Test Any Implementation

The same tests work for any implementation:
- SQLAlchemy implementation
- PostgreSQL implementation
- Cloud storage implementation
- Mock implementation

---

## Future PostgreSQL Support

### Current Implementation

Currently, CRMS uses SQLite with SQLAlchemy:

```python
class DocumentRepository(DocumentRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session  # SQLAlchemy session
```

### Future PostgreSQL Implementation

To add PostgreSQL support, we create a new implementation:

```python
class PostgreSQLDocumentRepository(DocumentRepositoryInterface):
    def __init__(self, connection_string: str):
        self.connection = psycopg2.connect(connection_string)

    def get_by_id(self, entity_id: int) -> Optional[Document]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = %s", (entity_id,))
        row = cursor.fetchone()
        return self._row_to_domain(row)
```

### Application Layer Unchanged

The application layer remains unchanged:

```python
# Application code doesn't change
service = DocumentService(doc_repo)  # doc_repo can be any implementation
```

### Configuration-Based Selection

Select implementation based on configuration:

```python
def get_document_repository() -> DocumentRepositoryInterface:
    if settings.database.type == "sqlite":
        return DocumentRepository(session)
    elif settings.database.type == "postgresql":
        return PostgreSQLDocumentRepository(settings.database.connection_string)
    else:
        raise ValueError(f"Unknown database type: {settings.database.type}")
```

### Benefits

1. **No Application Changes:** Application layer unchanged
2. **Gradual Migration:** Can migrate gradually
3. **Parallel Development:** Can develop both implementations in parallel
4. **A/B Testing:** Can test both implementations in production
5. **Rollback:** Can rollback if issues arise

---

## Future Cloud Storage Support

### Use Case

For cloud deployment, documents might be stored in:
- AWS S3
- Azure Blob Storage
- Google Cloud Storage

### Cloud Storage Implementation

Create a cloud storage repository:

```python
class S3DocumentRepository(DocumentRepositoryInterface):
    def __init__(self, s3_client, bucket_name: str):
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    def get_by_id(self, entity_id: int) -> Optional[Document]:
        # Get from S3
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=f"documents/{entity_id}.json"
        )
        data = json.loads(response['Body'].read())
        return Document(**data)

    def create(self, entity: Document) -> Document:
        # Save to S3
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=f"documents/{entity.id}.json",
            Body=json.dumps(asdict(entity))
        )
        return entity
```

### Hybrid Implementation

For hybrid local + cloud storage:

```python
class HybridDocumentRepository(DocumentRepositoryInterface):
    def __init__(self, local_repo: DocumentRepositoryInterface, cloud_repo: DocumentRepositoryInterface):
        self.local_repo = local_repo
        self.cloud_repo = cloud_repo

    def get_by_id(self, entity_id: int) -> Optional[Document]:
        # Try local first, then cloud
        doc = self.local_repo.get_by_id(entity_id)
        if doc:
            return doc
        return self.cloud_repo.get_by_id(entity_id)

    def create(self, entity: Document) -> Document:
        # Save to both
        self.local_repo.create(entity)
        self.cloud_repo.create(entity)
        return entity
```

### Application Layer Unchanged

Again, the application layer remains unchanged:

```python
# Application code doesn't change
service = DocumentService(doc_repo)  # doc_repo can be S3, Azure, or local
```

### Benefits

1. **Seamless Cloud Migration:** Migrate to cloud without application changes
2. **Multi-Cloud Support:** Support multiple cloud providers
3. **Hybrid Deployment:** Run hybrid local + cloud
4. **Disaster Recovery:** Cloud backup of local data
5. **Edge Computing:** Local cache with cloud sync

---

## Dependency Injection

### Constructor Injection

Pass repositories through constructors:

```python
class DocumentService:
    def __init__(self, doc_repo: DocumentRepositoryInterface):
        self.doc_repo = doc_repo
```

### Factory Pattern

Use factories to create repositories:

```python
class RepositoryFactory:
    @staticmethod
    def create_document_repository() -> DocumentRepositoryInterface:
        if settings.database.type == "sqlite":
            return DocumentRepository(session)
        elif settings.database.type == "postgresql":
            return PostgreSQLDocumentRepository(settings.database.connection_string)
        elif settings.storage.type == "s3":
            return S3DocumentRepository(s3_client, settings.storage.bucket)
        else:
            raise ValueError(f"Unknown storage type: {settings.storage.type}")
```

### Service Locator

Use a service locator for more complex scenarios:

```python
class ServiceLocator:
    _instances = {}

    @classmethod
    def register(cls, interface: Type, implementation: Any):
        cls._instances[interface] = implementation

    @classmethod
    def get(cls, interface: Type) -> Any:
        return cls._instances.get(interface)

# Register implementations
ServiceLocator.register(DocumentRepositoryInterface, DocumentRepository(session))

# Use in application
doc_repo = ServiceLocator.get(DocumentRepositoryInterface)
```

---

## Interface Definition

### Complete Interface Example

```python
class DocumentRepositoryInterface(ABC):
    """Interface for Document repository."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Document]:
        """Get document by ID."""
        pass

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Document]:
        """Get all documents with optional pagination."""
        pass

    @abstractmethod
    def create(self, entity: Document) -> Document:
        """Create a new document."""
        pass

    @abstractmethod
    def update(self, entity: Document) -> Document:
        """Update an existing document."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete a document by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all documents."""
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if document exists by ID."""
        pass

    @abstractmethod
    def get_by_file_path(self, file_path: str) -> Optional[Document]:
        """Get document by file path."""
        pass

    @abstractmethod
    def get_by_file_hash(self, file_hash: str) -> List[Document]:
        """Get documents by file hash."""
        pass

    @abstractmethod
    def get_by_financial_year(self, financial_year: str) -> List[Document]:
        """Get documents by financial year."""
        pass

    @abstractmethod
    def get_by_document_type(self, document_type: str) -> List[Document]:
        """Get documents by document type."""
        pass

    @abstractmethod
    def get_duplicates(self) -> List[Document]:
        """Get all duplicate documents."""
        pass

    @abstractmethod
    def search_by_name(self, name_pattern: str) -> List[Document]:
        """Search documents by file name pattern."""
        pass

    @abstractmethod
    def get_unprocessed(self) -> List[Document]:
        """Get documents that haven't been processed yet."""
        pass
```

---

## Repository Package Structure

### Public Interface

```python
# repositories/__init__.py
from repositories.interfaces import (
    DocumentRepositoryInterface,
    MetadataRepositoryInterface,
    RelationshipRepositoryInterface,
    AuditLogRepositoryInterface,
    VersionLogRepositoryInterface,
)
from repositories.unit_of_work import UnitOfWork

__all__ = [
    "DocumentRepositoryInterface",
    "MetadataRepositoryInterface",
    "RelationshipRepositoryInterface",
    "AuditLogRepositoryInterface",
    "VersionLogRepositoryInterface",
    "UnitOfWork",
]
```

### Internal Implementation

```python
# Concrete implementations are NOT exported
# repositories/document_repository.py (internal)
# repositories/metadata_repository.py (internal)
# repositories/relationship_repository.py (internal)
# repositories/audit_log_repository.py (internal)
# repositories/version_log_repository.py (internal)
```

### Usage in Application Layer

```python
# Application layer depends on interfaces
from repositories.interfaces import DocumentRepositoryInterface

class DocumentService:
    def __init__(self, doc_repo: DocumentRepositoryInterface):
        self.doc_repo = doc_repo
```

---

## Benefits Summary

### 1. Dependency Inversion
- Application depends on interfaces, not implementations
- High-level modules decoupled from low-level modules
- Easier to maintain and extend

### 2. Testing
- Easy to mock for unit tests
- Tests run without database
- Faster, more reliable tests

### 3. Database Portability
- Switch databases without application changes
- Support multiple databases simultaneously
- Gradual migration strategies

### 4. Cloud Storage Support
- Migrate to cloud storage seamlessly
- Support multiple cloud providers
- Hybrid local + cloud deployments

### 5. Flexibility
- Add new implementations without changing application
- Swap implementations at runtime
- A/B test different implementations

### 6. Maintainability
- Clear separation of concerns
- Each implementation is independent
- Easier to understand and modify

---

## Trade-offs

### Complexity

**Increase:** Added interfaces and dependency injection

**Justification:** The complexity is justified by:
- Dependency inversion
- Testability
- Database portability
- Cloud storage support
- Long-term maintainability

### Overhead

**Minimal:** Interface overhead is negligible:
- Abstract methods have no runtime cost
- Dependency injection is constructor-based
- No performance impact

### Learning Curve

**Increase:** Developers must understand interfaces and dependency injection

**Justification:** Standard software engineering practices with clear benefits

---

## Best Practices

### 1. Always Program to Interfaces

```python
# ✅ Good
def process_document(repo: DocumentRepositoryInterface):
    doc = repo.get_by_id(1)

# ❌ Bad
def process_document(repo: DocumentRepository):
    doc = repo.get_by_id(1)
```

### 2. Use Constructor Injection

```python
# ✅ Good
class Service:
    def __init__(self, repo: DocumentRepositoryInterface):
        self.repo = repo

# ❌ Bad
class Service:
    def __init__(self):
        self.repo = DocumentRepository(session)
```

### 3. Hide Concrete Implementations

```python
# ✅ Good
from repositories.interfaces import DocumentRepositoryInterface

# ❌ Bad
from repositories.document_repository import DocumentRepository
```

### 4. Create Mock Implementations for Tests

```python
# ✅ Good
mock_repo = MockDocumentRepository()
service = DocumentService(mock_repo)

# ❌ Bad
service = DocumentService(DocumentRepository(session))
```

---

## Conclusion

Repository interfaces are a critical architectural pattern that enables dependency inversion, testability, database portability, and cloud storage support. The application layer depends on abstractions, not concrete implementations, making the system more flexible, maintainable, and testable.

**Status:** ✅ Dependency Inversion Compliant

---

**Document Version:** 1.0
**Last Updated:** 2024-01-01
**Next Review:** After adding new repository implementations
