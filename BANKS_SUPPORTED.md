# Supported Banks & CSV Formats

Mintly automatically detects and parses CSV statements from multiple banks and credit card companies. No configuration needed!

---

## 🏦 Currently Supported

### 1. Costco Visa Credit Cards

**Format Detection:** Looks for columns: `Status`, `Date`, `Description`, `Debit`, `Credit`, `Member Name`

**CSV Structure:**
```csv
Status,Date,Description,Debit,Credit,Member Name
Cleared,10/05/2025,COSTCO WHOLESALE #1234,234.56,,John Doe
Cleared,10/04/2025,SHELL GAS STATION,52.30,,John Doe
Cleared,09/28/2025,PAYMENT - THANK YOU,,500.00,John Doe
Pending,09/20/2025,SOUTHWEST AIRLINES,250.00,,Jane Doe
```

**Column Meanings:**
- **Status**: Cleared, Pending, etc.
- **Date**: Transaction date (MM/DD/YYYY)
- **Description**: Merchant name
- **Debit**: Purchases/charges (expenses)
- **Credit**: Payments/returns
- **Member Name**: Cardholder name

**Notes:**
- Debit amounts are treated as expenses (negative)
- Credit amounts are treated as payments/refunds (positive)
- Status and Member Name are stored in transaction notes
- Supports multiple cardholders on same account

---

### 2. Citibank Credit Cards

**Format Detection:** Looks for columns: `Status`, `Date`, `Description`, `Debit`, `Credit`

**CSV Structure:**
```csv
Status,Date,Description,Debit,Credit
Cleared,09/21/2025,"THE HOME DEPOT #4641 RESTON VA",199.99,
Cleared,09/21/2025,"TARGET RETURN",,50.00
Pending,09/22/2025,"AMAZON.COM",,25.99
```

**Column Meanings:**
- **Status**: Cleared, Pending, etc.
- **Date**: Transaction date (MM/DD/YYYY)
- **Description**: Merchant name
- **Debit**: Purchases/charges (expenses)
- **Credit**: Returns/refunds OR negative values for charges

**Notes:**
- Debit amounts are treated as expenses (negative)
- Credit amounts are treated as refunds/income (positive)
- Status is stored in transaction notes

---

### 3. Chase Credit Cards

**Format Detection:** Looks for columns: `Transaction Date`, `Post Date`, `Type`

**CSV Structure:**
```csv
Transaction Date,Post Date,Description,Category,Type,Amount,Memo
09/21/2025,09/22/2025,STARBUCKS,Food & Drink,Sale,-4.50,
09/20/2025,09/21/2025,AMAZON.COM,Shopping,Sale,-45.99,
09/19/2025,09/20/2025,RETURN REFUND,Shopping,Return,25.00,
```

**Column Meanings:**
- **Transaction Date**: Date of purchase
- **Post Date**: Date posted to account
- **Description**: Merchant name
- **Category**: Chase's category (optional)
- **Type**: Sale, Return, Payment, etc.
- **Amount**: Negative for purchases, positive for refunds

**Notes:**
- Uses Transaction Date as the primary date
- Type is stored in transaction notes
- Amounts already have correct signs

---

### 4. Generic Format (Fallback)

**Format Detection:** Requires `Date`, `Description`, and either `Amount` OR `Debit`/`Credit`

**CSV Structure Option 1 (Single Amount):**
```csv
Date,Description,Amount
2025-01-15,Starbucks Coffee,-4.50
2025-01-16,Amazon.com,-45.99
2025-01-17,Paycheck Deposit,2500.00
```

**CSV Structure Option 2 (Debit/Credit):**
```csv
Date,Description,Debit,Credit
2025-01-15,Starbucks Coffee,4.50,
2025-01-16,Amazon Return,,25.00
```

**Supported Date Formats:**
- YYYY-MM-DD (2025-01-15)
- MM/DD/YYYY (01/15/2025)
- DD/MM/YYYY (15/01/2025)
- YYYY/MM/DD (2025/01/15)
- MM-DD-YYYY (01-15-2025)
- DD-MM-YYYY (15-01-2025)

---

## 🔜 Coming Soon

The following banks/cards can be easily added:

### American Express
```csv
Date,Description,Amount
```

### Bank of America
```csv
Posted Date,Payee,Address,Amount
```

### Capital One
```csv
Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
```

### Discover
```csv
Trans. Date,Post Date,Description,Amount,Category
```

### Wells Fargo
```csv
Date,Amount,*,*,Name,Memo
```

---

## 🛠️ Adding Your Bank

If your bank isn't supported, you can easily add a parser:

### 1. Create a New Parser Class

Edit `app/csv_parsers.py` and add a new parser class:

```python
class YourBankParser(CSVParser):
    """Parser for YourBank statements"""
    
    def detect(self, csv_content: str) -> bool:
        """Detect YourBank format by checking headers"""
        csv_data = StringIO(csv_content)
        reader = csv.DictReader(csv_data)
        headers = [h.lower().strip() for h in reader.fieldnames]
        
        # Check for unique column names from your bank
        return 'unique_column' in headers
    
    def parse(self, csv_content: str) -> List[Dict]:
        """Parse YourBank CSV format"""
        # Your parsing logic here
        # Return list of dicts with: date, description, amount
        pass
```

### 2. Register the Parser

Add your parser to the `CSVParserFactory` in `csv_parsers.py`:

```python
def __init__(self):
    self.parsers = [
        YourBankParser(),  # Add your parser
        CitibankParser(),
        ChaseParser(),
        GenericParser(),  # Keep Generic last
    ]
```

### 3. Test It

Upload a sample CSV from your bank and check the logs to verify parsing.

---

## 📊 Export Your Data

To get CSV from your bank/credit card:

### Citibank
1. Log in to Citibank online
2. Go to "Account Activity"
3. Select date range
4. Click "Download" → "Comma Delimited"

### Chase
1. Log in to Chase.com
2. Go to "Activity"
3. Select "Download"
4. Choose "CSV" format

### Most Banks
1. Look for "Download", "Export", or "Activity" sections
2. Select CSV or Excel format
3. Choose your date range
4. Download and upload to Mintly

---

## 💡 Tips

1. **Download Monthly**: Export statements at the end of each month
2. **Check Format**: Open CSV in a text editor to verify format
3. **Date Range**: Start with 1-2 months to test
4. **Multiple Accounts**: You can upload CSVs from different banks
5. **Combine Accounts**: All transactions go into one database

---

## 🐛 Troubleshooting

**"No valid transactions found"**
- Check that your CSV has headers
- Verify date format is recognized
- Ensure Amount or Debit/Credit columns exist

**"File must be a CSV"**
- Make sure file extension is `.csv`
- Don't upload Excel (.xlsx) files directly
- Convert Excel to CSV first if needed

**Wrong amounts/signs**
- Check logs to see which parser was detected
- Verify parser logic matches your bank's convention
- May need to create custom parser for your bank

---

## 📝 Request Support for Your Bank

Don't see your bank listed? Open an issue with:
1. Bank name
2. Sample CSV (with sensitive data removed)
3. Column headers from your statement

We'll add support for it!

