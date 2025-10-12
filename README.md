# 💰 Mintly - Personal Budgeting App

A complete, production-ready Python-based personal budgeting application that helps you track and categorize your spending from credit card statements.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal.svg)

## ✨ Features

- 📤 **CSV Import**: Upload credit card statements in CSV format
- 🤖 **Auto-Categorization**: Automatically categorize transactions based on 100+ merchant patterns
- ✂️ **Transaction Splitting**: Split transactions across multiple categories
- 📊 **Visual Reports**: Interactive Plotly charts showing spending by category
- 💾 **DuckDB Storage**: Efficient local database storage with full privacy
- 🌐 **Web Interface**: Beautiful, responsive web interface for all operations
- 🐳 **Docker Ready**: One-command deployment with Docker Compose

## Tech Stack

- **Backend**: FastAPI
- **Data Processing**: Polars, PyArrow
- **Database**: DuckDB
- **Visualization**: Plotly
- **Data Validation**: Pydantic 2.0

## 🚀 Quick Start

Mintly offers **two frontend options**:
- **React Frontend** (Modern SPA) - Port 3000
- **Python/Jinja2 Frontend** (Original) - Port 8000

### Option 1: Using Docker with React Frontend (Recommended)

```bash
docker-compose up --build
```

**Access the app:**
- **React UI**: http://localhost:3000 (Modern, interactive)
- **Python UI**: http://localhost:8000 (Original, simple)
- **API Docs**: http://localhost:8000/docs

### Option 2: Python Backend Only

```bash
docker-compose up backend
```

Access at: **http://localhost:8000**

### Option 3: Local Development

**Backend:**
```bash
pip install -r requirements.txt
python app/main.py
```

**Frontend (optional):**
```bash
cd frontend
npm install
npm run dev
```

### Try it with Sample Data

1. Start the application
2. Navigate to http://localhost:8000
3. Upload the included `sample_transactions.csv`
4. Explore the auto-categorized transactions and reports!

## Project Structure

```
mintly_app/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic data models
│   ├── database.py          # DuckDB utilities
│   ├── categorizer.py       # Transaction categorization logic
│   ├── api/                 # API endpoints
│   │   ├── transactions.py
│   │   └── reports.py
│   ├── static/              # CSS, JS files
│   └── templates/           # HTML templates
├── data/                    # Database and uploaded files
├── logs/                    # Application logs
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Usage

1. **Upload Transactions**: Navigate to the home page and upload your CSV file
2. **Review Categories**: Check auto-categorized transactions and adjust if needed
3. **Split Transactions**: For mixed purchases, split amounts across categories
4. **View Reports**: Access interactive charts and spending analysis

## Supported CSV Formats

The app automatically detects and parses statements from multiple banks:

### 🏦 Costco Visa
```csv
Status,Date,Description,Debit,Credit,Member Name
Cleared,10/05/2025,COSTCO WHOLESALE,234.56,,John Doe
Cleared,09/28/2025,PAYMENT,,500.00,John Doe
```

### 🏦 Citibank
```csv
Status,Date,Description,Debit,Credit
Cleared,09/21/2025,"THE HOME DEPOT",199.99,
Cleared,09/22/2025,"TARGET RETURN",,50.00
```

### 🏦 Chase
```csv
Transaction Date,Post Date,Description,Category,Type,Amount
09/21/2025,09/22/2025,STARBUCKS,Food & Drink,Sale,-4.50
```

### 🏦 Generic Format
```csv
Date,Description,Amount
2025-01-15,Starbucks Coffee,-4.50
2025-01-16,Amazon.com,-45.99
```

**The app will automatically detect your bank's format!** See [BANKS_SUPPORTED.md](BANKS_SUPPORTED.md) for details.

## 📚 Documentation

- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - Guide to React vs Python frontend
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview and technical details
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive user guide with examples
- **[BANKS_SUPPORTED.md](BANKS_SUPPORTED.md)** - List of supported banks and how to add more
- **[frontend/README.md](frontend/README.md)** - React frontend documentation
- **API Docs** - Interactive API documentation at http://localhost:8000/docs

## 🎯 What Can You Do?

### Upload & Categorize
Upload your credit card statement CSV and watch as transactions are automatically categorized into 15 different categories (Groceries, Restaurants, Transportation, etc.)

### Split Transactions
Had a mixed purchase at Target? Split it into "Groceries" and "Personal Care" with just a few clicks.

### Analyze Spending
View beautiful interactive charts:
- 🥧 Pie chart: Overall spending distribution
- 📊 Bar chart: Category breakdown
- 📈 Line chart: Daily spending trends

### Stay Private
All data stays local on your machine. No cloud services, no data sharing.

## 🛠️ Built With

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern web framework
- **[DuckDB](https://duckdb.org/)** - Embedded analytical database
- **[Polars](https://pola-rs.github.io/polars/)** - Fast DataFrames
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation
- **[Plotly](https://plotly.com/python/)** - Interactive visualizations

### Frontend Options
- **[React 18](https://react.dev/)** - Modern UI library
- **[Vite](https://vitejs.dev/)** - Fast build tool
- **[Recharts](https://recharts.org/)** - React charts
- **Jinja2** - Python templating (original)

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built following Python best practices and workspace rules for data processing, logging, and performance optimization.

