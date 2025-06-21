import './LoadingSpinner.css'

function LoadingSpinner() {
  return (
    <div className="loading-container">
      <div className="loading-spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
      </div>
      <div className="loading-text">
        <h3>🧠 AI is analyzing Netflix's 10-K filing...</h3>
        <p>⚡ Lightning-fast search in progress</p>
        <div className="loading-steps">
          <div className="step active">🔍 Finding relevant sections</div>
          <div className="step active">🤖 AI analysis in progress</div>
          <div className="step">📊 Generating insights</div>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
