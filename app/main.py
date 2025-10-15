"""
Main FastAPI application for Mintly budgeting app
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
import logging
from datetime import datetime
from pathlib import Path

from app.api import transactions, reports, tags

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

