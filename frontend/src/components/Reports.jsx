import React, { useState, useEffect } from 'react'
import { getSpendingSummary } from '../services/api'
import { format, startOfMonth, endOfMonth } from 'date-fns'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B195', '#C06C84',
]

function Reports() {
  const [startDate, setStartDate] = useState(
    format(startOfMonth(new Date()), 'yyyy-MM-dd')
  )
  const [endDate, setEndDate] = useState(
    format(endOfMonth(new Date()), 'yyyy-MM-dd')
  )
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const loadReport = async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await getSpendingSummary(startDate, endDate)
      setSummary(data.report)
    } catch (err) {
      setError('Error loading report')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReport()
  }, [])

  const formatCurrency = (value) => `$${Math.abs(value).toFixed(2)}`

  const pieData = summary?.categories.map((cat) => ({
    name: cat.category,
    value: cat.total_amount,
  })) || []

  const barData = summary?.categories.map((cat) => ({
    category: cat.category,
    amount: cat.total_amount,
  })) || []

  return (
    <div className="reports-page">
      <div className="page-header">
        <h2>Spending Reports</h2>
        <p>Analyze your spending patterns and trends</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Date Range</h3>
        </div>
        <div className="card-body">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="startDate">Start Date</label>
              <input
                type="date"
                id="startDate"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="endDate">End Date</label>
              <input
                type="date"
                id="endDate"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <div className="form-group">
              <button className="btn btn-primary" onClick={loadReport}>
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {loading && <div className="loading">Loading report...</div>}

      {error && <div className="error-message">{error}</div>}

      {summary && !loading && (
        <>
          <div className="card">
            <div className="card-header">
              <h3>Summary</h3>
            </div>
            <div className="card-body">
              <div className="summary-grid">
                <div className="summary-item">
                  <div className="summary-label">Total Income</div>
                  <div className="summary-value income">
                    {formatCurrency(summary.total_income)}
                  </div>
                </div>
                <div className="summary-item">
                  <div className="summary-label">Total Spent</div>
                  <div className="summary-value expense">
                    {formatCurrency(summary.total_spent)}
                  </div>
                </div>
                <div className="summary-item">
                  <div className="summary-label">Net Balance</div>
                  <div
                    className={`summary-value ${
                      summary.net_balance >= 0 ? 'income' : 'expense'
                    }`}
                  >
                    {formatCurrency(summary.net_balance)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {pieData.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3>Spending by Category</h3>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name}: ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {barData.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3>Category Breakdown</h3>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={barData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="category" type="category" />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Bar dataKey="amount" fill="#4ECDC4" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Reports

