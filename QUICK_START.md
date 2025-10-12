# Mintly Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Start the App

```bash
docker-compose up --build
```

Wait for the containers to build (~2 minutes first time).

### Step 2: Open the App

Choose your frontend:

**Modern React UI (Recommended)**
```
http://localhost:3000
```

**Original Python UI**
```
http://localhost:8000
```

### Step 3: Upload Your First CSV

1. Click "Upload" or navigate to home page
2. Choose a CSV file:
   - Use included `sample_costco_visa.csv` or `sample_citibank.csv`
   - Or export your own from your bank
3. Click "Upload & Process"
4. Watch transactions auto-categorize!

### Step 4: Explore Features

#### View Transactions
- Click "Transactions" in navigation
- Change categories with dropdowns
- Click "Split" to divide multi-category purchases
- Click "Delete" to remove unwanted entries

#### View Reports
- Click "Reports" in navigation
- Select date range
- Click "Generate Report"
- See pie charts, bar charts, and summaries

---

## 📊 Supported Banks

The app auto-detects these formats:

- **Costco Visa** ✅
- **Citibank** ✅
- **Chase** ✅
- **Generic CSV** ✅

Just upload your CSV - no configuration needed!

---

## 🎯 Common Tasks

### Export CSV from Your Bank

#### Costco Visa (Citibank)
1. Log in to Citibank.com
2. Navigate to your Costco Visa account
3. Click "Download" → "Year to Date" → "Comma Delimited"

#### Chase
1. Log in to Chase.com
2. Go to "Activity"
3. Select date range
4. Click "Download" → "CSV"

#### Other Banks
Look for "Export", "Download", or "Activity" sections.

### Split a Transaction

Example: You bought groceries AND household items at Target for $150.

1. Find the transaction in "Transactions" page
2. Click "Split" button
3. Add splits:
   - Groceries: $100
   - Shopping: $50
4. Click "Save Split"

### Change Categories

If auto-categorization is wrong:

1. Go to "Transactions" page
2. Use the dropdown to select correct category
3. Changes save automatically!

### View Monthly Report

1. Go to "Reports" page
2. Set Start Date: Beginning of month
3. Set End Date: End of month
4. Click "Generate Report"
5. See your spending breakdown!

---

## 🐛 Troubleshooting

### "Connection refused" Error

**Problem:** Can't connect to http://localhost:3000 or http://localhost:8000

**Solution:**
```bash
# Check if containers are running
docker ps

# If not, start them
docker-compose up
```

### CSV Upload Fails

**Problem:** "No valid transactions found"

**Solutions:**
1. Check CSV has headers: `Date`, `Description`, `Amount` (or `Debit`/`Credit`)
2. Open CSV in text editor to verify format
3. Make sure dates are in format MM/DD/YYYY or YYYY-MM-DD
4. Check that file extension is `.csv` (not `.xlsx`)

### Transactions Not Showing

**Problem:** Uploaded but nothing appears

**Solutions:**
1. Click "Refresh" button
2. Check browser console for errors (F12)
3. Restart containers: `docker-compose restart`

### Charts Not Loading

**Problem:** Reports page shows no data

**Solutions:**
1. Verify you have transactions in the date range
2. Check that transactions are categorized
3. Reload the page

---

## 💡 Tips

1. **Upload Regularly**: Import statements monthly for best tracking
2. **Review Categories**: Check auto-categorization and adjust
3. **Use Splits**: Split mixed purchases for accurate reporting
4. **Set Date Ranges**: Use specific ranges for targeted insights
5. **Export Backup**: Your data is in `data/mintly.db` - back it up!

---

## 🎓 Next Steps

### Learn More
- Read **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - Compare React vs Python UI
- Read **[BANKS_SUPPORTED.md](BANKS_SUPPORTED.md)** - Add your bank
- Check **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Advanced features

### Customize
- Edit categories in `app/models.py`
- Add merchant patterns in `app/categorizer.py`
- Create custom bank parser in `app/csv_parsers.py`

### Contribute
- Report bugs on GitHub
- Request bank support
- Submit pull requests

---

## ⚡ Quick Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart after code changes
docker-compose restart

# Rebuild after dependency changes
docker-compose up --build

# Stop only frontend
docker-compose stop frontend

# Stop only backend
docker-compose stop backend

# Clear database (fresh start)
rm data/mintly.db
docker-compose restart
```

---

## 🎉 You're Ready!

Start uploading your transactions and take control of your finances!

Questions? Check the [README.md](README.md) or [USAGE_GUIDE.md](USAGE_GUIDE.md).

