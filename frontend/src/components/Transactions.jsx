import React, { useState, useEffect } from 'react'
import {
  getTransactions,
  getCategories,
  updateTransactionCategory,
  deleteTransaction,
  splitTransaction,
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

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [txnData, catData] = await Promise.all([
        getTransactions(100),
        getCategories(),
      ])
      
      setTransactions(txnData.transactions || [])
      setCategories(catData.categories || [])
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
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((txn) => (
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

