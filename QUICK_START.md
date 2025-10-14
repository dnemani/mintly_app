# 🚀 Quick Start Guide

## Access Your Reports

After running `docker-compose up --build`:

### 1️⃣ React Reports (Recommended)
**URL:** http://localhost:3000/reports

**Features:**
- Quick date buttons: MTD, YTD, QTD, 30D, 60D, 90D
- Category filter checkboxes
- Interactive charts
- Real-time updates

### 2️⃣ Python Reports
**URL:** http://localhost:8000/reports

**Features:**
- Date range picker
- Interactive Plotly charts
- Server-side rendered

### 3️⃣ Upload Transactions
**URL:** http://localhost:8000/

Upload your credit card CSV files.

### 4️⃣ View All Transactions
**URL:** http://localhost:8000/transactions

Browse and manage your transactions.

## Supported Banks

1. **Citibank** - Status, Date, Description, Debit, Credit columns
2. **Costco Visa** - Status, Date, Description, Debit, Credit, Member Name columns
3. **Generic CSV** - Single "Amount" column format

## Quick Tips

✅ **Use React frontend** (port 3000) for best experience
✅ **Click date preset buttons** instead of manually selecting dates
✅ **Filter by category** using checkboxes
✅ **Hover over charts** for detailed information
✅ **Split transactions** into multiple categories
✅ **All data stored** in DuckDB for fast queries

## Need Help?

Check these files:
- `README.md` - Full documentation
- `INTERACTIVE_REPORTS_SOLUTION.md` - Details about reports
- `BANKS_SUPPORTED.md` - How to add new bank formats
