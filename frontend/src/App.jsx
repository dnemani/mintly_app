import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Upload from './components/Upload'
import Transactions from './components/Transactions'
import Reports from './components/Reports'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="container">
            <div className="nav-brand">
              <h1>💰 Mintly</h1>
            </div>
            <ul className="nav-menu">
              <li><Link to="/" className="nav-link">Upload</Link></li>
              <li><Link to="/transactions" className="nav-link">Transactions</Link></li>
              <li><Link to="/reports" className="nav-link">Reports</Link></li>
            </ul>
          </div>
        </nav>

        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/" element={<Upload />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </div>
        </main>

        <footer className="footer">
          <div className="container">
            <p>&copy; 2025 Mintly. Track your spending, save your future.</p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App

