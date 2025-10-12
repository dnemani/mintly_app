import React, { useState } from 'react'

function SplitModal({ transaction, categories, onSave, onClose }) {
  const [splits, setSplits] = useState([
    { category: categories[0] || '', amount: 0, notes: '' },
    { category: categories[0] || '', amount: 0, notes: '' },
  ])

  const addSplit = () => {
    setSplits([...splits, { category: categories[0] || '', amount: 0, notes: '' }])
  }

  const removeSplit = (index) => {
    if (splits.length > 2) {
      setSplits(splits.filter((_, i) => i !== index))
    }
  }

  const updateSplit = (index, field, value) => {
    const newSplits = [...splits]
    newSplits[index][field] = field === 'amount' ? parseFloat(value) || 0 : value
    setSplits(newSplits)
  }

  const handleSubmit = () => {
    const totalAmount = splits.reduce((sum, split) => sum + Math.abs(split.amount), 0)
    const expectedAmount = Math.abs(transaction.amount)

    if (Math.abs(totalAmount - expectedAmount) > 0.01) {
      alert(
        `Split amounts ($${totalAmount.toFixed(2)}) must equal transaction amount ($${expectedAmount.toFixed(2)})`
      )
      return
    }

    if (splits.length < 2) {
      alert('Must have at least 2 splits')
      return
    }

    // Convert amounts to negative for expenses
    const formattedSplits = splits.map(split => ({
      category: split.category,
      amount: -Math.abs(split.amount),
      notes: split.notes || null
    }))

    onSave(formattedSplits)
  }

  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Split Transaction</h3>
          <button className="close-btn" onClick={onClose}>
            &times;
          </button>
        </div>
        <div className="modal-body">
          <div className="transaction-info">
            <p><strong>Transaction:</strong> {transaction.description}</p>
            <p><strong>Amount:</strong> ${Math.abs(transaction.amount).toFixed(2)}</p>
          </div>

          <div className="split-entries">
            {splits.map((split, index) => (
              <div key={index} className="split-entry">
                <div className="form-row">
                  <div className="form-group">
                    <label>Category</label>
                    <select
                      value={split.category}
                      onChange={(e) => updateSplit(index, 'category', e.target.value)}
                    >
                      {categories.map((cat) => (
                        <option key={cat} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      value={split.amount || ''}
                      onChange={(e) => updateSplit(index, 'amount', e.target.value)}
                      placeholder="0.00"
                    />
                  </div>
                  <div className="form-group">
                    <label>Notes</label>
                    <input
                      type="text"
                      value={split.notes}
                      onChange={(e) => updateSplit(index, 'notes', e.target.value)}
                      placeholder="Optional"
                    />
                  </div>
                  {splits.length > 2 && (
                    <button
                      type="button"
                      className="btn-small btn-danger"
                      onClick={() => removeSplit(index)}
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          <button type="button" className="btn btn-secondary" onClick={addSplit}>
            + Add Split
          </button>

          <div className="modal-actions">
            <button type="button" className="btn btn-primary" onClick={handleSubmit}>
              Save Split
            </button>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SplitModal

