# Mintly Usage Guide

## Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up --build
```
Then open your browser to http://localhost:8000

### Option 2: Local Development
```bash
chmod +x run_local.sh
./run_local.sh
```

## Features Overview

### 1. Upload Transactions

1. Navigate to the home page (http://localhost:8000)
2. Click "Choose File" and select your CSV file
3. Click "Upload & Process"
4. The app will automatically categorize your transactions

**CSV Format:**
```csv
Date,Description,Amount
2025-01-15,Starbucks Coffee,-4.50
2025-01-16,Amazon.com,-45.99
```

**Supported Date Formats:**
- YYYY-MM-DD (2025-01-15)
- MM/DD/YYYY (01/15/2025)
- DD/MM/YYYY (15/01/2025)
- YYYY/MM/DD (2025/01/15)

**Amount Format:**
- Negative for expenses: -50.00
- Positive for income: 2500.00
- Can include currency symbols: $50.00
- Can use parentheses for negative: (50.00)

### 2. Manage Transactions

1. Go to the Transactions page
2. View all imported transactions
3. Change categories using the dropdown
4. Split transactions into multiple categories
5. Delete unwanted transactions

**Splitting a Transaction:**
1. Click "Split" button next to any transaction
2. Add multiple category entries
3. Ensure split amounts sum to the original amount
4. Click "Save Split"

### 3. View Reports

1. Navigate to the Reports page
2. Select date range (defaults to current month)
3. Click "Generate Report"
4. View:
   - Summary statistics (income, expenses, net balance)
   - Pie chart of spending by category
   - Bar chart of category breakdown
   - Line chart of daily spending trends

## Automatic Categorization

The app automatically categorizes transactions based on merchant names:

### Categories:
- **Groceries**: Whole Foods, Trader Joe's, Safeway, Kroger, etc.
- **Restaurants**: Starbucks, Chipotle, McDonald's, etc.
- **Transportation**: Shell, Uber, Lyft, parking, etc.
- **Utilities**: Electric, water, internet, phone bills
- **Entertainment**: Netflix, Spotify, movies, games
- **Shopping**: Amazon, Target, Best Buy, etc.
- **Healthcare**: CVS, Walgreens, doctors, dental
- **Travel**: Airlines, hotels, Airbnb
- **Housing**: Rent, mortgage, HOA
- **Insurance**: Auto, health, home insurance
- **Education**: Tuition, books, courses
- **Personal Care**: Gym, salon, spa
- **Subscriptions**: Monthly services
- **Income**: Positive amounts
- **Uncategorized**: Everything else

## Data Storage

- All data is stored locally in `data/mintly.db` (DuckDB database)
- Logs are stored in `logs/` directory with timestamps
- No data is sent to external servers
- Your financial data stays private

## Tips & Best Practices

1. **Regular Uploads**: Upload statements monthly for best tracking
2. **Review Categories**: Check auto-categorized transactions and adjust as needed
3. **Use Splits**: Split mixed purchases (e.g., groceries + household items)
4. **Export Data**: DuckDB files can be queried with SQL tools
5. **Backup**: Regularly backup your `data/` directory

## Troubleshooting

### CSV Upload Fails
- Ensure CSV has headers: Date, Description, Amount
- Check date format matches supported formats
- Remove any extra columns or formatting

### Charts Not Displaying
- Ensure you have transactions in the selected date range
- Check browser console for errors
- Refresh the page

### Docker Issues
```bash
# Rebuild container
docker-compose down
docker-compose up --build

# View logs
docker-compose logs -f
```

### Local Development Issues
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear cache
rm -rf __pycache__ app/__pycache__

# Reset database
rm data/mintly.db
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints:

**Upload Transactions:**
```
POST /api/transactions/upload
Content-Type: multipart/form-data
Body: file (CSV)
```

**List Transactions:**
```
GET /api/transactions/list?limit=100
```

**Update Category:**
```
PUT /api/transactions/{id}/category?category=Groceries
```

**Split Transaction:**
```
POST /api/transactions/{id}/split
Body: {
  "transaction_id": 1,
  "splits": [
    {"category": "Groceries", "amount": -50.00},
    {"category": "Personal Care", "amount": -15.00}
  ]
}
```

**Get Spending Report:**
```
GET /api/reports/summary?start_date=2025-01-01&end_date=2025-01-31
```

## Advanced Usage

### Querying the Database Directly

```python
import duckdb

conn = duckdb.connect('data/mintly.db')

# Get total spending by category
result = conn.execute("""
    SELECT category, SUM(amount) as total
    FROM transactions
    WHERE amount < 0
    GROUP BY category
    ORDER BY total ASC
""").fetchall()

print(result)
```

### Custom Categorization Patterns

Edit `app/categorizer.py` to add custom patterns:

```python
# Add in TransactionCategorizer.__init__
self.category_patterns[CategoryEnum.GROCERIES].append(r'\bmy local store\b')
```

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review this guide
3. Check the API documentation at `/docs`

## Version

Mintly v1.0.0

