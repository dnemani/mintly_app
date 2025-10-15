# 🏷️ Tag-Based Filtering Implementation

## ✅ Completed Features

### 1. **Database Schema Updates** ✅
Added support for tags, source tracking, and merchant extraction:

#### New Tables
- **`tags`** - Stores unique tag names
  - `id` (INTEGER PRIMARY KEY)
  - `name` (VARCHAR UNIQUE)
  - `created_at` (TIMESTAMP)

- **`transaction_tags`** - Junction table for many-to-many relationship
  - `transaction_id` (INTEGER, FK to transactions)
  - `tag_id` (INTEGER, FK to tags)
  - `created_at` (TIMESTAMP)
  - PRIMARY KEY (transaction_id, tag_id)

#### New Transaction Columns
- **`source`** (VARCHAR) - Tracks which bank/card the transaction came from
  - Examples: "Citibank", "Costco Visa", "Chase", "Generic CSV"
- **`merchant`** (VARCHAR) - Extracted merchant name from description
  - Examples: "Amazon", "Walmart", "Target", "Costco"

### 2. **Merchant Extraction Logic** ✅
Created intelligent merchant extraction system (`app/merchant_extractor.py`):

#### Features
- **Pattern-based extraction** - Uses regex patterns to identify merchants
- **Name cleanup** - Removes corporate suffixes (INC, LLC, etc.)
- **Common mappings** - Maps abbreviations to full names (AMZN → Amazon)
- **Fallback logic** - Takes first few words if pattern matching fails

#### Example Extractions
```
"THE HOME DEPOT #4641 RESTON VA" → "The Home Depot"
"AMAZON MKTPLACE AMZN.COM/BILL WA" → "Amazon"
"COSTCO WHSE #1234 STERLING VA" → "Costco"
"SQ *COFFEE SHOP" → "Coffee Shop"
```

### 3. **CSV Parser Updates** ✅
Updated all CSV parsers to track source and extract merchants:

#### Updated Parsers
- **CitibankParser** - `source_name = "Citibank"`
- **CostcoVisaParser** - `source_name = "Costco Visa"`
- **ChaseParser** - `source_name = "Chase"`
- **GenericParser** - `source_name = "Generic CSV"`

#### What's Tracked
- Each transaction now includes:
  - `source`: Which bank/card it came from
  - `merchant`: Extracted merchant name from description

### 4. **API Endpoints for Tag Management** ✅
Created comprehensive REST API for tags (`app/api/tags.py`):

#### Tag Management Endpoints
```
GET    /api/tags/list                      - Get all tags with usage counts
POST   /api/tags/{transaction_id}/add      - Add tag to transaction
DELETE /api/tags/{transaction_id}/remove   - Remove tag from transaction
GET    /api/tags/{transaction_id}/list     - Get tags for a transaction
```

#### Filtering Endpoints
```
GET    /api/tags/filter/{tag_name}         - Get transactions by tag
GET    /api/tags/sources                   - Get all transaction sources
GET    /api/tags/merchants                 - Get all merchants with counts
```

#### Example API Usage
```bash
# Get all tags
curl http://localhost:8000/api/tags/list

# Add a tag to transaction #5
curl -X POST http://localhost:8000/api/tags/5/add \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "business-expense"}'

# Get transactions tagged "business-expense"
curl http://localhost:8000/api/tags/filter/business-expense

# Get all sources
curl http://localhost:8000/api/tags/sources
# Returns: {"sources": ["Citibank", "Costco Visa", "Chase"]}

# Get all merchants
curl http://localhost:8000/api/tags/merchants
# Returns: {"merchants": [{"name": "Amazon", "count": 15}, ...]}
```

### 5. **Database Helper Methods** ✅
Added comprehensive tag management methods to `DatabaseManager`:

```python
# Tag Management
db_manager.get_or_create_tag(tag_name)                 # Create tag if needed
db_manager.add_tag_to_transaction(transaction_id, tag)  # Add tag
db_manager.remove_tag_from_transaction(transaction_id, tag)  # Remove tag
db_manager.get_transaction_tags(transaction_id)        # Get all tags
db_manager.get_all_tags()                              # Get all tags with counts
db_manager.get_transactions_by_tag(tag_name)           # Filter by tag
```

## 🔧 How It Works

### When You Upload a CSV
1. **Parser Detection** - System detects which bank format
2. **Transaction Parsing** - Extracts date, description, amount
3. **Source Tagging** - Sets `source` field (e.g., "Costco Visa")
4. **Merchant Extraction** - Parses description to get merchant name
5. **Auto-Categorization** - Assigns category based on rules
6. **Database Insert** - Saves with all fields

### Example Transaction Flow
```
CSV Row:
  Date: 09/21/2025
  Description: "THE HOME DEPOT #4641 RESTON VA"
  Debit: 224.00

After Processing:
  date: 2025-09-21
  description: "THE HOME DEPOT #4641 RESTON VA"
  amount: -224.00
  category: "Shopping"  (auto-assigned)
  source: "Costco Visa"  (from parser)
  merchant: "The Home Depot"  (extracted)
  notes: "Status: Cleared"
```

## 📊 Use Cases

### 1. Filter by Source
```sql
SELECT * FROM transactions WHERE source = 'Citibank'
```
See all transactions from your Citibank card.

### 2. Filter by Merchant
```sql
SELECT * FROM transactions WHERE merchant = 'Amazon'
```
See all Amazon purchases across all cards.

### 3. Tag Business Expenses
```python
# Tag transactions for tax purposes
db_manager.add_tag_to_transaction(123, "business-expense")
db_manager.add_tag_to_transaction(124, "business-expense")

# Later, get all business expenses
business_txns = db_manager.get_transactions_by_tag("business-expense")
```

### 4. Track Merchant Spending
```bash
# Get top merchants
curl http://localhost:8000/api/tags/merchants
```
See where you spend the most money.

## 🚀 Testing the Features

### 1. Upload a CSV
```bash
curl -X POST http://localhost:8000/api/transactions/upload \
  -F "file=@sample_costco_visa.csv"
```

### 2. Check Sources
```bash
curl http://localhost:8000/api/tags/sources
# Should show: {"sources": ["Costco Visa"]}
```

### 3. Check Merchants
```bash
curl http://localhost:8000/api/tags/merchants
# Shows: {"merchants": [{"name": "The Home Depot", "count": 2}, ...]}
```

### 4. Add a Tag
```bash
curl -X POST http://localhost:8000/api/tags/4/add \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "home-improvement"}'
```

### 5. Filter by Tag
```bash
curl http://localhost:8000/api/tags/filter/home-improvement
```

## 📝 Database Schema

```sql
-- Tags table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction-Tags junction table
CREATE TABLE transaction_tags (
    transaction_id INTEGER,
    tag_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id, tag_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- Updated transactions table
ALTER TABLE transactions ADD COLUMN source VARCHAR;
ALTER TABLE transactions ADD COLUMN merchant VARCHAR;
```

## 🎯 Future Enhancements (Pending)

### 1. **Ollama LLM Integration** (Pending)
- Automatic categorization using local LLM
- Learn from user's past categorization choices
- Suggest tags based on transaction patterns

### 2. **Frontend Updates** (Pending)
- Display tags in transaction list
- Add/remove tags from UI
- Filter by tags, source, and merchant
- Visual tag chips/badges

### 3. **Report Enhancements** (Pending)
- Spending by source (compare cards)
- Spending by merchant over time
- Tag-based budget tracking
- Export filtered transactions

## 🔍 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tags/list` | Get all tags with usage counts |
| POST | `/api/tags/{id}/add` | Add tag to transaction |
| DELETE | `/api/tags/{id}/remove?tag_name=X` | Remove tag from transaction |
| GET | `/api/tags/{id}/list` | Get transaction's tags |
| GET | `/api/tags/filter/{tag_name}` | Get transactions by tag |
| GET | `/api/tags/sources` | Get all transaction sources |
| GET | `/api/tags/merchants` | Get all merchants with counts |

### Response Examples

**GET /api/tags/list**
```json
[
  {
    "id": 1,
    "name": "business-expense",
    "usage_count": 15
  },
  {
    "id": 2,
    "name": "tax-deductible",
    "usage_count": 8
  }
]
```

**GET /api/tags/merchants**
```json
{
  "merchants": [
    {"name": "Amazon", "count": 42},
    {"name": "Walmart", "count": 18},
    {"name": "The Home Depot", "count": 12}
  ]
}
```

**GET /api/tags/sources**
```json
{
  "sources": ["Citibank", "Costco Visa", "Chase"]
}
```

## ✅ Summary

**Completed:**
- ✅ Database schema with tags, source, and merchant
- ✅ Intelligent merchant extraction from descriptions
- ✅ CSV parsers track source for all bank formats
- ✅ Complete REST API for tag management
- ✅ Filtering by tags, source, and merchant

**Pending:**
- ⏳ Ollama LLM integration for smart categorization
- ⏳ Frontend UI for displaying and managing tags
- ⏳ Enhanced reports with tag-based filtering

**Ready to Use:**
- Upload CSVs and see source & merchant automatically populated
- Use API to add custom tags to transactions
- Filter transactions by tags, source, or merchant
- Track spending patterns across different cards/merchants

---

*Last Updated: October 14, 2025*

