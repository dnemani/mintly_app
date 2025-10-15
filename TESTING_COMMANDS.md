# 🧪 Mintly App Testing Commands

This document provides comprehensive testing commands for the Mintly budgeting application, covering all deployment methods and testing scenarios.

## 📋 Table of Contents

- [Quick Health Checks](#-quick-health-checks)
- [Docker Testing](#-docker-testing)
- [Local Development Testing](#-local-development-testing)
- [API Endpoint Testing](#-api-endpoint-testing)
- [Frontend Testing](#-frontend-testing)
- [Database Testing](#-database-testing)
- [Performance Testing](#-performance-testing)
- [Troubleshooting Commands](#-troubleshooting-commands)

---

## 🏥 Quick Health Checks

### Basic Health Check
```bash
# Check if backend is running and healthy
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "dash_enabled": false,
#   "timestamp": "2025-01-15T10:30:00.000000"
# }
```

### Port Availability Check
```bash
# Check which ports are in use
lsof -i :8000  # Backend
lsof -i :3000  # React Frontend
lsof -i :8050  # Dash Reports

# Kill process on specific port (replace PID)
kill -9 <PID>
```

### Service Status Check
```bash
# Check Docker containers
docker ps

# Check specific container logs
docker logs mintly_backend
docker logs mintly_frontend
docker logs mintly_dash
```

---

## 🐳 Docker Testing

### Full Stack Testing (Recommended)
```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up --build -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart dash
```

### Individual Service Testing
```bash
# Backend only
docker-compose up backend

# Frontend only (requires backend)
docker-compose up frontend

# Dash reports only (requires backend)
docker-compose up dash
```

### Docker Health Monitoring
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f dash

# Check container health
docker-compose ps
```

### Docker Cleanup
```bash
# Remove containers and networks
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Rebuild from scratch
docker-compose down
docker-compose up --build --force-recreate
```

---

## 💻 Local Development Testing

### Backend Testing
```bash
# Using the provided script
./run_local.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

### Frontend Testing
```bash
# React frontend
cd frontend
npm install
npm run dev

# Check if frontend is running
curl http://localhost:3000
```

### Dash Reports Testing
```bash
# Run standalone Dash app
python run_dash_standalone.py

# Check if Dash is running
curl http://localhost:8050
```

---

## 🔌 API Endpoint Testing

### Transaction Endpoints
```bash
# Upload CSV file
curl -X POST "http://localhost:8000/api/transactions/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_transactions.csv"

# List transactions
curl "http://localhost:8000/api/transactions/list?limit=10"

# Get transaction by ID
curl "http://localhost:8000/api/transactions/1"

# Update transaction category
curl -X PUT "http://localhost:8000/api/transactions/1/category" \
  -H "Content-Type: application/json" \
  -d '{"category": "Groceries"}'

# Split transaction
curl -X POST "http://localhost:8000/api/transactions/1/split" \
  -H "Content-Type: application/json" \
  -d '{"splits": [{"amount": 50.0, "category": "Groceries"}, {"amount": 25.0, "category": "Personal Care"}]}'

# Delete transaction
curl -X DELETE "http://localhost:8000/api/transactions/1"
```

### Reports Endpoints
```bash
# Get spending summary
curl "http://localhost:8000/api/reports/summary"

# Get category pie chart data
curl "http://localhost:8000/api/reports/chart/category-pie"

# Get daily trend data
curl "http://localhost:8000/api/reports/chart/daily-trend"

# Get top merchants
curl "http://localhost:8000/api/reports/chart/top-merchants"
```

### Tags Endpoints
```bash
# Get all tags
curl "http://localhost:8000/api/tags/"

# Create new tag
curl -X POST "http://localhost:8000/api/tags/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work", "color": "#FF5733"}'

# Update tag
curl -X PUT "http://localhost:8000/api/tags/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work Expenses", "color": "#33FF57"}'

# Delete tag
curl -X DELETE "http://localhost:8000/api/tags/1"
```

### API Documentation
```bash
# Open interactive API docs
open http://localhost:8000/docs

# Open alternative docs
open http://localhost:8000/redoc
```

---

## 🎨 Frontend Testing

### React Frontend (Port 3000)
```bash
# Test main page
curl http://localhost:3000

# Test API connectivity from frontend
# Open browser console and check for network errors
# Visit: http://localhost:3000
```

### Python Frontend (Port 8000)
```bash
# Test main page
curl http://localhost:8000

# Test reports page
curl http://localhost:8000/reports

# Test transactions page
curl http://localhost:8000/transactions
```

### Dash Reports (Port 8050)
```bash
# Test Dash app
curl http://localhost:8050

# Test specific Dash endpoints
curl http://localhost:8050/_dash-layout
curl http://localhost:8050/_dash-dependencies
```

### Frontend Integration Testing
```bash
# Test file upload functionality
# 1. Open http://localhost:8000 in browser
# 2. Upload sample_transactions.csv
# 3. Verify transactions appear

# Test React frontend
# 1. Open http://localhost:3000 in browser
# 2. Check if data loads from backend
# 3. Test interactive features
```

---

## 🗄️ Database Testing

### DuckDB Testing
```bash
# Connect to database directly
duckdb data/mintly.db

# Run SQL queries
.tables
SELECT COUNT(*) FROM transactions;
SELECT * FROM transactions LIMIT 5;
SELECT category, COUNT(*) FROM transactions GROUP BY category;
.quit
```

### Database File Checks
```bash
# Check if database exists
ls -la data/

# Check database size
du -h data/mintly.db

# Check database integrity
duckdb data/mintly.db "PRAGMA integrity_check;"
```

### Data Validation
```bash
# Count transactions by category
duckdb data/mintly.db "SELECT category, COUNT(*) as count FROM transactions GROUP BY category ORDER BY count DESC;"

# Check date ranges
duckdb data/mintly.db "SELECT MIN(date) as earliest, MAX(date) as latest FROM transactions;"

# Check for duplicates
duckdb data/mintly.db "SELECT description, date, amount, COUNT(*) as count FROM transactions GROUP BY description, date, amount HAVING COUNT(*) > 1;"
```

---

## ⚡ Performance Testing

### Load Testing
```bash
# Test API response times
time curl http://localhost:8000/health

# Test with multiple requests
for i in {1..10}; do
  curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/transactions/list
done

# Create curl-format.txt for timing
cat > curl-format.txt << EOF
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF
```

### Memory Usage Testing
```bash
# Check container memory usage
docker stats

# Check specific container
docker stats mintly_backend

# Check Python process memory
ps aux | grep python
```

### Database Performance
```bash
# Test query performance
time duckdb data/mintly.db "SELECT * FROM transactions WHERE category = 'Groceries';"

# Test with large dataset
duckdb data/mintly.db "EXPLAIN SELECT category, SUM(amount) FROM transactions GROUP BY category;"
```

---

## 🔧 Troubleshooting Commands

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000
lsof -i :3000
lsof -i :8050

# Kill process
kill -9 <PID>

# Or kill all processes on port
sudo lsof -ti:8000 | xargs kill -9
```

#### Docker Issues
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Reset Docker Compose
docker-compose down -v
docker-compose up --build --force-recreate
```

#### Database Lock Issues
```bash
# Check for database locks
duckdb data/mintly.db "PRAGMA database_list;"

# If locked, restart backend
docker-compose restart backend
```

#### Missing Dependencies
```bash
# Reinstall Python dependencies
pip install -r requirements.txt

# Reinstall Node dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Log Analysis
```bash
# View application logs
tail -f logs/app_*.log

# View Docker logs with timestamps
docker-compose logs -f -t

# Search logs for errors
grep -i error logs/app_*.log
grep -i exception logs/app_*.log
```

### Network Testing
```bash
# Test internal Docker networking
docker exec mintly_frontend curl http://backend:8000/health

# Test external connectivity
curl -I http://localhost:8000
curl -I http://localhost:3000
curl -I http://localhost:8050
```

---

## 🎯 Test Scenarios

### Complete Workflow Test
```bash
# 1. Start all services
docker-compose up --build -d

# 2. Wait for services to be ready
sleep 30

# 3. Test health
curl http://localhost:8000/health

# 4. Upload sample data
curl -X POST "http://localhost:8000/api/transactions/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_transactions.csv"

# 5. Verify data
curl "http://localhost:8000/api/transactions/list?limit=5"

# 6. Test reports
curl "http://localhost:8000/api/reports/summary"

# 7. Test frontends
open http://localhost:3000  # React
open http://localhost:8000  # Python
open http://localhost:8050  # Dash
```

### Error Handling Test
```bash
# Test invalid file upload
curl -X POST "http://localhost:8000/api/transactions/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@README.md"

# Test invalid transaction ID
curl "http://localhost:8000/api/transactions/99999"

# Test invalid category update
curl -X PUT "http://localhost:8000/api/transactions/1/category" \
  -H "Content-Type: application/json" \
  -d '{"category": "InvalidCategory"}'
```

---

## 📊 Monitoring Commands

### Real-time Monitoring
```bash
# Monitor all logs
docker-compose logs -f

# Monitor specific service
docker-compose logs -f backend | grep -E "(ERROR|WARN|INFO)"

# Monitor system resources
htop
# or
top
```

### Database Monitoring
```bash
# Monitor database queries
duckdb data/mintly.db "PRAGMA table_info(transactions);"

# Check database statistics
duckdb data/mintly.db "SELECT COUNT(*) as total_transactions, MIN(date) as earliest, MAX(date) as latest FROM transactions;"
```

---

## 🚀 Production Testing

### Pre-deployment Checklist
```bash
# 1. Run all health checks
curl http://localhost:8000/health

# 2. Test all API endpoints
curl http://localhost:8000/api/transactions/list
curl http://localhost:8000/api/reports/summary

# 3. Test frontend connectivity
curl -I http://localhost:3000
curl -I http://localhost:8000

# 4. Verify database integrity
duckdb data/mintly.db "PRAGMA integrity_check;"

# 5. Check logs for errors
grep -i error logs/app_*.log | tail -10
```

### Performance Benchmarks
```bash
# API response time test
time curl -s http://localhost:8000/api/transactions/list > /dev/null

# Database query performance
time duckdb data/mintly.db "SELECT category, SUM(amount) FROM transactions GROUP BY category;" > /dev/null

# Frontend load time
time curl -s http://localhost:3000 > /dev/null
```

---

## 📝 Notes

- All commands assume you're in the project root directory (`/Users/ndurga00/git/mintly_app`)
- Replace `localhost` with your server IP for remote testing
- Use `-v` flag with curl for verbose output when debugging
- Check `logs/` directory for detailed application logs
- Use `docker-compose logs -f` for real-time container monitoring

---

## 🔗 Related Documentation

- [README.md](README.md) - Main project documentation
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Detailed usage instructions
- [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) - Frontend testing guide
- [DASH_REPORTS_GUIDE.md](DASH_REPORTS_GUIDE.md) - Dash reports testing
