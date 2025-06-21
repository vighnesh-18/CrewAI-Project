import { useState, useEffect } from 'react'
import './App.css'
import Header from './components/Header'
import QueryInput from './components/QueryInput'
import ResultDisplay from './components/ResultDisplay'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [apiStatus, setApiStatus] = useState('checking')

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/health')
      if (response.ok) {
        setApiStatus('connected')
      } else {
        setApiStatus('error')
      }
    } catch (error) {
      setApiStatus('error')
    }
  }

  const handleAnalyze = async () => {
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const clearResults = () => {
    setResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <Header apiStatus={apiStatus} />
      
      <main className="main-content">
        <div className="container">
          {apiStatus === 'error' && (
            <div className="error-message">
              <h3>🔌 Connection Error</h3>
              <p>Cannot connect to the backend API. Make sure the Flask server is running on port 5000.</p>
              <button onClick={checkApiHealth} className="btn-secondary">
                Retry Connection
              </button>
            </div>
          )}

          {apiStatus === 'connected' && (
            <>
              <QueryInput 
                query={query}
                setQuery={setQuery}
                onAnalyze={handleAnalyze}
                loading={loading}
              />

              {loading && <LoadingSpinner />}
              
              {error && (
                <div className="error-message">
                  <h3>❌ Analysis Error</h3>
                  <p>{error}</p>
                  <button onClick={clearResults} className="btn-secondary">
                    Try Again
                  </button>
                </div>
              )}

              {result && (
                <ResultDisplay 
                  result={result}
                  onClear={clearResults}
                />
              )}
            </>
          )}

          {apiStatus === 'checking' && (
            <div className="checking-connection">
              <LoadingSpinner />
              <p>Connecting to Netflix AI Analyzer...</p>
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>🚀 Netflix AI Analyzer | Powered by Google Gemini & CrewAI | Lightning Fast Analysis</p>
        </div>
      </footer>
    </div>
  )
}

export default App
