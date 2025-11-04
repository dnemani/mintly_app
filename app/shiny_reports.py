"""
Interactive Shiny Reports with filters and date range presets
Uses Shiny for Python (https://shiny.posit.co/py/)
"""
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from app.database import DatabaseManager
import shutil
import os

logger = logging.getLogger(__name__)


def create_db_copy():
    """Create a copy of the database for read-only access"""
    source_db = "data/mintly.db"
    copy_db = "data/mintly_shiny.db"

    if os.path.exists(source_db):
        shutil.copy2(source_db, copy_db)
        return copy_db
    return source_db


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
    else:  # default to MTD
        start_date = today.replace(day=1)
        end_date = today

    return start_date, end_date


def load_transactions_data(db_manager, start_date, end_date, category_filter=None, min_amount=None, max_amount=None):
    """Load and filter transaction data"""
    try:
        # Get transactions from database
        df_polars = db_manager.get_transactions_by_date_range(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )

        # Convert to pandas for plotting
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


# Create Shiny UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("📅 Filters"),

        # Date Range Presets
        ui.h6("Quick Date Ranges"),
        ui.layout_column_wrap(
            ui.input_action_button("btn_mtd", "MTD", class_="btn-sm btn-primary"),
            ui.input_action_button("btn_ytd", "YTD", class_="btn-sm btn-primary"),
            ui.input_action_button("btn_qtd", "QTD", class_="btn-sm btn-primary"),
            ui.input_action_button("btn_30d", "30D", class_="btn-sm btn-primary"),
            ui.input_action_button("btn_60d", "60D", class_="btn-sm btn-primary"),
            ui.input_action_button("btn_90d", "90D", class_="btn-sm btn-primary"),
            width=1/3
        ),

        ui.hr(),

        # Custom Date Range
        ui.h6("Custom Date Range"),
        ui.input_date("start_date", "Start Date", value=datetime.now().replace(day=1).date()),
        ui.input_date("end_date", "End Date", value=datetime.now().date()),

        ui.hr(),

        # Category Filter
        ui.input_selectize(
            "category_filter",
            "Categories",
            choices=["All"],
            selected=["All"],
            multiple=True
        ),

        ui.hr(),

        # Amount Range
        ui.input_slider(
            "amount_range",
            "Amount Range",
            min=-1000,
            max=0,
            value=[-1000, 0],
            step=10
        ),

        width=300,
        bg="#f8f9fa"
    ),

    ui.h2("💰 Mintly Interactive Reports (Shiny)", class_="text-primary mb-4"),

    # Summary Cards
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Total Income", class_="bg-success text-white"),
            ui.output_text("total_income")
        ),
        ui.card(
            ui.card_header("Total Expenses", class_="bg-danger text-white"),
            ui.output_text("total_expenses")
        ),
        ui.card(
            ui.card_header("Net Balance", class_="bg-info text-white"),
            ui.output_text("net_balance")
        ),
        ui.card(
            ui.card_header("Transactions", class_="bg-secondary text-white"),
            ui.output_text("transaction_count")
        ),
        width=1/4
    ),

    ui.br(),

    # Charts Section
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("📊 Spending by Category"),
            ui.output_ui("category_pie_chart")
        ),
        ui.card(
            ui.card_header("📈 Daily Spending Trend"),
            ui.output_ui("daily_trend_chart")
        ),
        width=1/2
    ),

    ui.br(),

    ui.layout_column_wrap(
        ui.card(
            ui.card_header("🏪 Top Merchants"),
            ui.output_ui("top_merchants_chart")
        ),
        ui.card(
            ui.card_header("📉 Category Breakdown"),
            ui.output_ui("category_bar_chart")
        ),
        width=1/2
    ),

    ui.br(),

    # Transaction Table
    ui.card(
        ui.card_header("📋 Transaction Details"),
        ui.output_data_frame("transactions_table")
    ),

    title="Mintly - Shiny Reports"
)


# Create Shiny Server
def server(input: Inputs, output: Outputs, session: Session):
    # Initialize database manager with read-only copy
    db_copy_path = create_db_copy()
    db_manager = DatabaseManager(db_path=db_copy_path, read_only=True)

    # Reactive date range
    @reactive.Calc
    def date_range():
        """Get current date range from inputs or button clicks"""
        return (input.start_date(), input.end_date())

    # Handle date preset buttons
    @reactive.Effect
    @reactive.event(input.btn_mtd)
    def _():
        start, end = get_date_range_preset('mtd')
        ui.update_date("start_date", value=start)
        ui.update_date("end_date", value=end)

    @reactive.Effect
    @reactive.event(input.btn_ytd)
    def _():
        start, end = get_date_range_preset('ytd')
        ui.update_date("start_date", value=start)
        ui.update_date("end_date", value=end)

    @reactive.Effect
    @reactive.event(input.btn_qtd)
    def _():
        start, end = get_date_range_preset('qtd')
        ui.update_date("start_date", value=start)
        ui.update_date("end_date", value=end)

    @reactive.Effect
    @reactive.event(input.btn_30d)
    def _():
        start, end = get_date_range_preset('30d')
        ui.update_date("start_date", value=start)
        ui.update_date("end_date", value=end)

    @reactive.Effect
    @reactive.event(input.btn_60d)
    def _():
        start, end = get_date_range_preset('60d')
        ui.update_date("start_date", value=start)
        ui.update_date("end_date", value=end)

    @reactive.Effect
    @reactive.event(input.btn_90d)
    def _():
        start, end = get_date_range_preset('90d')
        ui.update_date("start_date", value=start)
        ui.update_date("end_date", value=end)

    # Reactive data loading
    @reactive.Calc
    def transactions_data():
        """Load filtered transaction data"""
        start_date, end_date = date_range()
        amount_range = input.amount_range()

        df = load_transactions_data(
            db_manager,
            start_date,
            end_date,
            category_filter=input.category_filter(),
            min_amount=amount_range[0],
            max_amount=amount_range[1]
        )

        return df

    # Update category dropdown
    @reactive.Effect
    def _():
        try:
            # Load all transactions from the past year to get categories
            today = datetime.now().date()
            df = load_transactions_data(
                db_manager,
                today - timedelta(days=365),
                today
            )

            if len(df) > 0:
                categories = sorted(df['category'].unique().tolist())
                choices = ["All"] + categories
                ui.update_selectize("category_filter", choices=choices, selected=["All"])
        except Exception as e:
            logger.error(f"Error updating categories: {str(e)}")

    # Update amount range based on data
    @reactive.Effect
    def _():
        try:
            start_date, end_date = date_range()
            df = load_transactions_data(db_manager, start_date, end_date)

            if len(df) > 0:
                min_amount = float(df[df['amount'] < 0]['amount'].min()) if len(df[df['amount'] < 0]) > 0 else -1000
                max_amount = 0
                ui.update_slider("amount_range", min=min_amount, max=max_amount, value=[min_amount, max_amount])
        except Exception as e:
            logger.error(f"Error updating amount range: {str(e)}")

    # Render summary metrics
    @output
    @render.text
    def total_income():
        df = transactions_data()
        if len(df) == 0:
            return "$0.00"
        income = df[df['amount'] > 0]['amount'].sum()
        return f"${income:,.2f}"

    @output
    @render.text
    def total_expenses():
        df = transactions_data()
        if len(df) == 0:
            return "$0.00"
        expenses = abs(df[df['amount'] < 0]['amount'].sum())
        return f"${expenses:,.2f}"

    @output
    @render.text
    def net_balance():
        df = transactions_data()
        if len(df) == 0:
            return "$0.00"
        income = df[df['amount'] > 0]['amount'].sum()
        expenses = abs(df[df['amount'] < 0]['amount'].sum())
        balance = income - expenses
        return f"${balance:,.2f}"

    @output
    @render.text
    def transaction_count():
        df = transactions_data()
        return f"{len(df):,}"

    # Render charts
    @output
    @render.ui
    def category_pie_chart():
        df = transactions_data()
        if len(df) == 0:
            return ui.p("No data available")

        expenses_by_category = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()

        fig = px.pie(
            values=expenses_by_category.values,
            names=expenses_by_category.index,
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=True, height=400, margin=dict(l=0, r=0, t=0, b=0))

        return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="pie_chart"))

    @output
    @render.ui
    def daily_trend_chart():
        df = transactions_data()
        if len(df) == 0:
            return ui.p("No data available")

        df['date_only'] = pd.to_datetime(df['date']).dt.date
        daily_spending = df[df['amount'] < 0].groupby('date_only')['amount'].sum().abs()

        fig = px.line(
            x=daily_spending.index,
            y=daily_spending.values,
            labels={'x': 'Date', 'y': 'Amount Spent ($)'}
        )
        fig.update_traces(line_color='#FF6B6B', line_width=2)
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))

        return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="trend_chart"))

    @output
    @render.ui
    def top_merchants_chart():
        df = transactions_data()
        if len(df) == 0:
            return ui.p("No data available")

        top_merchants = df[df['amount'] < 0].groupby('description')['amount'].sum().abs().nlargest(10)

        fig = px.bar(
            x=top_merchants.values,
            y=top_merchants.index,
            orientation='h',
            labels={'x': 'Amount Spent ($)', 'y': 'Merchant'}
        )
        fig.update_traces(marker_color='#4ECDC4')
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'}, margin=dict(l=0, r=0, t=0, b=0))

        return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="merchants_chart"))

    @output
    @render.ui
    def category_bar_chart():
        df = transactions_data()
        if len(df) == 0:
            return ui.p("No data available")

        expenses_by_category = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()

        fig = px.bar(
            x=expenses_by_category.index,
            y=expenses_by_category.values,
            labels={'x': 'Category', 'y': 'Amount Spent ($)'}
        )
        fig.update_traces(marker_color='#45B7D1')
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))

        return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="category_chart"))

    @output
    @render.data_frame
    def transactions_table():
        df = transactions_data()
        if len(df) == 0:
            return pd.DataFrame()

        # Prepare table data
        table_df = df[['date', 'description', 'amount', 'category']].copy()
        table_df['date'] = pd.to_datetime(table_df['date']).dt.strftime('%Y-%m-%d')
        table_df['amount'] = table_df['amount'].round(2)
        table_df = table_df.sort_values('date', ascending=False)

        return render.DataGrid(table_df, height="400px")


# Create Shiny app instance
shiny_app = App(app_ui, server)