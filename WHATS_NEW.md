# What's New - Multi-Bank Support! 🎉

## Latest Updates

### ✅ Multi-Bank CSV Parser System

The app now automatically detects and parses CSV files from different banks!

### 🏦 Supported Banks

1. **Citibank** - Full support for Status, Debit/Credit format
2. **Chase** - Transaction Date, Post Date, Type format
3. **Generic** - Standard Date, Description, Amount format

### 🎯 Key Features

- **Automatic Detection** - Upload any supported format, no configuration needed
- **Extensible** - Easy to add new bank formats (see BANKS_SUPPORTED.md)
- **Smart Parsing** - Handles different date formats, amount conventions
- **Preserves Metadata** - Stores transaction status, type in notes

### 📂 Sample Files Included

- `sample_transactions.csv` - Generic format example
- `sample_citibank.csv` - Citibank format example

### 🚀 Try It Now

1. **App is running at:** http://localhost:8000
2. **Upload Citibank CSV:**
   - Go to home page
   - Upload `sample_citibank.csv`
   - Watch transactions auto-categorize
3. **View Reports:**
   - Navigate to Reports
   - See spending breakdown by category

### 📝 How It Works

```
CSV Upload → Format Detection → Bank-Specific Parser → Categorization → Database
```

The system:
1. Reads your CSV file
2. Detects the bank format (Citibank, Chase, or Generic)
3. Uses the appropriate parser
4. Converts to standard format
5. Auto-categorizes transactions
6. Stores in DuckDB

### 🔧 Architecture

New file: `app/csv_parsers.py`
- `CSVParser` - Base class
- `CitibankParser` - Handles Citibank format
- `ChaseParser` - Handles Chase format
- `GenericParser` - Fallback for standard format
- `CSVParserFactory` - Automatic detection and routing

### 📖 Documentation

- **[BANKS_SUPPORTED.md](BANKS_SUPPORTED.md)** - Complete guide to supported banks
- **[README.md](README.md)** - Updated with bank support info

### 🐛 Bug Fixes

- ✅ Fixed database insert issue (missing created_at column)
- ✅ Added pandas dependency for Plotly
- ✅ Improved error handling for malformed CSVs

### 🎓 Adding Your Bank

It's easy! See `BANKS_SUPPORTED.md` for step-by-step guide.

Example banks that can be added:
- American Express
- Bank of America  
- Capital One
- Discover
- Wells Fargo

### 💡 Next Steps

1. Upload your actual bank CSV
2. Check transaction categorization
3. Adjust categories as needed
4. Split any mixed transactions
5. Generate monthly reports

---

## Previous Features (Already Included)

✅ Web interface for upload and reports  
✅ Automatic categorization (15 categories)  
✅ Transaction splitting  
✅ Interactive Plotly charts  
✅ DuckDB storage  
✅ Docker containerization  
✅ Comprehensive logging  

---

**Enjoy your enhanced budgeting app!** 💰

