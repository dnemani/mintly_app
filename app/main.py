"""
Main FastAPI application for Mintly budgeting app
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.wsgi import WSGIMiddleware
import os
import uvicorn
import logging
from datetime import datetime
from pathlib import Path

from app.api import transactions, reports, tags
from app.csv_parsers import CSVParserFactory
from app.categorizer import categorizer
from app.db_instance import db_manager

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s|%(levelname)s|%(name)s|%(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mintly - Personal Budgeting App",
    description="Track and categorize your spending from credit card statements",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(transactions.router)
app.include_router(reports.router)
app.include_router(tags.router)

# Note: Dash integration has technical limitations with FastAPI's WSGIMiddleware
# For interactive reports with filters and date presets, use the React frontend at port 3000
dash_initialized = False
logger.info("ℹ️  For interactive reports, use React frontend (port 3000) or Python reports (port 8000)")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with upload interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports and analytics page (static Plotly)"""
    return templates.TemplateResponse("reports.html", {"request": request})


@app.get("/dash", response_class=HTMLResponse)
@app.get("/dash/", response_class=HTMLResponse)
async def interactive_reports_info(request: Request):
    """Show interactive reports options"""
    return templates.TemplateResponse("dash_alternative.html", {"request": request})


@app.get("/transactions", response_class=HTMLResponse)
async def transactions_page(request: Request):
    """Transaction management page"""
    return templates.TemplateResponse("transactions.html", {"request": request})


@app.get("/bulk-edit", response_class=HTMLResponse)
async def bulk_edit_page(request: Request):
    """Bulk edit transactions page"""
    return templates.TemplateResponse("bulk_edit.html", {"request": request})


def _load_sample_file(csv_file, db_manager, parser_factory, categorizer):
    """Load a single sample CSV file into the database. Returns the count loaded, or 0 on failure."""
    try:
        csv_content = csv_file.read_text(encoding="utf-8")
        transactions = parser_factory.parse(csv_content)
        if not transactions:
            logger.warning(f"No transactions found in {csv_file.name}")
            return 0

        categorized_transactions = categorizer.categorize_batch(transactions)
        count = db_manager.insert_transactions_batch(categorized_transactions)
        return count
    except Exception as e:
        logger.error(f"Failed to load {csv_file.name}: {e}")
        return 0


@app.on_event("startup")
async def seed_sample_data():
    """Seed sample transactions if database is empty or has few records."""
    if os.environ.get("LOAD_SAMPLES") != "true":
        logger.debug("LOAD_SAMPLES not set, skipping seed data.")
        return

    sample_dir = Path(__file__).resolve().parent.parent
    sample_files = [f for f in sample_dir.glob("sample_*.csv")]

    # Check if database already has data
    df = db_manager.get_all_transactions()
    if len(df) >= 5:
        logger.info(f"Database already has {len(df)} transactions, skipping seed.")
        return

    logger.info(f"Database has {len(df)} transactions, loading sample data...")

    total_loaded = 0
    for csv_file in sorted(sample_files):
        count = _load_sample_file(csv_file, db_manager, CSVParserFactory(), categorizer)
        if count > 0:
            total_loaded += count
            logger.info(f"✓ Loaded {count} transactions from {csv_file.name}")

    logger.info(f"Seed complete: {total_loaded} transactions loaded from {len(sample_files)} file(s).")



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "dash_enabled": dash_initialized,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    logger.info("Starting Mintly application...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

