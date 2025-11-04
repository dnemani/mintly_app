# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

Mintly is a personal budgeting application that parses credit card statements (CSV), auto-categorizes transactions, and provides interactive reports. Built with FastAPI backend, DuckDB database, Polars for data processing, and offers multiple frontend options (React SPA, Python/Jinja2, Dash, and Shiny).

## Common Commands

### Running the Application

```bash
# Full stack with Docker (recommended)
docker-compose up --build

# Backend only
docker-compose up backend
# Or locally: python app/main.py

# React frontend (requires backend)
cd frontend && npm install && npm run dev

# Standalone Dash reports
python run_dash_standalone.py

# Standalone Shiny reports
shiny run --host 0.0.0.0 --port 8051 run_shiny_standalone.py

# Health check
curl http://localhost:8000/health
```

### Testing

```bash
# Test file upload
curl -X POST "http://localhost:8000/api/transactions/upload" \
  -F "file=@sample_transactions.csv"

# List transactions
curl "http://localhost:8000/api/transactions/list?limit=10"

# Get reports
curl "http://localhost:8000/api/reports/summary"

# Interactive API docs
open http://localhost:8000/docs
```

### Database Operations

```bash
# Connect to database
duckdb data/mintly.db

# Check data
duckdb data/mintly.db "SELECT COUNT(*) FROM transactions;"
duckdb data/mintly.db "SELECT category, COUNT(*) FROM transactions GROUP BY category;"
```

## Architecture

### Data Flow

**CSV Upload → Parser Detection → Merchant Extraction → Auto-Categorization → Database Storage**

1. **CSV Parsing**: Factory pattern detects bank format (Citibank, Costco Visa, Chase, Generic) based on column headers
2. **Merchant Extraction**: Regex patterns clean descriptions to extract merchant names (e.g., "COSTCO WHSE #1234" → "Costco")
3. **Auto-Categorization**: 100+ merchant patterns match to 15 categories (Groceries, Restaurants, Transportation, etc.)
4. **Database Storage**: DuckDB with sequence-managed IDs and tag relationships

### Key Components

**Database Layer (`app/database.py`)**
- `DatabaseManager`: Singleton-pattern class managing DuckDB connection
- Schema uses sequences for ID generation (not auto-increment)
- Read-only mode available for concurrent access (Dash reports use this)
- Three tables: `transactions`, `tags`, `transaction_tags` (many-to-many junction)

**CSV Parsing (`app/csv_parsers.py`)**
- Factory pattern with parser detection chain: CostcoVisaParser → CitibankParser → ChaseParser → GenericParser
- Each parser has `detect()` method checking column headers
- Parsers set `source` field (bank name) and call merchant extractor
- Amount normalization: expenses are negative, payments/returns are positive

**Categorization (`app/categorizer.py`)**
- Pattern-matching with compiled regex for performance
- Category hierarchy: specific patterns first, fallback to UNCATEGORIZED
- Positive amounts automatically categorized as INCOME
- `categorize_batch()` for efficient bulk processing

**Merchant Extraction (`app/merchant_extractor.py`)**
- Removes location codes, store numbers, suffixes (INC, LLC, etc.)
- Maps common abbreviations (AMZN → Amazon, WHSE → Warehouse)
- Fallback: takes first 2-3 words if patterns don't match

**API Structure (`app/api/`)**
- `transactions.py`: Upload, list, CRUD, split operations
- `reports.py`: Summary, charts (pie, bar, line), date filtering
- `tags.py`: Tag management, filter by tag/source/merchant

**Database ID Management**
- Uses DuckDB sequences: `transactions_id_seq`, `tags_id_seq`
- Batch inserts: Get starting ID, generate sequence, advance sequence
- `_sync_sequence()` called on initialization to prevent ID conflicts

### Multi Frontend Architecture

**Python/Jinja2 (Port 8000)**
- Server-rendered templates in `app/templates/`
- Static Plotly charts embedded in HTML
- Simple upload interface at root `/`

**React SPA (Port 3000)**
- Vite build system, modern component architecture
- Located in `frontend/` directory
- API calls to backend via `services/` layer
- Recharts for client-side visualizations

**Dash Reports (Port 8050)**
- Standalone application using `run_dash_standalone.py`
- Creates DB copy (`mintly_dash.db`) for read-only access (prevents locks)
- Interactive filters: date presets (MTD/YTD/QTD), categories, amount ranges
- Top merchants analysis, sortable transaction tables
- Built with Dash and Bootstrap components

**Shiny Reports (Port 8051)**
- Standalone application using `run_shiny_standalone.py`
- Creates DB copy (`mintly_shiny.db`) for read-only access (prevents locks)
- Reactive programming model with decorator-based server logic
- Interactive filters: date presets, categories, amount ranges
- Similar functionality to Dash but using Shiny for Python framework
- Command: `shiny run --host 0.0.0.0 --port 8051 run_shiny_standalone.py`

## Important Patterns

### Database Connection Management

```python
# Normal write access
db_manager = DatabaseManager(db_path="data/mintly.db")

# Read-only for concurrent access (Dash reports)
db_manager = DatabaseManager(db_path="data/mintly_dash.db", read_only=True)

# Read-only for concurrent access (Shiny reports)
db_manager = DatabaseManager(db_path="data/mintly_shiny.db", read_only=True)
```

**Why**: DuckDB locks on writes. Dash and Shiny reports use separate DB copies in read-only mode to avoid conflicts with the main app.

### Batch Inserts with Sequences

```python
# Get starting ID
start_id = conn.execute("SELECT nextval('transactions_id_seq')").fetchone()[0]

# Generate IDs for batch
ids = list(range(start_id, start_id + len(df)))

# Advance sequence for remaining IDs
for _ in range(len(df) - 1):
    conn.execute("SELECT nextval('transactions_id_seq')")
```

**Why**: DuckDB sequences don't auto-increment in batch inserts. Must manually generate and advance.

### Transaction Splitting Pattern

1. Mark parent transaction with `is_split = TRUE`
2. Create child transactions with `parent_transaction_id` reference
3. Child transactions inherit parent's date but have own category/amount
4. Reports filter `is_split = FALSE` to avoid double-counting

### CSV Parser Factory Pattern

```python
factory = CSVParserFactory()
parser = factory.get_parser(csv_content)  # Auto-detects format
transactions = parser.parse(csv_content)
```

**Why**: Single interface handles multiple bank formats without conditional logic in upload endpoint.

## File Organization

```
app/
├── main.py              # FastAPI app, routers, static/template mounting
├── models.py            # Pydantic models, CategoryEnum (15 categories)
├── database.py          # DatabaseManager singleton, all DB operations
├── categorizer.py       # Pattern-based categorization with 100+ rules
├── csv_parsers.py       # Factory + bank-specific parsers
├── merchant_extractor.py # Merchant name extraction logic
├── dash_reports.py      # Dash app definition (not mounted in main.py)
├── shiny_reports.py     # Shiny app definition (standalone)
├── api/
│   ├── transactions.py  # Upload, CRUD, split operations
│   ├── reports.py       # Analytics, charts, summaries
│   └── tags.py          # Tag CRUD, filtering by tag/source/merchant
├── templates/           # Jinja2 HTML templates
└── static/              # CSS, JS for Python frontend

frontend/                # React SPA (Vite)
├── src/
│   ├── components/      # React components
│   ├── services/        # API client layer
│   └── App.jsx          # Main app component
└── package.json

data/
├── mintly.db            # Main database
├── mintly_dash.db       # Copy for Dash reports (read-only)
└── mintly_shiny.db      # Copy for Shiny reports (read-only)

logs/                    # Timestamped application logs
```

## Logging Convention

All modules use structured logging:
```python
logging.basicConfig(
    format='%(asctime)s|%(levelname)s|%(name)s|%(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
```

Logs include: timestamp, level, module name, message. Check `logs/` directory for debugging.

## Known Gotchas

1. **Dash Integration with FastAPI**: WSGIMiddleware has technical limitations. Dash runs standalone on port 8050, not mounted in main FastAPI app.

2. **Database Locking**: Main app and Dash can't share same DB file with write access. Dash uses read-only copy created by `create_db_copy()`.

3. **Sequence Sync**: After direct SQL inserts or DB copy operations, must call `_sync_sequence()` or manual `DROP/CREATE SEQUENCE` to prevent ID conflicts.

4. **Amount Sign Convention**: Expenses are negative, income/refunds are positive. CSV parsers normalize to this convention (Debit columns → negative).

5. **Category Enum**: All categories must be valid `CategoryEnum` values. Free-form strings will fail Pydantic validation.

6. **Port Conflicts**: App uses ports 8000 (backend), 3000 (React), 8050 (Dash), 8051 (Shiny). Check with `lsof -i :PORT` if startup fails.

## Tag-Based Filtering

Comprehensive tagging system for transactions:

- **Source tracking**: Every transaction records originating bank/card (e.g., "Citibank", "Costco Visa")
- **Merchant extraction**: Automated parsing of merchant names from descriptions
- **Custom tags**: User-defined tags via many-to-many relationship
- **API endpoints**: `/api/tags/` for tag CRUD, filtering, and source/merchant queries

See `TAG_BASED_FILTERING_IMPLEMENTATION.md` for detailed implementation.

## Docker Considerations

- Backend healthcheck prevents frontend/dash/shiny from starting before API is ready
- Volumes mount: `./data`, `./logs`, `./results` for persistence across container restarts
- Network: `mintly_network` bridge allows inter-container communication
- Frontend env: `VITE_API_URL` points to backend service name (not localhost)
- Services: backend (8000), frontend (3000), dash (8050), shiny (8051)

## Testing Sample Data

Three sample CSV files provided:
- `sample_transactions.csv`: Generic format
- `sample_costco_visa.csv`: Costco Visa format with Member Name
- `sample_citibank.csv`: Citibank format

Use these to test parser detection and categorization logic.
