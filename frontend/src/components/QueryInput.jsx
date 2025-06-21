import { useState } from 'react'
import './QueryInput.css'

function QueryInput({ query, setQuery, onAnalyze, loading }) {
  const [showSuggestions, setShowSuggestions] = useState(false)

  const suggestions = [
    "What is Netflix's total revenue for 2024?",
    "What are Netflix's main revenue streams?", 
    "How many subscribers does Netflix have?",
    "What are Netflix's biggest risk factors?",
    "What is Netflix's content spending?",
    "What are Netflix's operating expenses?",
    "How much cash does Netflix have?",
    "What is Netflix's debt situation?"
  ]

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion)
    setShowSuggestions(false)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onAnalyze()
  }

  return (
    <div className="query-section">
      <div className="query-header">
        <h2>🤖 Ask anything about Netflix's 10-K filing</h2>
        <p>Get instant AI-powered insights from Netflix's financial documents</p>
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-container">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: What is Netflix's total revenue for 2024 and how did it change from 2023?"
            className="query-input"
            rows={3}
            disabled={loading}
          />
          <button 
            type="submit" 
            className={`analyze-btn ${loading ? 'loading' : ''}`}
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                <span className="btn-icon">⚡</span>
                Analyze
              </>
            )}
          </button>
        </div>
      </form>

      <div className="suggestions-section">
        <button 
          className="suggestions-toggle"
          onClick={() => setShowSuggestions(!showSuggestions)}
        >
          💡 {showSuggestions ? 'Hide' : 'Show'} Example Questions
        </button>

        {showSuggestions && (
          <div className="suggestions-grid">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={loading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default QueryInput
