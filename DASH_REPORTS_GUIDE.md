# Interactive Dash Reports Guide

## 🎉 New Feature: Interactive Reports with Dash!

Based on the [Plotly Dash tutorial](https://dash.plotly.com/tutorial), we've added a powerful interactive reporting dashboard to Mintly!

---

## ✨ Features

### 📅 Quick Date Range Presets
No more manual date picking! Click preset buttons:
- **MTD** - Month to Date
- **YTD** - Year to Date  
- **QTD** - Quarter to Date
- **30D** - Last 30 days
- **60D** - Last 60 days
- **90D** - Last 90 days

### 🎛️ Interactive Filters
- **Category Filter** - Multi-select dropdown to filter by categories
- **Amount Range Slider** - Filter transactions by amount
- **Real-time Updates** - Charts update instantly as you adjust filters

### 📊 Enhanced Visualizations
- **Pie Chart** - Spending by category with percentages
- **Daily Trend Line Chart** - See your daily spending patterns
- **Top Merchants Bar Chart** - Your top 10 spending locations
- **Category Breakdown** - Horizontal bar chart of all categories
- **Transaction Table** - Sortable, filterable data table

### 📈 Summary Cards
- Total Income
- Total Expenses
- Net Balance
- Transaction Count

---

## 🚀 How to Access

### Option 1: Direct URL
```
http://localhost:8000/dash/
```

### Option 2: Navigation Menu
Click "📊 Interactive" in the top navigation bar

### Option 3: From Python Frontend
Go to Reports → Interactive Reports link

---

## 💡 How to Use

### 1. Select Date Range

**Quick Presets:**
```
Click MTD → Instantly see this month's data
Click YTD → See year-to-date spending
Click 90D → Last 3 months analysis
```

**Custom Range:**
```
Use date pickers for specific date ranges
```

### 2. Apply Filters

**Filter by Category:**
- Select one or more categories from dropdown
- Charts update immediately
- Great for comparing specific spending types

**Filter by Amount:**
- Drag slider to set min/max amounts
- Focus on large or small transactions
- Exclude outliers for cleaner analysis

### 3. Analyze Data

**Summary Cards** - Get quick overview at the top

**Pie Chart** - See category distribution
- Hover for exact amounts
- Click legend to hide/show categories

**Daily Trend** - Track spending over time
- Identify spending spikes
- See patterns (weekdays vs weekends)

**Top Merchants** - Find your biggest expenses
- Discover where money goes
- Make informed decisions

**Transaction Table** - Drill into details
- Sort by any column
- Filter with search
- Export data (if needed)

---

## 🎯 Use Cases

### Monthly Budget Review
```
1. Click "MTD" button
2. Review pie chart for category breakdown
3. Check if spending aligns with budget
4. Identify overspending categories
```

### Quarterly Analysis
```
1. Click "QTD" button
2. View daily trend for patterns
3. Check top merchants
4. Plan next quarter's budget
```

### Category Deep Dive
```
1. Select "Groceries" from category filter
2. See only grocery spending
3. Check top grocery stores
4. Analyze daily grocery trends
```

### Large Transaction Review
```
1. Adjust amount slider to show only large purchases
2. Review high-spend items
3. Verify all charges are correct
4. Plan for similar future expenses
```

---

## 🔧 Technical Details

### Built With
- **Dash 2.14.2** - Interactive Python framework
- **Dash Bootstrap Components** - Modern UI styling
- **Plotly Express** - Chart visualizations
- **Pandas** - Data processing
- **DuckDB** - Data source

### Architecture
```
FastAPI Backend (Port 8000)
    ↓
Dash App (/dash/)
    ↓
DuckDB Database
    ↓
Interactive Charts & Filters
```

### Performance
- **Real-time Updates** - Callbacks execute in milliseconds
- **Efficient Queries** - DuckDB provides fast data retrieval
- **Client-side Rendering** - Charts render in browser
- **Responsive** - Works on desktop and mobile

---

## 📱 vs Other Report Options

| Feature | Interactive Dash | React Reports | Python Reports |
|---------|-----------------|---------------|----------------|
| **Port** | 8000/dash | 3000 | 8000/reports |
| **Date Presets** | ✅ MTD/YTD/QTD/etc | ✅ MTD/YTD/QTD/etc | ❌ Manual only |
| **Category Filter** | ✅ Multi-select | ✅ Checkboxes | ❌ |
| **Amount Filter** | ✅ Slider | ❌ | ❌ |
| **Top Merchants** | ✅ | ❌ | ❌ |
| **Daily Trend** | ✅ | ❌ | ✅ |
| **Transaction Table** | ✅ Sortable/Filterable | ❌ | ❌ |
| **Real-time Updates** | ✅ Instant | ✅ Instant | ❌ Page reload |

---

## 🎨 Customization

### Add More Date Presets

Edit `app/dash_reports.py`:

```python
def get_date_range_preset(preset):
    if preset == 'last_week':
        start_date = today - timedelta(days=7)
        end_date = today
    # Add more presets...
```

### Add Custom Charts

Add new chart in layout:

```python
dbc.Col([
    dbc.Card([
        dbc.CardHeader(html.H5("📊 My Custom Chart")),
        dbc.CardBody([
            dcc.Graph(id='custom-chart')
        ])
    ])
], md=6),
```

Add callback:

```python
@callback(
    Output('custom-chart', 'figure'),
    [Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
def update_custom_chart(start, end):
    # Your chart logic
    fig = px.bar(...)
    return fig
```

### Change Color Scheme

Edit chart colors:

```python
fig.update_traces(marker_color='#YourColor')
```

Or change theme:

```python
external_stylesheets=[dbc.themes.DARKLY]  # Dark theme
external_stylesheets=[dbc.themes.FLATLY]  # Flat theme
```

---

## 🐛 Troubleshooting

### Dash Page Not Loading

**Problem:** Can't access /dash/ URL

**Solution:**
```bash
# Check if Dash is installed
pip install dash dash-bootstrap-components

# Restart backend
docker-compose restart backend
```

### Charts Show No Data

**Problem:** Empty charts despite having transactions

**Solutions:**
1. Check date range includes your transactions
2. Verify transactions exist in database
3. Clear filters (category/amount)
4. Refresh the page

### Filters Not Working

**Problem:** Selecting filters doesn't update charts

**Solution:**
- Check browser console for errors
- Ensure JavaScript is enabled
- Try refreshing the page
- Check backend logs: `docker-compose logs backend`

### Slow Performance

**Problem:** Charts take long to load

**Solutions:**
- Reduce date range (use 30D instead of YTD)
- Limit transaction count in database query
- Check database size: `ls -lh data/mintly.db`
- Restart containers: `docker-compose restart`

---

## 📚 Learn More

### Dash Documentation
- **Official Tutorial**: https://dash.plotly.com/tutorial
- **Dash Bootstrap**: https://dash-bootstrap-components.opensource.faculty.ai/
- **Plotly Express**: https://plotly.com/python/plotly-express/

### Related Files
- `app/dash_reports.py` - Main Dash application
- `app/main.py` - FastAPI integration
- `requirements.txt` - Dependencies

---

## 🚀 Future Enhancements

Potential additions:
- [ ] Export reports to PDF
- [ ] Email scheduled reports
- [ ] Budget vs actual comparison
- [ ] Savings rate calculation
- [ ] Spending predictions
- [ ] Merchant categorization suggestions
- [ ] Multi-currency support
- [ ] Shared household budgets

---

## 🎓 Pro Tips

1. **Use Presets** - Faster than manual date entry
2. **Combine Filters** - Category + amount range for deep analysis
3. **Check Daily Trend** - Identify spending patterns
4. **Review Top Merchants** - Find savings opportunities
5. **Export Data** - Use table filter/sort for specific queries
6. **Bookmark /dash/** - Quick access to interactive reports

---

## 💬 Feedback

Found a bug? Want a feature? 
- Check logs: `logs/app_*.log`
- Review code: `app/dash_reports.py`
- Customize to your needs!

---

**Enjoy your interactive reports!** 📊✨


