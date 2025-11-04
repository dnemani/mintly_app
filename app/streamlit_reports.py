"""
Interactive Streamlit Reports with filters and date range presets
Uses Streamlit (https://docs.streamlit.io/)
"""
import streamlit as st
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
    copy_db = "data/mintly_streamlit.db"

    if os.path.exists(source_db):
        shutil.copy2(source_db, copy_db)
        return copy_db
    return source_db


def get_date_range_preset(preset):
    """Calculate date ranges for presets"""
    today = datetime.now().date()

    if preset == 'MTD':  # Month to Date
        start_date = today.replace(day=1)
        end_date = today
    elif preset == 'YTD':  # Year to Date
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif preset == 'QTD':  # Quarter to Date
        quarter = (today.month - 1) // 3
        start_month = quarter * 3 + 1
        start_date = today.replace(month=start_month, day=1)
        end_date = today
    elif preset == '30D':  # Last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
    elif preset == '60D':  # Last 60 days
        start_date = today - timedelta(days=60)
        end_date = today
    elif preset == '90D':  # Last 90 days
        start_date = today - timedelta(days=90)
        end_date = today
    else:  # default to MTD
        start_date = today.replace(day=1)
        end_date = today

    return start_date, end_date


@st.cache_resource
def get_db_manager():
    """Get cached database manager"""
    db_copy_path = create_db_copy()
    return DatabaseManager(db_path=db_copy_path, read_only=True)


@st.cache_data(ttl=60)
def load_transactions_data(_db_manager, start_date, end_date, category_filter=None, min_amount=None, max_amount=None):
    """Load and filter transaction data"""
    try:
        # Get transactions from database
        df_polars = _db_manager.get_transactions_by_date_range(
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


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Mintly - Streamlit Reports",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title
    st.title("💰 Mintly Interactive Reports (Streamlit)")

    # Initialize database
    db_manager = get_db_manager()

    # Sidebar for filters
    with st.sidebar:
        st.header("📅 Filters")

        # Date Range Presets
        st.subheader("Quick Date Ranges")
        preset_cols = st.columns(3)

        preset_clicked = None
        with preset_cols[0]:
            if st.button("MTD", use_container_width=True):
                preset_clicked = 'MTD'
            if st.button("30D", use_container_width=True):
                preset_clicked = '30D'

        with preset_cols[1]:
            if st.button("YTD", use_container_width=True):
                preset_clicked = 'YTD'
            if st.button("60D", use_container_width=True):
                preset_clicked = '60D'

        with preset_cols[2]:
            if st.button("QTD", use_container_width=True):
                preset_clicked = 'QTD'
            if st.button("90D", use_container_width=True):
                preset_clicked = '90D'

        # Handle preset clicks
        if preset_clicked:
            start, end = get_date_range_preset(preset_clicked)
            st.session_state['start_date'] = start
            st.session_state['end_date'] = end

        st.divider()

        # Custom Date Range
        st.subheader("Custom Date Range")

        # Initialize session state for dates
        if 'start_date' not in st.session_state:
            st.session_state['start_date'] = datetime.now().replace(day=1).date()
        if 'end_date' not in st.session_state:
            st.session_state['end_date'] = datetime.now().date()

        start_date = st.date_input(
            "Start Date",
            value=st.session_state['start_date'],
            key='start_date_input'
        )
        end_date = st.date_input(
            "End Date",
            value=st.session_state['end_date'],
            key='end_date_input'
        )

        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date

        st.divider()

        # Category Filter
        st.subheader("Categories")

        # Load all categories
        try:
            df_all = load_transactions_data(
                db_manager,
                datetime.now().date() - timedelta(days=365),
                datetime.now().date()
            )
            if len(df_all) > 0:
                categories = ['All'] + sorted(df_all['category'].unique().tolist())
            else:
                categories = ['All']
        except:
            categories = ['All']

        category_filter = st.multiselect(
            "Select categories",
            options=categories,
            default=['All']
        )

        st.divider()

        # Amount Range
        st.subheader("Amount Range")

        # Get data to determine range
        df_range = load_transactions_data(db_manager, start_date, end_date)
        if len(df_range) > 0 and len(df_range[df_range['amount'] < 0]) > 0:
            min_val = float(df_range[df_range['amount'] < 0]['amount'].min())
            max_val = 0.0
        else:
            min_val = -1000.0
            max_val = 0.0

        amount_range = st.slider(
            "Amount range",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            step=10.0
        )

    # Load filtered data
    df = load_transactions_data(
        db_manager,
        start_date,
        end_date,
        category_filter=category_filter if 'All' not in category_filter else None,
        min_amount=amount_range[0],
        max_amount=amount_range[1]
    )

    # Summary Cards
    if len(df) > 0:
        col1, col2, col3, col4 = st.columns(4)

        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expenses = abs(df[df['amount'] < 0]['amount'].sum())
        net_balance = total_income - total_expenses
        transaction_count = len(df)

        with col1:
            st.metric("Total Income", f"${total_income:,.2f}", delta=None)

        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}", delta=None)

        with col3:
            st.metric("Net Balance", f"${net_balance:,.2f}", delta=None)

        with col4:
            st.metric("Transactions", f"{transaction_count:,}", delta=None)

        st.divider()

        # Charts Section
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("📊 Spending by Category")
            expenses_by_category = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()

            if len(expenses_by_category) > 0:
                fig_pie = px.pie(
                    values=expenses_by_category.values,
                    names=expenses_by_category.index,
                    hole=0.4
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(showlegend=True, height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No expense data available")

        with chart_col2:
            st.subheader("📈 Daily Spending Trend")
            df['date_only'] = pd.to_datetime(df['date']).dt.date
            daily_spending = df[df['amount'] < 0].groupby('date_only')['amount'].sum().abs()

            if len(daily_spending) > 0:
                fig_line = px.line(
                    x=daily_spending.index,
                    y=daily_spending.values,
                    labels={'x': 'Date', 'y': 'Amount Spent ($)'}
                )
                fig_line.update_traces(line_color='#FF6B6B', line_width=2)
                fig_line.update_layout(height=400)
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No spending data available")

        st.divider()

        # Second row of charts
        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            st.subheader("🏪 Top Merchants")
            top_merchants = df[df['amount'] < 0].groupby('description')['amount'].sum().abs().nlargest(10)

            if len(top_merchants) > 0:
                fig_bar_h = px.bar(
                    x=top_merchants.values,
                    y=top_merchants.index,
                    orientation='h',
                    labels={'x': 'Amount Spent ($)', 'y': 'Merchant'}
                )
                fig_bar_h.update_traces(marker_color='#4ECDC4')
                fig_bar_h.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_bar_h, use_container_width=True)
            else:
                st.info("No merchant data available")

        with chart_col4:
            st.subheader("📉 Category Breakdown")

            if len(expenses_by_category) > 0:
                fig_bar = px.bar(
                    x=expenses_by_category.index,
                    y=expenses_by_category.values,
                    labels={'x': 'Category', 'y': 'Amount Spent ($)'}
                )
                fig_bar.update_traces(marker_color='#45B7D1')
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No category data available")

        st.divider()

        # Transaction Table
        st.subheader("📋 Transaction Details")

        table_df = df[['date', 'description', 'amount', 'category']].copy()
        table_df['date'] = pd.to_datetime(table_df['date']).dt.strftime('%Y-%m-%d')
        table_df['amount'] = table_df['amount'].round(2)
        table_df = table_df.sort_values('date', ascending=False)

        st.dataframe(
            table_df,
            use_container_width=True,
            height=400,
            column_config={
                "date": st.column_config.TextColumn("Date", width="small"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f",
                    width="small"
                ),
                "category": st.column_config.TextColumn("Category", width="medium")
            }
        )
    else:
        st.warning("No transaction data available for the selected filters. Please upload transactions or adjust your filters.")
        st.info("To upload transactions, visit the backend at http://localhost:8000")


if __name__ == "__main__":
    main()
