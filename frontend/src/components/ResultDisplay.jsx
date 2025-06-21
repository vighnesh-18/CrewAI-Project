import './ResultDisplay.css'

function ResultDisplay({ result, onClear }) {
  const formatTime = (seconds) => {
    return seconds < 1 ? '< 1s' : `${seconds.toFixed(1)}s`
  }

  return (
    <div className="result-container">
      <div className="result-header">
        <div className="result-title">
          <h3>📊 Analysis Complete!</h3>
          <div className="result-meta">
            <span className="time-badge">
              ⚡ {formatTime(result.analysis_time || 0)}
            </span>
            <span className="status-badge success">
              ✅ Success
            </span>
          </div>
        </div>
        <button onClick={onClear} className="clear-btn">
          🗑️ Clear
        </button>
      </div>

      <div className="result-content">
        <div className="question-section">
          <h4>❓ Your Question:</h4>
          <p className="question-text">{result.question}</p>
        </div>

        <div className="answer-section">
          <h4>🤖 AI Analysis:</h4>
          <div className="answer-text">
            {result.answer.split('\n').map((paragraph, index) => (
              paragraph.trim() && (
                <p key={index} className="answer-paragraph">
                  {paragraph}
                </p>
              )
            ))}
          </div>
        </div>

        {result.sections_used && (
          <div className="sources-section">
            <h4>📚 Sources Used:</h4>
            <div className="sources-list">
              {result.sections_used.map((section, index) => (
                <div key={index} className="source-item">
                  <span className="source-title">{section}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="result-footer">
        <p className="disclaimer">
          ℹ️ Analysis based on Netflix's 10-K filing. Always verify important information with official sources.
        </p>
      </div>
    </div>
  )
}

export default ResultDisplay
