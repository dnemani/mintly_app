# Mintly Application Architecture

This document provides a comprehensive overview of the Mintly budgeting application architecture.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        U1[User Browser]
    end

    subgraph "Frontend Services - Ports 3000, 8050-8052"
        FE1[React SPA<br/>Port 3000<br/>Vite + Recharts]
        FE2[Dash Reports<br/>Port 8050<br/>Plotly Dash]
        FE3[Shiny Reports<br/>Port 8051<br/>Shiny for Python]
        FE4[Streamlit Reports<br/>Port 8052<br/>Streamlit]
    end

    subgraph "Backend Service - Port 8000"
        BE[FastAPI Backend<br/>Port 8000]

        subgraph "API Routers"
            R1[Transactions Router]
            R2[Reports Router]
            R3[Tags Router]
        end

        subgraph "Core Logic"
            CSV[CSV Parser Factory<br/>Citibank/Costco/Chase/Generic]
            ME[Merchant Extractor<br/>Regex Pattern Matching]
            CAT[Auto Categorizer<br/>100+ Patterns]
            DBM[Database Manager<br/>Sequence Management]
        end

        subgraph "Templates"
            T1[Jinja2 Templates<br/>index/transactions/reports]
        end
    end

    subgraph "Data Storage"
        DB1[(Main Database<br/>mintly.db<br/>Read-Write)]
        DB2[(Dash Copy<br/>mintly_dash.db<br/>Read-Only)]
        DB3[(Shiny Copy<br/>mintly_shiny.db<br/>Read-Only)]
        DB4[(Streamlit Copy<br/>mintly_streamlit.db<br/>Read-Only)]
    end

    subgraph "Data Processing"
        POL[Polars DataFrames<br/>PyArrow Backend]
        DUCK[DuckDB<br/>Analytical Database]
    end

    %% User Connections
    U1 --> |HTTP| FE1
    U1 --> |HTTP| FE2
    U1 --> |HTTP| FE3
    U1 --> |HTTP| FE4
    U1 --> |HTTP| BE

    %% Frontend to Backend
    FE1 --> |REST API| BE

    %% Backend Internal Flow
    BE --> R1
    BE --> R2
    BE --> R3
    BE --> T1

    R1 --> CSV
    CSV --> ME
    ME --> CAT
    CAT --> DBM
    R1 --> DBM
    R2 --> DBM
    R3 --> DBM

    %% Database Connections
    DBM --> |Read-Write| DB1
    FE2 --> |Read-Only| DB2
    FE3 --> |Read-Only| DB3
    FE4 --> |Read-Only| DB4

    %% Data Processing
    DBM --> DUCK
    DBM --> POL
    DUCK --> DB1
    POL -.-> DUCK

    %% Styling
    classDef frontend fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    classDef backend fill:#FFF3E0,stroke:#F57C00,stroke-width:2px
    classDef database fill:#E8F5E9,stroke:#388E3C,stroke-width:2px
    classDef processing fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px

    class FE1,FE2,FE3,FE4 frontend
    class BE,R1,R2,R3,CSV,ME,CAT,DBM,T1 backend
    class DB1,DB2,DB3,DB4 database
    class POL,DUCK processing
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph "CSV Upload Flow"
        A[User Uploads CSV] --> B{Detect Format}
        B -->|Citibank| C1[CitibankParser]
        B -->|Costco Visa| C2[CostcoVisaParser]
        B -->|Chase| C3[ChaseParser]
        B -->|Generic| C4[GenericParser]

        C1 & C2 & C3 & C4 --> D[Extract Merchant]
        D --> E[Auto-Categorize<br/>100+ Patterns]
        E --> F[Normalize Amounts<br/>Expenses Negative]
        F --> G[Batch Insert<br/>Sequence IDs]
        G --> H[(mintly.db)]
    end

    subgraph "Reports Generation Flow"
        H --> I[Query by Date Range]
        I --> J[Filter: Category/Tag/Merchant]
        J --> K[Aggregate Data<br/>Polars DataFrames]
        K --> L1[Plotly Charts]
        K --> L2[Transaction Tables]
        L1 & L2 --> M[Render to Frontend]
    end

    classDef upload fill:#FFE0B2,stroke:#E65100
    classDef reports fill:#C8E6C9,stroke:#2E7D32

    class A,B,C1,C2,C3,C4,D,E,F,G,H upload
    class I,J,K,L1,L2,M reports
```

## Component Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant CSVParser
    participant MerchantExtractor
    participant Categorizer
    participant Database

    User->>Frontend: Upload CSV File
    Frontend->>Backend: POST /api/transactions/upload
    Backend->>CSVParser: Detect and Parse Format
    CSVParser->>MerchantExtractor: Extract Merchant Names
    MerchantExtractor->>Categorizer: Categorize by Patterns
    Categorizer->>Database: Batch Insert with Sequences
    Database-->>Backend: Transaction IDs
    Backend-->>Frontend: Success Response
    Frontend-->>User: Show Upload Summary

    User->>Frontend: View Reports
    Frontend->>Backend: GET /api/reports/summary?dates
    Backend->>Database: Query Transactions
    Database-->>Backend: Transaction Data
    Backend->>Backend: Aggregate with Polars
    Backend-->>Frontend: JSON Report Data
    Frontend-->>User: Render Charts & Tables
```

## Database Schema

```mermaid
erDiagram
    TRANSACTIONS ||--o{ TRANSACTION_TAGS : has
    TAGS ||--o{ TRANSACTION_TAGS : applied_to
    TRANSACTIONS ||--o| TRANSACTIONS : "split from"

    TRANSACTIONS {
        int id PK "Sequence Generated"
        datetime date
        string description
        float amount "Negative for expenses"
        string category "CategoryEnum"
        string notes
        bool is_split
        int parent_transaction_id FK
        string source "Bank name"
        string merchant "Extracted name"
    }

    TAGS {
        int id PK "Sequence Generated"
        string name UK
        datetime created_at
    }

    TRANSACTION_TAGS {
        int transaction_id FK
        int tag_id FK
    }
```

## Technology Stack

```mermaid
mindmap
  root((Mintly Stack))
    Backend
      FastAPI 0.104.1
      Python 3.11
      Uvicorn ASGI Server
    Database
      DuckDB 1.4.1
        Sequence Management
        Read-Only Mode
      Polars 0.19.19
        PyArrow Backend
        Fast Data Processing
    Frontend Options
      React SPA
        Vite Build Tool
        Recharts Visualization
      Python Templates
        Jinja2 Server-Side
        Plotly Static Charts
      Interactive Reports
        Dash 2.14.2
        Shiny 0.7.1
        Streamlit 1.29.0
    Data Processing
      CSV Parsing
        Factory Pattern
        4 Bank Formats
      Auto-Categorization
        Regex Patterns
        15 Categories
      Merchant Extraction
        Name Cleanup
        Abbreviation Mapping
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Compose Network: mintly_network"
        subgraph "Backend Container"
            B1[FastAPI App<br/>Port 8000]
            B2[Main Database<br/>mintly.db]
        end

        subgraph "Frontend Container"
            F1[React Dev Server<br/>Port 3000<br/>Vite + HMR]
        end

        subgraph "Dash Container"
            D1[Dash App<br/>Port 8050]
            D2[DB Copy<br/>mintly_dash.db]
        end

        subgraph "Shiny Container"
            S1[Shiny App<br/>Port 8051]
            S2[DB Copy<br/>mintly_shiny.db]
        end

        subgraph "Streamlit Container"
            ST1[Streamlit App<br/>Port 8052]
            ST2[DB Copy<br/>mintly_streamlit.db]
        end
    end

    subgraph "Mounted Volumes"
        V1[./data]
        V2[./logs]
        V3[./results]
    end

    B1 --> B2
    B2 -.->|Copy on Startup| D2
    B2 -.->|Copy on Startup| S2
    B2 -.->|Copy on Startup| ST2

    B1 -.-> V1
    B1 -.-> V2
    D1 -.-> V1
    S1 -.-> V1
    ST1 -.-> V1

    F1 -->|API Calls| B1
    D1 --> D2
    S1 --> S2
    ST1 --> ST2

    classDef container fill:#E1F5FE,stroke:#01579B,stroke-width:2px
    classDef volume fill:#FFF9C4,stroke:#F57F17,stroke-width:2px

    class B1,F1,D1,S1,ST1 container
    class V1,V2,V3 volume
```

## Key Architectural Patterns

### 1. Factory Pattern (CSV Parsing)
```
CSVParserFactory
  ├── CostcoVisaParser
  ├── CitibankParser
  ├── ChaseParser
  └── GenericParser
```

### 2. Singleton Pattern (Database Manager)
```
DatabaseManager (Single Instance)
  ├── Connection Pool Management
  ├── Sequence Generation
  └── Read-Only Mode Support
```

### 3. Strategy Pattern (Categorization)
```
Categorizer
  ├── Pattern Matching Strategy
  ├── 15 Category Enums
  └── 100+ Regex Rules
```

### 4. Repository Pattern (Data Access)
```
DatabaseManager
  ├── get_transactions_by_date_range()
  ├── insert_transactions_batch()
  ├── get_category_summary()
  └── tag_management()
```

## Port Allocation

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Backend | 8000 | HTTP | REST API & Server-Rendered UI |
| React | 3000 | HTTP | Modern SPA Frontend |
| Dash | 8050 | HTTP | Python Interactive Reports |
| Shiny | 8051 | HTTP | Reactive Reports (R-style) |
| Streamlit | 8052 | HTTP | Data Science Reports |

## Security Considerations

1. **Database Isolation**: Read-only copies prevent concurrent write conflicts
2. **Input Validation**: Pydantic models validate all API inputs
3. **CSV Sanitization**: Parser validates date formats and numeric values
4. **Amount Normalization**: Prevents injection via amount manipulation
5. **Category Enum**: Restricts categories to predefined safe values

## Performance Optimizations

1. **Caching Strategies**:
   - Streamlit: `@st.cache_data`, `@st.cache_resource`
   - Shiny: `@reactive.calc` for computed values
   - Backend: Polars lazy evaluation

2. **Batch Processing**:
   - CSV uploads processed in bulk
   - Sequence IDs generated in batch
   - Database inserts use batch operations

3. **Database Copies**:
   - Prevents read locks on main database
   - Each reporting service has dedicated copy
   - Refresh on service restart

## Future Architecture Considerations

- **Horizontal Scaling**: Add load balancer for multiple backend instances
- **Database Replication**: PostgreSQL or distributed DuckDB
- **Message Queue**: Async CSV processing with Celery/RabbitMQ
- **Caching Layer**: Redis for session state and query results
- **API Gateway**: Kong or Traefik for unified API management
