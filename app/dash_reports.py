"""
Interactive Dash Reports with filters and date range presets
Based on https://dash.plotly.com/tutorial
"""
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import logging
from app.database import DatabaseManager
import shutil
import os

# Create a copy of the database for read-only access
def create_db_copy():
    """Create a copy of the database for read-only access"""
    source_db = "data/mintly.db"
    copy_db = "data/mintly_dash.db"
    
    if os.path.exists(source_db):
        shutil.copy2(source_db, copy_db)
        return copy_db
    return source_db

# Initialize database manager with a copy for read-only access
db_copy_path = create_db_copy()
db_manager = DatabaseManager(db_path=db_copy_path, read_only=True)

logger = logging.getLogger(__name__)

# Initialize Dash app with Bootstrap theme
# Configure to work when mounted at /dash/
dash_app = Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                serve_locally=True,
                url_base_pathname='/dash/',
                assets_url_path='/dash/assets/')


def get_date_range_preset(preset):
    """Calculate date ranges for presets"""
    today = datetime.now().date()
    
    if preset == 'mtd':  # Month to Date
        start_date = today.replace(day=1)
        end_date = today
    elif preset == 'ytd':  # Year to Date
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif preset == 'qtd':  # Quarter to Date
        quarter = (today.month - 1) // 3
        start_month = quarter * 3 + 1
        start_date = today.replace(month=start_month, day=1)
        end_date = today
    elif preset == '30d':  # Last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
    elif preset == '60d':  # Last 60 days
        start_date = today - timedelta(days=60)
        end_date = today
    elif preset == '90d':  # Last 90 days
        start_date = today - timedelta(days=90)
        end_date = today
    elif preset == 'last_month':  # Last complete month
        first_of_month = today.replace(day=1)
        end_date = first_of_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif preset == 'last_quarter':  # Last complete quarter
        quarter = (today.month - 1) // 3
        if quarter == 0:
            start_date = today.replace(year=today.year-1, month=10, day=1)
            end_date = today.replace(year=today.year-1, month=12, day=31)
        else:
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 2
            start_date = today.replace(month=start_month, day=1)
            # Get last day of end_month
            if end_month == 12:
                end_date = today.replace(month=12, day=31)
            else:
                end_date = today.replace(month=end_month+1, day=1) - timedelta(days=1)
    else:  # custom or default to MTD
        start_date = today.replace(day=1)
        end_date = today
    
    return start_date, end_date


def load_transactions_data(start_date, end_date, category_filter=None, min_amount=None, max_amount=None):
    """Load and filter transaction data"""
    try:
        # Get transactions from database
        df_polars = db_manager.get_transactions_by_date_range(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )
        
        # Convert to pandas for Dash
        df = df_polars.to_pandas()
        
        if len(df) == 0:
            return pd.DataFrame()
        
        # Filter out split parent transactions
        df = df[df['is_split'] == False]
        
        # Apply filters
        if category_filter and 'All' not in category_filter:
            df = df[df['category'].isin(category_filter)]
        
        if min_amount is not None:
            df = df[df['amount'] >= min_amount]
        
        if max_amount is not None:
            df = df[df['amount'] <= max_amount]
        
        return df
    except Exception as e:
        logger.error(f"Error loading transaction data: {str(e)}")
        return pd.DataFrame()


# App layout
dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("💰 Mintly Interactive Reports", className="text-primary text-center mb-4")
        ])
    ]),
    
    # Date Range and Filters Section
    dbc.Card([
        dbc.CardHeader(html.H4("📅 Date Range & Filters")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Quick Date Ranges:", className="fw-bold"),
                    dbc.ButtonGroup([
                        dbc.Button("MTD", id="btn-mtd", color="primary", outline=True, size="sm"),
                        dbc.Button("YTD", id="btn-ytd", color="primary", outline=True, size="sm"),
                        dbc.Button("QTD", id="btn-qtd", color="primary", outline=True, size="sm"),
                        dbc.Button("30D", id="btn-30d", color="primary", outline=True, size="sm"),
                        dbc.Button("60D", id="btn-60d", color="primary", outline=True, size="sm"),
                        dbc.Button("90D", id="btn-90d", color="primary", outline=True, size="sm"),
                    ], className="mb-2"),
                ], md=6),
                dbc.Col([
                    html.Label("Custom Date Range:", className="fw-bold"),
                    dbc.Row([
                        dbc.Col([
                            dcc.DatePickerSingle(
                                id='start-date-picker',
                                date=datetime.now().replace(day=1).date(),
                                display_format='YYYY-MM-DD'
                            )
                        ], width=6),
                        dbc.Col([
                            dcc.DatePickerSingle(
                                id='end-date-picker',
                                date=datetime.now().date(),
                                display_format='YYYY-MM-DD'
                            )
                        ], width=6),
                    ])
                ], md=6),
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Categories:", className="fw-bold"),
                    dcc.Dropdown(
                        id='category-filter',
                        options=[],  # Will be populated by callback
                        value=['All'],
                        multi=True,
                        placeholder="Select categories..."
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Amount Range:", className="fw-bold"),
                    dcc.RangeSlider(
                        id='amount-range-slider',
                        min=-1000,
                        max=0,
                        step=10,
                        value=[-1000, 0],
                        marks={-1000: '-$1000', -500: '-$500', 0: '$0'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], md=6),
            ]),
        ])
    ], className="mb-4"),
    
    # Summary Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Income", className="text-muted"),
                    html.H3(id="total-income", className="text-success")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Expenses", className="text-muted"),
                    html.H3(id="total-expenses", className="text-danger")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Net Balance", className="text-muted"),
                    html.H3(id="net-balance")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Transactions", className="text-muted"),
                    html.H3(id="transaction-count")
                ])
            ])
        ], md=3),
    ], className="mb-4"),
    
    # Charts Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📊 Spending by Category")),
                dbc.CardBody([
                    dcc.Graph(id='category-pie-chart', config={'displayModeBar': False})
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📈 Daily Spending Trend")),
                dbc.CardBody([
                    dcc.Graph(id='daily-trend-chart', config={'displayModeBar': False})
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🏪 Top Merchants")),
                dbc.CardBody([
                    dcc.Graph(id='top-merchants-chart', config={'displayModeBar': False})
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📉 Category Breakdown")),
                dbc.CardBody([
                    dcc.Graph(id='category-bar-chart', config={'displayModeBar': False})
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    # Transaction Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📋 Transaction Details")),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='transactions-table',
                        columns=[],
                        data=[],
                        page_size=15,
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'padding': '10px'},
                        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{amount} < 0'},
                                'color': '#dc3545'
                            },
                            {
                                'if': {'filter_query': '{amount} > 0'},
                                'color': '#28a745'
                            }
                        ],
                        sort_action='native',
                        filter_action='native',
                    )
                ])
            ])
        ])
    ]),
    
    # Hidden div to store date range state
    html.Div(id='date-range-state', style={'display': 'none'})
    
], fluid=True, className="p-4")


# Callback for date range buttons
@callback(
    [Output('start-date-picker', 'date'),
     Output('end-date-picker', 'date')],
    [Input('btn-mtd', 'n_clicks'),
     Input('btn-ytd', 'n_clicks'),
     Input('btn-qtd', 'n_clicks'),
     Input('btn-30d', 'n_clicks'),
     Input('btn-60d', 'n_clicks'),
     Input('btn-90d', 'n_clicks')],
    prevent_initial_call=True
)
def update_date_range(mtd, ytd, qtd, d30, d60, d90):
    """Update date range based on preset button clicks"""
    from dash import ctx
    
    if not ctx.triggered:
        start, end = get_date_range_preset('mtd')
        return start, end
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    preset_map = {
        'btn-mtd': 'mtd',
        'btn-ytd': 'ytd',
        'btn-qtd': 'qtd',
        'btn-30d': '30d',
        'btn-60d': '60d',
        'btn-90d': '90d'
    }
    
    preset = preset_map.get(button_id, 'mtd')
    start, end = get_date_range_preset(preset)
    
    return start, end


# Populate category dropdown
@callback(
    Output('category-filter', 'options'),
    Input('start-date-picker', 'date')
)
def populate_categories(_):
    """Populate category filter dropdown"""
    try:
        df = load_transactions_data(
            datetime.now().date() - timedelta(days=365),
            datetime.now().date()
        )
        
        if len(df) == 0:
            return [{'label': 'All', 'value': 'All'}]
        
        categories = sorted(df['category'].unique().tolist())
        options = [{'label': 'All', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in categories]
        return options
    except:
        return [{'label': 'All', 'value': 'All'}]


# Main callback to update all charts and metrics
@callback(
    [Output('total-income', 'children'),
     Output('total-expenses', 'children'),
     Output('net-balance', 'children'),
     Output('transaction-count', 'children'),
     Output('category-pie-chart', 'figure'),
     Output('daily-trend-chart', 'figure'),
     Output('top-merchants-chart', 'figure'),
     Output('category-bar-chart', 'figure'),
     Output('transactions-table', 'data'),
     Output('transactions-table', 'columns'),
     Output('amount-range-slider', 'min'),
     Output('amount-range-slider', 'max'),
     Output('amount-range-slider', 'value')],
    [Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date'),
     Input('category-filter', 'value'),
     Input('amount-range-slider', 'value')]
)
def update_dashboard(start_date, end_date, categories, amount_range):
    """Update all dashboard components based on filters"""
    
    # Convert dates
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    
    # Load data
    df = load_transactions_data(start, end)
    
    if len(df) == 0:
        # Return empty states
        return (
            "$0.00", "$0.00", "$0.00", "0",
            {}, {}, {}, {},
            [], [],
            -1000, 0, [-1000, 0]
        )
    
    # Calculate amount range from data
    min_amount = float(df[df['amount'] < 0]['amount'].min()) if len(df[df['amount'] < 0]) > 0 else -1000
    max_amount = 0
    current_range = [min_amount, max_amount]
    
    # Apply amount filter
    df_filtered = df[(df['amount'] >= amount_range[0]) & (df['amount'] <= amount_range[1])]
    
    # Apply category filter
    if categories and 'All' not in categories:
        df_filtered = df_filtered[df_filtered['category'].isin(categories)]
    
    # Calculate metrics
    total_income = df_filtered[df_filtered['amount'] > 0]['amount'].sum()
    total_expenses = abs(df_filtered[df_filtered['amount'] < 0]['amount'].sum())
    net_balance = total_income - total_expenses
    transaction_count = len(df_filtered)
    
    # Pie Chart - Spending by Category
    expenses_by_category = df_filtered[df_filtered['amount'] < 0].groupby('category')['amount'].sum().abs()
    pie_fig = px.pie(
        values=expenses_by_category.values,
        names=expenses_by_category.index,
        title="",
        hole=0.4
    )
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    pie_fig.update_layout(showlegend=True, height=350)
    
    # Line Chart - Daily Spending Trend
    df_filtered['date_only'] = pd.to_datetime(df_filtered['date']).dt.date
    daily_spending = df_filtered[df_filtered['amount'] < 0].groupby('date_only')['amount'].sum().abs()
    trend_fig = px.line(
        x=daily_spending.index,
        y=daily_spending.values,
        title="",
        labels={'x': 'Date', 'y': 'Amount Spent ($)'}
    )
    trend_fig.update_traces(line_color='#FF6B6B', line_width=2)
    trend_fig.update_layout(height=350)
    
    # Top Merchants Bar Chart
    top_merchants = df_filtered[df_filtered['amount'] < 0].groupby('description')['amount'].sum().abs().nlargest(10)
    merchants_fig = px.bar(
        x=top_merchants.values,
        y=top_merchants.index,
        orientation='h',
        title="",
        labels={'x': 'Amount Spent ($)', 'y': 'Merchant'}
    )
    merchants_fig.update_traces(marker_color='#4ECDC4')
    merchants_fig.update_layout(height=350, yaxis={'categoryorder': 'total ascending'})
    
    # Category Breakdown Bar Chart
    category_bar_fig = px.bar(
        x=expenses_by_category.index,
        y=expenses_by_category.values,
        title="",
        labels={'x': 'Category', 'y': 'Amount Spent ($)'}
    )
    category_bar_fig.update_traces(marker_color='#45B7D1')
    category_bar_fig.update_layout(height=350)
    
    # Transaction Table
    table_df = df_filtered[['date', 'description', 'amount', 'category']].copy()
    table_df['date'] = pd.to_datetime(table_df['date']).dt.strftime('%Y-%m-%d')
    table_df['amount'] = table_df['amount'].round(2)
    table_df = table_df.sort_values('date', ascending=False)
    
    columns = [
        {'name': 'Date', 'id': 'date'},
        {'name': 'Description', 'id': 'description'},
        {'name': 'Amount', 'id': 'amount', 'type': 'numeric', 'format': {'specifier': '$,.2f'}},
        {'name': 'Category', 'id': 'category'}
    ]
    
    return (
        f"${total_income:,.2f}",
        f"${total_expenses:,.2f}",
        f"${net_balance:,.2f}",
        f"{transaction_count:,}",
        pie_fig,
        trend_fig,
        merchants_fig,
        category_bar_fig,
        table_df.to_dict('records'),
        columns,
        min_amount,
        max_amount,
        current_range
    )


def init_dash_app(server):
    """Initialize Dash app with FastAPI server"""
    dash_app.server = server
    return dash_app

