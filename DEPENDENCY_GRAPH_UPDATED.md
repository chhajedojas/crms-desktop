# Updated Dependency Graph (With Repository Interfaces)

## Clean Architecture Dependency Graph (Updated)

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Electron + React UI]
    end

    subgraph "Application Layer"
        APP[Business Logic]
    end

    subgraph "Domain Layer"
        DOMAIN[Domain Entities]
        DOMAIN_NOTE[Document, Metadata, etc.]
    end

    subgraph "Persistence Layer"
        subgraph "Public Interface"
            INTERFACES[Repository Interfaces]
            REPOS_IMPL[Concrete Repositories]
            UOW[Unit of Work]
        end

        subgraph "Internal Implementation"
            MAP[Mappers]
            MODELS[ORM Models]
            CONN[Connection Manager]
        end
    end

    subgraph "Infrastructure"
        SQLITE[SQLite]
        POSTGRES[PostgreSQL]
        S3[AWS S3]
        ALEMBIC[Alembic]
    end

    UI --> APP
    APP --> INTERFACES
    INTERFACES --> DOMAIN
    REPOS_IMPL --> INTERFACES
    REPOS_IMPL --> DOMAIN
    REPOS_IMPL --> MODELS
    REPOS_IMPL --> MAP
    UOW --> INTERFACES
    MODELS --> SQLITE
    MODELS --> POSTGRES
    S3 -.-> REPOS_IMPL
    CONN --> SQLITE
    CONN --> POSTGRES
    ALEMBIC -.-> MODELS

    style DOMAIN fill:#e8f5e9
    style INTERFACES fill:#e3f2fd
    style MODELS fill:#fff3e0
    style MAP fill:#f3e5f5
    style REPOS_IMPL fill:#e1f5ff
    style UI fill:#fce4ec
    style APP fill:#fff9c4
```

## Module Dependency Graph (Updated)

```mermaid
graph TD
    DOMAIN[domain/__init__.py]
    INTERFACES[repositories/interfaces.py]
    BASE[repositories/base.py]
    DOC_REPO[repositories/document_repository.py]
    META_REPO[repositories/metadata_repository.py]
    REL_REPO[repositories/relationship_repository.py]
    AUDIT_REPO[repositories/audit_log_repository.py]
    VER_REPO[repositories/version_log_repository.py]
    UOW[repositories/unit_of_work.py]
    MODELS[database/models.py]
    MAP[database/mappers.py]
    CONN[database/connection.py]
    EXCEPT[database/exceptions.py]

    INTERFACES --> DOMAIN
    BASE --> INTERFACES
    BASE --> EXCEPT
    BASE --> MODELS
    BASE --> MAP

    DOC_REPO --> BASE
    DOC_REPO --> INTERFACES
    DOC_REPO --> DOMAIN
    DOC_REPO --> MODELS
    DOC_REPO --> MAP

    META_REPO --> BASE
    META_REPO --> INTERFACES
    META_REPO --> DOMAIN
    META_REPO --> MODELS
    META_REPO --> MAP

    REL_REPO --> BASE
    REL_REPO --> INTERFACES
    REL_REPO --> DOMAIN
    REL_REPO --> MODELS
    REL_REPO --> MAP

    AUDIT_REPO --> BASE
    AUDIT_REPO --> INTERFACES
    AUDIT_REPO --> DOMAIN
    AUDIT_REPO --> MODELS
    AUDIT_REPO --> MAP

    VER_REPO --> BASE
    VER_REPO --> INTERFACES
    VER_REPO --> DOMAIN
    VER_REPO --> MODELS
    VER_REPO --> MAP

    UOW --> INTERFACES

    CONN --> MODELS

    style DOMAIN fill:#e8f5e9
    style INTERFACES fill:#e3f2fd
    style MODELS fill:#fff3e0
    style MAP fill:#f3e5f5
    style REPOS fill:#e1f5ff
    style CONN fill:#fce4ec
```

## Dependency Inversion Example

```mermaid
sequenceDiagram
    participant App as Application Layer
    participant Intf as Repository Interface
    participant Impl as Concrete Repository
    participant ORM as ORM Model
    participant DB as Database

    App->>Intf: doc_repo.get_by_id(1)
    Intf->>Impl: (polymorphic call)
    Impl->>ORM: SELECT * FROM documents WHERE id = 1
    ORM->>DB: Query
    DB-->>ORM: ORM Model
    ORM-->>Impl: ORM Model
    Impl->>MAP: to_domain(ORM Model)
    MAP-->>Impl: Domain Entity
    Impl-->>Intf: Domain Entity
    Intf-->>App: Domain Entity
```

## Application Layer Dependency

```mermaid
graph LR
    APP[Application Layer]
    INTF[Repository Interfaces]
    DOMAIN[Domain Entities]

    APP --> INTF
    INTF --> DOMAIN

    style APP fill:#fff9c4
    style INTF fill:#e3f2fd
    style DOMAIN fill:#e8f5e9
```

**Key Point:** Application layer depends ONLY on interfaces, not concrete implementations.

## Multiple Implementations

```mermaid
graph TB
    subgraph "Application Layer"
        APP[Business Logic]
    end

    subgraph "Repository Interface"
        INTF[DocumentRepositoryInterface]
    end

    subgraph "Concrete Implementations"
        SQLITE_REPO[SQLite Repository]
        POSTGRES_REPO[PostgreSQL Repository]
        S3_REPO[S3 Repository]
        MOCK_REPO[Mock Repository]
    end

    APP --> INTF
    INTF --> SQLITE_REPO
    INTF --> POSTGRES_REPO
    INTF --> S3_REPO
    INTF --> MOCK_REPO

    style APP fill:#fff9c4
    style INTF fill:#e3f2fd
    style SQLITE_REPO fill:#e1f5ff
    style POSTGRES_REPO fill:#e1f5ff
    style S3_REPO fill:#e1f5ff
    style MOCK_REPO fill:#c8e6c9
```

## Repository Package Exports

```mermaid
graph LR
    subgraph "repositories/__init__.py"
        EXPORTS[Public Exports]
    end

    subgraph "Internal Files"
        INTERFACES[interfaces.py]
        BASE[base.py]
        DOC[document_repository.py]
        META[metadata_repository.py]
        REL[relationship_repository.py]
        AUDIT[audit_log_repository.py]
        VER[version_log_repository.py]
        UOW[unit_of_work.py]
    end

    EXPORTS --> INTERFACES
    EXPORTS --> UOW

    style EXPORTS fill:#e3f2fd
    style INTERFACES fill:#e3f2fd
    style UOW fill:#e3f2fd
    style DOC fill:#fff3e0
    style META fill:#fff3e0
    style REL fill:#fff3e0
    style AUDIT fill:#fff3e0
    style VER fill:#fff3e0
    style BASE fill:#fff3e0
```

**Key Point:** Only interfaces and Unit of Work are exported. Concrete implementations are internal.

## Testing Architecture

```mermaid
graph TB
    subgraph "Tests"
        TEST[Unit Tests]
    end

    subgraph "Test Doubles"
        MOCK[Mock Repository]
    end

    subgraph "Repository Interface"
        INTF[DocumentRepositoryInterface]
    end

    subgraph "Production Code"
        IMPL[Concrete Repository]
    end

    TEST --> MOCK
    MOCK --> INTF
    INTF --> IMPL

    style TEST fill:#c8e6c9
    style MOCK fill:#c8e6c9
    style INTF fill:#e3f2fd
    style IMPL fill:#e1f5ff
```

**Key Point:** Tests use mock implementations that implement the same interface as production code.

## Database Portability

```mermaid
graph TB
    subgraph "Application Layer"
        APP[Business Logic]
    end

    subgraph "Repository Interface"
        INTF[DocumentRepositoryInterface]
    end

    subgraph "SQLite Implementation"
        SQLITE_REPO[SQLite Repository]
        SQLITE[SQLite Database]
    end

    subgraph "PostgreSQL Implementation"
        POSTGRES_REPO[PostgreSQL Repository]
        POSTGRES[PostgreSQL Database]
    end

    APP --> INTF
    INTF --> SQLITE_REPO
    SQLITE_REPO --> SQLITE
    INTF --> POSTGRES_REPO
    POSTGRES_REPO --> POSTGRES

    style APP fill:#fff9c4
    style INTF fill:#e3f2fd
    style SQLITE_REPO fill:#e1f5ff
    style POSTGRES_REPO fill:#e1f5ff
```

**Key Point:** Application layer unchanged when switching databases.

## Cloud Storage Support

```mermaid
graph TB
    subgraph "Application Layer"
        APP[Business Logic]
    end

    subgraph "Repository Interface"
        INTF[DocumentRepositoryInterface]
    end

    subgraph "Local Storage"
        LOCAL_REPO[Local Repository]
        LOCAL_DB[SQLite Database]
    end

    subgraph "Cloud Storage"
        S3_REPO[S3 Repository]
        S3[AWS S3]
    end

    APP --> INTF
    INTF --> LOCAL_REPO
    LOCAL_REPO --> LOCAL_DB
    INTF --> S3_REPO
    S3_REPO --> S3

    style APP fill:#fff9c4
    style INTF fill:#e3f2fd
    style LOCAL_REPO fill:#e1f5ff
    style S3_REPO fill:#e1f5ff
```

**Key Point:** Application layer unchanged when migrating to cloud storage.

## Comparison: Before vs After

### Before (No Interfaces)

```mermaid
graph TB
    APP[Application Layer]
    REPO[Concrete Repository]
    ORM[ORM Models]
    DB[Database]

    APP --> REPO
    REPO --> ORM
    ORM --> DB

    style APP fill:#fff9c4
    style REPO fill:#fff3e0
    style ORM fill:#fff3e0
    style DB fill:#fff3e0
```

**Problem:** Application depends on concrete implementation.

### After (With Interfaces)

```mermaid
graph TB
    APP[Application Layer]
    INTF[Repository Interface]
    REPO[Concrete Repository]
    ORM[ORM Models]
    DB[Database]

    APP --> INTF
    INTF --> REPO
    REPO --> ORM
    ORM --> DB

    style APP fill:#fff9c4
    style INTF fill:#e3f2fd
    style REPO fill:#e1f5ff
    style ORM fill:#fff3e0
    style DB fill:#fff3e0
```

**Solution:** Application depends on interface, concrete implementation depends on interface.

## Summary of Changes

### Added

1. **Repository Interfaces** (`repositories/interfaces.py`)
   - DocumentRepositoryInterface
   - MetadataRepositoryInterface
   - RelationshipRepositoryInterface
   - AuditLogRepositoryInterface
   - VersionLogRepositoryInterface

2. **Concrete Implementations Updated**
   - All repositories now implement their respective interfaces
   - DocumentRepository implements DocumentRepositoryInterface
   - MetadataRepository implements MetadataRepositoryInterface
   - etc.

3. **Package Exports Updated**
   - Only interfaces and Unit of Work are exported
   - Concrete implementations are internal

### Benefits

1. **Dependency Inversion**
   - Application depends on interfaces
   - Concrete implementations depend on interfaces
   - High-level modules decoupled from low-level modules

2. **Testing**
   - Easy to mock for unit tests
   - Tests run without database
   - Faster, more reliable tests

3. **Database Portability**
   - Switch databases without application changes
   - Support multiple databases simultaneously
   - Gradual migration strategies

4. **Cloud Storage Support**
   - Migrate to cloud storage seamlessly
   - Support multiple cloud providers
   - Hybrid local + cloud deployments

---

**Document Version:** 2.0
**Last Updated:** 2024-01-01
**Changes:** Added repository interfaces for dependency inversion
