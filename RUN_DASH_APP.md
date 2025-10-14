# 🚀 How to Run the Dash Interactive Reports

## Quick Start

### Method 1: Standalone (Outside Docker) - **Easiest!**

1. **Activate your Python environment:**
   ```bash
   cd /Users/ndurga00/git/mintly_app
   
   # If using venv:
   # source venv/bin/activate
   
   # Or just use your system Python with the packages installed
   ```

2. **Run the standalone Dash app:**
   ```bash
   python run_dash_standalone.py
   ```

3. **Open in browser:**
   ```
   http://localhost:8050
   ```

That's it! The Dash app will connect to your existing DuckDB database and show all your transactions with interactive filters.

---

### Method 2: Add to Docker (Run Alongside Backend & Frontend)

If you want the Dash app to run as part of your Docker setup:

#### Step 1: Update `docker-compose.yml`

Add this service:

```yaml
  dash:
    build:
      context: .
      dockerfile: Dockerfile
      target: backend
    container_name: mintly_dash
    command: python run_dash_standalone.py
    ports:
      - "8050:8050"
    volumes:
      - ./app:/app/app
      - ./data:/app/data
      - ./run_dash_standalone.py:/app/run_dash_standalone.py
    networks:
      - mintly_network
    depends_on:
      - backend
```

#### Step 2: Restart Docker

```bash
docker-compose down
docker-compose up --build
```

#### Step 3: Access All Services

- **Backend:** http://localhost:8000
- **React Frontend:** http://localhost:3000
- **Dash Reports:** http://localhost:8050 ⭐

---

## Features Available in Dash App

✅ **Date Range Presets**
   - MTD (Month to Date)
   - YTD (Year to Date)
   - QTD (Quarter to Date)
   - 30 Days
   - 60 Days
   - 90 Days

✅ **Category Filters**
   - Multi-select dropdown
   - Filter charts and table

✅ **Interactive Charts**
   - Spending by Category (Pie Chart)
   - Category Breakdown (Bar Chart)
   - Daily Spending Trend (Line Chart)
   - Top 10 Merchants (Bar Chart)

✅ **Transaction Table**
   - Sortable columns
   - Built-in search
   - Color-coded (red for expenses, green for income)

✅ **Summary Cards**
   - Total Spending
   - Transaction Count
   - Average Transaction

---

## Troubleshooting

### Port 8050 Already in Use

```bash
# Find what's using port 8050
lsof -i :8050

# Kill the process (replace PID with actual number)
kill -9 PID
```

### Database Not Found

Make sure your backend has created the DuckDB database:

```bash
# Check if database exists
ls -la data/

# You should see: transactions.db
```

### Missing Python Packages

```bash
pip install dash dash-bootstrap-components pandas plotly
```

---

## Comparison: Dash vs React vs Python Reports

| Feature | Dash App (8050) | React (3000) | Python (8000) |
|---------|----------------|--------------|---------------|
| Date Presets | ✅ | ✅ | ❌ |
| Category Filters | ✅ Dropdown | ✅ Checkboxes | ❌ |
| Chart Library | Plotly | Recharts | Plotly |
| Real-time Updates | ✅ | ✅ | ❌ |
| Port | 8050 | 3000 | 8000 |
| Run Without Docker | ✅ Easy | ❌ Needs build | ✅ |

---

## Quick Test

Once the Dash app is running, try this:

1. ✅ Click **"MTD"** button - see Month to Date data
2. ✅ Click **"YTD"** button - see Year to Date data
3. ✅ Select categories from dropdown - charts update instantly
4. ✅ Hover over charts for details
5. ✅ Sort table columns by clicking headers

---

## Why Run Dash Standalone?

**Pros:**
- ✅ No WSGIMiddleware issues
- ✅ Full Dash features work perfectly
- ✅ Easier to debug
- ✅ Can run on different port

**Cons:**
- ❌ One more service to manage
- ❌ Need to open another port

**Recommendation:** 
Use **React frontend (port 3000)** for production, but run **Dash standalone (port 8050)** when you want the full Plotly+Dash experience!

---

## Pro Tip: Run All Three! 🎉

```bash
# Terminal 1: Backend
cd /Users/ndurga00/git/mintly_app
docker-compose up backend

# Terminal 2: Frontend
docker-compose up frontend

# Terminal 3: Dash
python run_dash_standalone.py
```

Now you have:
- ✅ Backend API: http://localhost:8000
- ✅ React UI: http://localhost:3000
- ✅ Dash Reports: http://localhost:8050

Three different ways to view your data! 🚀

