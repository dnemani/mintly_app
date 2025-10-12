import React, { useState } from 'react'
import { uploadTransactions } from '../services/api'
import { useNavigate } from 'react-router-dom'

function Upload() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && (selectedFile.name.endsWith('.csv') || selectedFile.name.endsWith('.CSV'))) {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('Please select a CSV file')
      setFile(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)
    setMessage(null)

    try {
      const result = await uploadTransactions(file)
      setMessage(`Success! Uploaded ${result.count} transactions.`)
      setFile(null)
      e.target.reset()
      
      // Redirect to transactions page after 2 seconds
      setTimeout(() => {
        navigate('/transactions')
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading file')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-page">
      <div className="page-header">
        <h2>Upload Transactions</h2>
        <p>Upload your credit card statement in CSV format</p>
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="csvFile">Select CSV File</label>
              <input
                type="file"
                id="csvFile"
                accept=".csv,.CSV"
                onChange={handleFileChange}
                disabled={uploading}
              />
              <small>
                Supports: Costco Visa, Citibank, Chase, and generic formats
              </small>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={!file || uploading}
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
          </form>

          {uploading && (
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
          )}

          {message && (
            <div className="status-message success">
              {message}
            </div>
          )}

          {error && (
            <div className="status-message error">
              {error}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Supported Banks & Formats</h3>
        </div>
        <div className="card-body">
          <div className="bank-formats">
            <div className="bank-format">
              <h4>🏦 Costco Visa</h4>
              <code>Status, Date, Description, Debit, Credit, Member Name</code>
            </div>
            <div className="bank-format">
              <h4>🏦 Citibank</h4>
              <code>Status, Date, Description, Debit, Credit</code>
            </div>
            <div className="bank-format">
              <h4>🏦 Chase</h4>
              <code>Transaction Date, Post Date, Description, Amount, Type</code>
            </div>
            <div className="bank-format">
              <h4>🏦 Generic</h4>
              <code>Date, Description, Amount</code>
            </div>
          </div>
          <p className="info-text">
            The app automatically detects your bank's format!
          </p>
        </div>
      </div>
    </div>
  )
}

export default Upload

