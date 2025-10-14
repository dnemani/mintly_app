# 🎛️ Interactive Reports Feature Added!

## 🎉 What's New

Your Mintly app now has **interactive Dash reports** with advanced filtering and date range presets, following the [Plotly Dash tutorial](https://dash.plotly.com/tutorial)!

---

## ✨ New Features

### 1. 📅 Quick Date Range Presets
Click buttons for instant date selection:
- **MTD** - Month to Date
- **YTD** - Year to Date
- **QTD** - Quarter to Date
- **30D** - Last 30 days
- **60D** - Last 60 days
- **90D** - Last 90 days

### 2. 🎛️ Interactive Filters
- **Category Multi-Select** - Filter by one or more categories
- **Amount Range Slider** - Focus on specific spending amounts
- **Real-time Updates** - Charts refresh instantly

### 3. 📊 Enhanced Visualizations
- **Pie Chart** - Spending by category with hover details
- **Daily Trend Line** - See spending patterns over time
- **Top 10 Merchants** - Discover where you spend most
- **Category Breakdown** - Horizontal bar comparison
- **Transaction Table** - Sortable, filterable data grid

### 4. 📈 Summary Cards
Quick metrics at a glance:
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
Click **"📊 Interactive"** in the top menu bar

### Option 3: Python Frontend
Navigate to Reports → Interactive Reports

### Option 4: React Frontend  
Reports page now has date presets and category filters built-in!

---

## 🎯 What Was Added

### Backend (`app/`)
✅ **`app/dash_reports.py`** (450 lines)
- Complete Dash application
- Date range preset logic
- Interactive callbacks
- Filter implementations
- Chart generation

✅ **`app/main.py`** - Updated
- Mounted Dash app at `/dash/`
- Added WSGI middleware
- New navigation link

### Frontend Updates

#### Python/Jinja2
✅ **`app/templates/base.html`** - Updated
- Added "📊 Interactive" menu link

✅ **`app/templates/dash_redirect.html`** - New
- Redirect page to Dash app

#### React
✅ **`frontend/src/components/Reports.jsx`** - Enhanced
- Date range preset buttons (MTD/YTD/QTD/30D/60D/90D)
- Category filter checkboxes
- Auto-reload on preset selection

✅ **`frontend/src/App.css`** - Updated
- Button group styling
- Filter chip styling
- Responsive design

### Dependencies
✅ **`requirements.txt`** - Updated
```
dash==2.14.2
dash-bootstrap-components==1.5.0
```

### Documentation
✅ **`DASH_REPORTS_GUIDE.md`** - Complete guide
✅ **`INTERACTIVE_REPORTS_SUMMARY.md`** - This file
✅ **`README.md`** - Updated with new features

---

## 📸 Features Comparison

| Feature | Interactive Dash | React Reports | Python Reports |
|---------|-----------------|---------------|----------------|
| **Access** | /dash/ | Port 3000 | /reports |
| **Date Presets** | ✅ MTD/YTD/QTD/30D/60D/90D | ✅ MTD/YTD/QTD/30D/60D/90D | ❌ |
| **Category Filter** | ✅ Dropdown | ✅ Checkboxes | ❌ |
| **Amount Filter** | ✅ Slider | ❌ | ❌ |
| **Top Merchants** | ✅ Bar Chart | ❌ | ❌ |
| **Transaction Table** | ✅ Sortable | ❌ | ❌ |
| **Real-time** | ✅ Instant | ✅ Instant | ❌ Page reload |
| **Framework** | Dash/Bootstrap | React/Recharts | Jinja2/Plotly |

---

## 🎓 Example Usage

### Quick Monthly Review
```
1. Navigate to http://localhost:8000/dash/
2. Click "MTD" button
3. View spending breakdown
4. Check top merchants
5. Filter specific categories if needed
```

### Quarterly Analysis
```
1. Click "QTD" button
2. Use amount slider to focus on large purchases
3. Select "Shopping" category from filter
4. Review daily trend chart
5. Check transaction table for details
```

### Custom Deep Dive
```
1. Set custom date range (e.g., vacation dates)
2. Select "Travel" + "Restaurants" categories
3. View combined spending
4. Sort transaction table by amount
5. Identify areas to optimize
```

---

## 🛠️ Technical Implementation

### Based on Dash Tutorial
Following https://dash.plotly.com/tutorial, we implemented:

1. **App Initialization**
```python
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

dash_app = Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP])
```

2. **Layout with Components**
```python
app.layout = dbc.Container([
    dbc.Row([...]),  # Date range controls
    dbc.Row([...]),  # Summary cards
    dbc.Row([...]),  # Charts
])
```

3. **Interactive Callbacks**
```python
@callback(
    [Output('chart', 'figure')],
    [Input('date-picker', 'date'),
     Input('category-filter', 'value')]
)
def update_charts(date, categories):
    # Update charts based on filters
    return fig
```

4. **Integration with FastAPI**
```python
from fastapi.middleware.wsgi import WSGIMiddleware

app.mount("/dash", WSGIMiddleware(dash_app.server))
```

---

## 📦 What You Need to Do

### Rebuild Docker Container
```bash
docker-compose down
docker-compose up --build
```

This will install the new dependencies (Dash + Bootstrap components)

### Access Interactive Reports
```bash
# Start app
docker-compose up

# Visit in browser
http://localhost:8000/dash/
```

---

## 💡 Pro Tips

1. **Use Presets First** - Faster than manual date selection
2. **Combine Filters** - Category + amount for precise analysis
3. **Check Daily Trends** - Spot spending patterns
4. **Review Top Merchants** - Find savings opportunities
5. **Use Transaction Table** - Sort/filter for specific items
6. **Bookmark `/dash/`** - Direct access to interactive reports

---

## 🎨 Customization

### Add Custom Date Preset

Edit `app/dash_reports.py`:

```python
# Add button
dbc.Button("Last Week", id="btn-week", ...)

# Add preset logic
def get_date_range_preset(preset):
    if preset == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
```

### Change Chart Colors

```python
pie_fig.update_traces(marker_colors=['#FF6B6B', '#4ECDC4', ...])
```

### Add New Chart

```python
dbc.Col([
    dbc.Card([
        dbc.CardHeader(html.H5("My Chart")),
        dbc.CardBody([
            dcc.Graph(id='my-chart')
        ])
    ])
]),

# Add callback
@callback(Output('my-chart', 'figure'), ...)
def update_my_chart(...):
    return fig
```

---

## 🚀 Future Enhancements

Potential additions:
- [ ] Export to PDF/Excel
- [ ] Budget vs actual comparison
- [ ] Predictive analytics
- [ ] Email scheduled reports
- [ ] Spending alerts
- [ ] Multi-currency support

---

## 📚 Resources

- **Dash Tutorial**: https://dash.plotly.com/tutorial
- **Dash Bootstrap**: https://dash-bootstrap-components.opensource.faculty.ai/
- **Plotly Express**: https://plotly.com/python/plotly-express/
- **Guide**: `DASH_REPORTS_GUIDE.md`

---

## ✅ Summary

You now have:
- ✅ Interactive Dash reports at `/dash/`
- ✅ 6 date range presets (MTD/YTD/QTD/30D/60D/90D)
- ✅ Category and amount filters
- ✅ 4 different chart types
- ✅ Top merchants analysis
- ✅ Sortable transaction table
- ✅ Real-time updates
- ✅ React frontend with presets too!

**Start using it:**
```bash
docker-compose up --build
# Visit: http://localhost:8000/dash/
```

**Enjoy your enhanced reporting!** 🎉📊


