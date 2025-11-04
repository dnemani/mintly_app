# Testing Shiny Reports

This guide provides instructions for testing the new Shiny interactive reports feature.

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.10+ with virtualenv

## Option 1: Test with Docker (Recommended)

### Build and run all services including Shiny

```bash
# Build and start all services
docker-compose up --build

# Or start only backend and shiny services
docker-compose up backend shiny
```

### Access Shiny Reports

Once the containers are running, access Shiny reports at:
- **Shiny Reports**: http://localhost:8051

### Verify Shiny is running

```bash
# Check container status
docker ps | grep mintly_shiny

# Check Shiny logs
docker logs mintly_shiny

# Test health (after data is loaded)
curl http://localhost:8051
```

## Option 2: Test with Local Virtual Environment

### Create and activate virtual environment

```bash
# Create venv in project folder
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run backend and Shiny separately

```bash
# Terminal 1: Start backend
python app/main.py

# Terminal 2: Start Shiny (after activating venv)
shiny run --host 0.0.0.0 --port 8051 run_shiny_standalone.py
```

### Access Shiny Reports

- **Backend API**: http://localhost:8000
- **Shiny Reports**: http://localhost:8051

## Testing Checklist

### 1. Upload Test Data

First, upload some transaction data via the backend:

```bash
curl -X POST "http://localhost:8000/api/transactions/upload" \
  -F "file=@sample_transactions.csv"
```

Or use the web interface at http://localhost:8000

### 2. Verify Shiny Features

Access http://localhost:8051 and test:

- [ ] **Date Range Presets**: Click MTD, YTD, QTD, 30D, 60D, 90D buttons
- [ ] **Custom Date Range**: Use date pickers to select custom ranges
- [ ] **Category Filter**: Select multiple categories from dropdown
- [ ] **Amount Range Slider**: Adjust min/max spending amounts
- [ ] **Summary Cards**: Verify Total Income, Total Expenses, Net Balance, Transaction Count
- [ ] **Charts**:
  - [ ] Spending by Category (pie chart)
  - [ ] Daily Spending Trend (line chart)
  - [ ] Top Merchants (horizontal bar chart)
  - [ ] Category Breakdown (vertical bar chart)
- [ ] **Transaction Table**: Verify data displays with sorting and pagination

### 3. Compare with Dash Reports

Access both reporting interfaces and compare functionality:

- **Dash Reports**: http://localhost:8050
- **Shiny Reports**: http://localhost:8051

Both should show similar data and filtering capabilities.

### 4. Database Isolation

Verify that Shiny uses its own read-only database copy:

```bash
# Check for separate database files
ls -lh data/mintly*.db

# Expected files:
# - mintly.db (main database)
# - mintly_dash.db (Dash copy)
# - mintly_shiny.db (Shiny copy)
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8051
lsof -i :8051

# Kill process if needed
kill -9 <PID>
```

### Database Not Found

If you see "No data available":
1. Ensure backend is running (port 8000)
2. Upload transaction data via `/api/transactions/upload`
3. Restart Shiny service to pick up new data

### Import Errors

If you see `ModuleNotFoundError: No module named 'shiny'`:

**Docker**: Rebuild the image
```bash
docker-compose build shiny
docker-compose up shiny
```

**Local venv**: Reinstall dependencies
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Shiny App Not Starting

Check logs for errors:
```bash
# Docker
docker logs mintly_shiny -f

# Local
# Output will appear in terminal where you ran shiny run
```

## Performance Notes

- Shiny creates a database copy (`mintly_shiny.db`) on startup for read-only access
- This prevents database locking issues when multiple services access the database
- The copy is refreshed each time the Shiny service restarts
- For production, consider implementing a periodic refresh mechanism

## Differences from Dash

Both Dash and Shiny provide similar functionality, but with different frameworks:

| Feature | Dash | Shiny |
|---------|------|-------|
| Framework | Plotly Dash | Shiny for Python |
| Port | 8050 | 8051 |
| Reactive Model | Callback decorators | Reactive decorators |
| UI Components | Dash/Bootstrap | Shiny UI |
| Database | mintly_dash.db | mintly_shiny.db |

## Next Steps

After verifying Shiny works correctly:

1. Upload real credit card statements
2. Test filtering with actual transaction data
3. Verify performance with large datasets (1000+ transactions)
4. Compare user experience between React, Dash, and Shiny frontends
5. Choose your preferred reporting interface for daily use

## Docker Compose Services

All services in docker-compose.yml:

- **backend** (8000): FastAPI backend with transaction management
- **frontend** (3000): React SPA frontend
- **dash** (8050): Dash interactive reports
- **shiny** (8051): Shiny interactive reports (NEW)

Run specific services:
```bash
# Just backend and Shiny
docker-compose up backend shiny

# All services
docker-compose up
```
