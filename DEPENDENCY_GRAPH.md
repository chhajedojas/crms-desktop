# Dependency Graph

## Clean Architecture Dependency Graph

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
            REPOS[Repositories]
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
        ALEMBIC[Alembic]
    end

    UI --> APP
    APP --> DOMAIN
    DOMAIN --> REPOS
    REPOS --> DOMAIN
    REPOS --> MODELS
    REPOS --> MAP
    UOW --> REPOS
    MODELS --> SQLITE
    MODELS --> POSTGRES
    CONN --> SQLITE
    CONN --> POSTGRES
    ALEMBIC -.-> MODELS

    style DOMAIN fill:#e8f5e9
    style MODELS fill:#fff3e0
    style MAP fill:#f3e5f5
    style REPOS fill:#e1f5ff
    style UI fill:#fce4ec
    style APP fill:#fff9c4
```

## Module Dependency Graph

```mermaid
graph TD
    DOMAIN[domain/__init__.py]
    BASE[repositories/base.py]
    DOC_REPO[repositories/document_repository.py]
    META_REPO[repositories/metadata_repository.py]
    UOW[repositories/unit_of_work.py]
    MODELS[database/models.py]
    MAP[database/mappers.py]
    CONN[database/connection.py]
    EXCEPT[database/exceptions.py]

    BASE --> DOMAIN
    BASE --> EXCEPT
    BASE --> MODELS
    BASE --> MAP

    DOC_REPO --> BASE
    DOC_REPO --> DOMAIN
    DOC_REPO --> MODELS
    DOC_REPO --> MAP

    META_REPO --> BASE
    META_REPO --> DOMAIN
    META_REPO --> MODELS
    META_REPO --> MAP

    UOW --> REPOS

    CONN --> MODELS

    style DOMAIN fill:#e8f5e9
    style MODELS fill:#fff3e0
    style MAP fill:#f3e5f5
    style REPOS fill:#e1f5ff
    style CONN fill:#fce4ec
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant App as Application Layer
    participant Repo as Repository
    participant Mapper as Mapper
    participant ORM as ORM Model
    participant DB as Database

    App->>Repo: get_by_id(1)
    Repo->>ORM: SELECT * FROM documents WHERE id = 1
    ORM->>DB: Query
    DB-->>ORM: ORM Model
    ORM-->>Repo: ORM Model
    Repo->>Mapper: to_domain(ORM Model)
    Mapper-->>Repo: Domain Entity
    Repo-->>App: Domain Entity
```

## Architecture Layers Comparison

### Before Refactoring (Violations)

```
Application Layer
    ↓ (violates: depends on SQLAlchemy)
Persistence Layer
    ↓ (violates: ORM models exposed)
Domain Layer (empty/ignored)
```

### After Refactoring (Compliant)

```
Application Layer
    ↓ (depends on domain entities only)
Domain Layer
    ↓ (pure Python, no infrastructure)
Persistence Layer
    ↓ (ORM models internal, mappers convert)
Database
```

## Import Dependencies

### Domain Layer

```mermaid
graph LR
    D[domain/__init__.py] --> DC[dataclasses]
    D --> DT[datetime]
    D --> TP[typing]
    D --> E[enum]

    style D fill:#e8f5e9
```

### Repository Layer

```mermaid
graph LR
    RB[repositories/base.py] --> D[domain/__init__.py]
    RB --> EX[database/exceptions.py]
    RB --> M[database/models.py]
    RB --> MP[database/mappers.py]

    DR[repositories/document_repository.py] --> RB
    DR --> D
    DR --> M
    DR --> MP

    MR[repositories/metadata_repository.py] --> RB
    MR --> D
    MR --> M
    MR --> MP

    style D fill:#e8f5e9
    style M fill:#fff3e0
    style MP fill:#f3e5f5
    style RB fill:#e1f5ff
```

### Persistence Layer

```mermaid
graph LR
    M[database/models.py] --> SA[sqlalchemy]
    C[database/connection.py] --> SA
    C --> M
    MP[database/mappers.py] --> D[domain/__init__.py]
    MP --> M

    style M fill:#fff3e0
    style SA fill:#e1f5ff
    style MP fill:#f3e5f5
    style D fill:#e8f5e9
```

## Database Portability

### SQLite to PostgreSQL Migration

```mermaid
graph TB
    subgraph "What Changes"
        C1[database/connection.py]
        M1[database/models.py]
        MP1[database/mappers.py]
    end

    subgraph "What Stays the Same"
        D1[domain/__init__.py]
        R1[repositories/*.py]
        APP[Application Layer]
        UI[Presentation Layer]
    end

    C1 -.-> D1
    M1 -.-> D1
    MP1 -.-> D1

    style C1 fill:#fff3e0
    style M1 fill:#fff3e0
    style MP1 fill:#f3e5f5
    style D1 fill:#e8f5e9
    style R1 fill:#e1f5ff
    style APP fill:#fff9c4
    style UI fill:#fce4ec
```
