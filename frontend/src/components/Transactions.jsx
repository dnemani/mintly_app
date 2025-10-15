import React, { useState, useEffect } from 'react'
import {
  getTransactions,
  getCategories,
  updateTransactionCategory,
  deleteTransaction,
  splitTransaction,
  addTagToTransaction,
  removeTagFromTransaction,
  getAllSources,
  getAllMerchants,
} from '../services/api'
import { format } from 'date-fns'
import SplitModal from './SplitModal'

function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [splitModalOpen, setSplitModalOpen] = useState(false)
  const [selectedTransaction, setSelectedTransaction] = useState(null)
  const [newTag, setNewTag] = useState({})
  const [sources, setSources] = useState([])
  const [merchants, setMerchants] = useState([])
  const [filters, setFilters] = useState({
    source: '',
    merchant: '',
    category: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [txnData, catData, sourcesData, merchantsData] = await Promise.all([
        getTransactions(100),
        getCategories(),
        getAllSources(),
        getAllMerchants(),
      ])
      
      setTransactions(txnData.transactions || [])
      setCategories(catData.categories || [])
      setSources(sourcesData.sources || [])
      setMerchants(merchantsData.merchants || [])
    } catch (err) {
      setError('Error loading transactions')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCategoryChange = async (transactionId, newCategory) => {
    try {
      await updateTransactionCategory(transactionId, newCategory)
      // Update local state
      setTransactions(prev =>
        prev.map(txn =>
          txn.id === transactionId ? { ...txn, category: newCategory } : txn
        )
      )
    } catch (err) {
      alert('Error updating category')
      console.error(err)
    }
  }

  const handleDelete = async (transactionId) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) {
      return
    }

    try {
      await deleteTransaction(transactionId)
      setTransactions(prev => prev.filter(txn => txn.id !== transactionId))
    } catch (err) {
      alert('Error deleting transaction')
      console.error(err)
    }
  }

  const handleSplitClick = (transaction) => {
    setSelectedTransaction(transaction)
    setSplitModalOpen(true)
  }

  const handleSplitSave = async (splits) => {
    try {
      await splitTransaction(selectedTransaction.id, splits)
      setSplitModalOpen(false)
      setSelectedTransaction(null)
      loadData() // Reload to show split transactions
    } catch (err) {
      alert(err.response?.data?.detail || 'Error splitting transaction')
    }
  }

  const handleAddTag = async (transactionId, tagName) => {
    if (!tagName || !tagName.trim()) return
    
    try {
      await addTagToTransaction(transactionId, tagName.trim())
      // Update local state
      setTransactions(prev =>
        prev.map(txn =>
          txn.id === transactionId
            ? { ...txn, tags: [...(txn.tags || []), tagName.trim()] }
            : txn
        )
      )
      setNewTag({ ...newTag, [transactionId]: '' })
    } catch (err) {
      alert('Error adding tag')
      console.error(err)
    }
  }

  const handleRemoveTag = async (transactionId, tagName) => {
    try {
      await removeTagFromTransaction(transactionId, tagName)
      // Update local state
      setTransactions(prev =>
        prev.map(txn =>
          txn.id === transactionId
            ? { ...txn, tags: (txn.tags || []).filter(t => t !== tagName) }
            : txn
        )
      )
    } catch (err) {
      alert('Error removing tag')
      console.error(err)
    }
  }

  const filteredTransactions = transactions.filter(txn => {
    if (filters.source && txn.source !== filters.source) return false
    if (filters.merchant && txn.merchant !== filters.merchant) return false
    if (filters.category && txn.category !== filters.category) return false
    return true
  })

  const formatAmount = (amount) => {
    const abs = Math.abs(amount)
    return amount < 0 ? `-$${abs.toFixed(2)}` : `$${abs.toFixed(2)}`
  }

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy')
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading">Loading transactions...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">{error}</div>
        <button onClick={loadData} className="btn btn-primary">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="transactions-page">
      <div className="page-header">
        <h2>Your Transactions</h2>
        <button onClick={loadData} className="btn btn-secondary">
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-body">
          <h3>Filters</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div>
              <label>Source</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters({ ...filters, source: e.target.value })}
                className="category-select"
              >
                <option value="">All Sources</option>
                {sources.map((source) => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label>Merchant</label>
              <select
                value={filters.merchant}
                onChange={(e) => setFilters({ ...filters, merchant: e.target.value })}
                className="category-select"
              >
                <option value="">All Merchants</option>
                {merchants.map((m) => (
                  <option key={m.name} value={m.name}>
                    {m.name} ({m.count})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label>Category</label>
              <select
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                className="category-select"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-end' }}>
              <button
                onClick={() => setFilters({ source: '', merchant: '', category: '' })}
                className="btn btn-secondary"
                style={{ width: '100%' }}
              >
                Clear Filters
              </button>
            </div>
          </div>
          <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
            Showing {filteredTransactions.length} of {transactions.length} transactions
          </div>
        </div>
      </div>

      {transactions.length === 0 ? (
        <div className="card">
          <div className="card-body">
            <p>No transactions found. <a href="/">Upload a CSV file</a> to get started.</p>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-body">
            <div className="table-container">
              <table className="transactions-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Source / Merchant</th>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Tags</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTransactions.map((txn) => (
                    <tr
                      key={txn.id}
                      className={txn.is_split ? 'split-transaction' : ''}
                    >
                      <td>{formatDate(txn.date)}</td>
                      <td>
                        {txn.description}
                        {txn.parent_transaction_id && (
                          <span className="badge">Split</span>
                        )}
                      </td>
                      <td style={{ fontSize: '12px' }}>
                        {txn.source && <div style={{ color: '#0066cc' }}>📍 {txn.source}</div>}
                        {txn.merchant && <div style={{ color: '#666' }}>🏪 {txn.merchant}</div>}
                      </td>
                      <td className={txn.amount < 0 ? 'expense' : 'income'}>
                        {formatAmount(txn.amount)}
                      </td>
                      <td>
                        <select
                          value={txn.category}
                          onChange={(e) =>
                            handleCategoryChange(txn.id, e.target.value)
                          }
                          disabled={txn.is_split && !txn.parent_transaction_id}
                          className="category-select"
                        >
                          {categories.map((cat) => (
                            <option key={cat} value={cat}>
                              {cat}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                            {(txn.tags || []).map((tag) => (
                              <span
                                key={tag}
                                className="badge"
                                style={{
                                  backgroundColor: '#e7f3ff',
                                  color: '#0066cc',
                                  padding: '2px 8px',
                                  borderRadius: '12px',
                                  fontSize: '11px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '4px'
                                }}
                              >
                                {tag}
                                <button
                                  onClick={() => handleRemoveTag(txn.id, tag)}
                                  style={{
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    padding: '0 2px',
                                    fontSize: '14px',
                                    color: '#cc0000'
                                  }}
                                  title="Remove tag"
                                >
                                  ×
                                </button>
                              </span>
                            ))}
                          </div>
                          <div style={{ display: 'flex', gap: '5px' }}>
                            <input
                              type="text"
                              placeholder="Add tag..."
                              value={newTag[txn.id] || ''}
                              onChange={(e) =>
                                setNewTag({ ...newTag, [txn.id]: e.target.value })
                              }
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  handleAddTag(txn.id, newTag[txn.id])
                                }
                              }}
                              style={{
                                flex: 1,
                                padding: '4px 8px',
                                fontSize: '12px',
                                border: '1px solid #ddd',
                                borderRadius: '4px'
                              }}
                            />
                            <button
                              onClick={() => handleAddTag(txn.id, newTag[txn.id])}
                              className="btn-small"
                              style={{ padding: '4px 8px', fontSize: '12px' }}
                            >
                              +
                            </button>
                          </div>
                        </div>
                      </td>
                      <td>
                        {!txn.is_split && !txn.parent_transaction_id && (
                          <button
                            onClick={() => handleSplitClick(txn)}
                            className="btn-small"
                          >
                            Split
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(txn.id)}
                          className="btn-small btn-danger"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {splitModalOpen && selectedTransaction && (
        <SplitModal
          transaction={selectedTransaction}
          categories={categories}
          onSave={handleSplitSave}
          onClose={() => {
            setSplitModalOpen(false)
            setSelectedTransaction(null)
          }}
        />
      )}
    </div>
  )
}

export default Transactions

