"""
API endpoints for reports and analytics
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
import logging

from app.db_instance import db_manager
from app.models import SpendingReport, CategorySummary

router = APIRouter(prefix="/api/reports", tags=["reports"])
logger = logging.getLogger(__name__)


@router.get("/summary")
async def get_spending_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get spending summary for a date range"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            # Default to current month
            end_dt = datetime.now()
            start_dt = end_dt.replace(day=1)
        
        # Get transactions
        df = db_manager.get_transactions_by_date_range(start_dt, end_dt)
        
        if len(df) == 0:
            return {
                "status": "success",
                "report": {
                    "start_date": start_dt.isoformat(),
                    "end_date": end_dt.isoformat(),
                    "total_spent": 0,
                    "total_income": 0,
                    "net_balance": 0,
                    "categories": []
                }
            }
        
        # Filter out split parent transactions (only count the splits)
        df_for_calc = df.filter(pl.col('is_split') == False)
        
        # Calculate totals
        expenses = df_for_calc.filter(pl.col('amount') < 0)
        income = df_for_calc.filter(pl.col('amount') > 0)
        
        total_spent = abs(expenses['amount'].sum()) if len(expenses) > 0 else 0
        total_income = income['amount'].sum() if len(income) > 0 else 0
        net_balance = total_income - total_spent
        
        # Get category breakdown
        category_df = db_manager.get_category_summary(start_dt, end_dt)
        
        # Filter to only expenses for category summary
        category_df = category_df.filter(pl.col('total_amount') < 0)
        
        categories = []
        for row in category_df.iter_rows(named=True):
            categories.append({
                "category": row['category'],
                "total_amount": abs(row['total_amount']),
                "transaction_count": row['transaction_count'],
                "percentage": row.get('percentage', 0)
            })
        
        report = {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "total_spent": float(total_spent),
            "total_income": float(total_income),
            "net_balance": float(net_balance),
            "categories": categories
        }
        
        return {
            "status": "success",
            "report": report
        }
    
    except Exception as e:
        logger.error(f"Error generating spending summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/chart/category-pie")
async def get_category_pie_chart(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Generate a pie chart of spending by category"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.now()
            start_dt = end_dt.replace(day=1)
        
        # Get category summary
        category_df = db_manager.get_category_summary(start_dt, end_dt)
        
        # Filter to only expenses
        category_df = category_df.filter(pl.col('total_amount') < 0)
        
        if len(category_df) == 0:
            return JSONResponse(content={"error": "No data available for the selected period"})
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=category_df['category'].to_list(),
            values=[abs(x) for x in category_df['total_amount'].to_list()],
            hole=0.3,
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f"Spending by Category ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')})",
            showlegend=True,
            height=500
        )
        
        return JSONResponse(content=fig.to_json())
    
    except Exception as e:
        logger.error(f"Error generating pie chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")


@router.get("/chart/spending-trend")
async def get_spending_trend_chart(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Generate a line chart showing spending trends over time"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=90)  # Last 3 months
        
        # Get transactions
        df = db_manager.get_transactions_by_date_range(start_dt, end_dt)
        
        if len(df) == 0:
            return JSONResponse(content={"error": "No data available for the selected period"})
        
        # Filter expenses only and non-split parents
        df = df.filter(
            (pl.col('amount') < 0) & 
            (pl.col('is_split') == False)
        )
        
        # Group by date and calculate daily spending
        df = df.with_columns(
            pl.col('date').cast(pl.Date).alias('date_only')
        )
        
        daily_spending = df.group_by('date_only').agg(
            pl.col('amount').sum().abs().alias('total_spent')
        ).sort('date_only')
        
        # Create line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_spending['date_only'].to_list(),
            y=daily_spending['total_spent'].to_list(),
            mode='lines+markers',
            name='Daily Spending',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=6),
            hovertemplate='<b>Date:</b> %{x}<br><b>Spent:</b> $%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"Daily Spending Trend ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')})",
            xaxis_title="Date",
            yaxis_title="Amount Spent ($)",
            hovermode='x unified',
            height=400
        )
        
        return JSONResponse(content=fig.to_json())
    
    except Exception as e:
        logger.error(f"Error generating trend chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")


@router.get("/chart/category-bar")
async def get_category_bar_chart(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Generate a bar chart of spending by category"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.now()
            start_dt = end_dt.replace(day=1)
        
        # Get category summary
        category_df = db_manager.get_category_summary(start_dt, end_dt)
        
        # Filter to only expenses and sort by amount
        category_df = category_df.filter(pl.col('total_amount') < 0)
        category_df = category_df.sort('total_amount')
        
        if len(category_df) == 0:
            return JSONResponse(content={"error": "No data available for the selected period"})
        
        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=[abs(x) for x in category_df['total_amount'].to_list()],
            y=category_df['category'].to_list(),
            orientation='h',
            marker=dict(color='#4ECDC4'),
            hovertemplate='<b>%{y}</b><br>Amount: $%{x:.2f}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f"Spending by Category ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')})",
            xaxis_title="Amount Spent ($)",
            yaxis_title="Category",
            height=500
        )
        
        return JSONResponse(content=fig.to_json())
    
    except Exception as e:
        logger.error(f"Error generating bar chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")

