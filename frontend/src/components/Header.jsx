import './Header.css'

function Header({ apiStatus }) {
  const getStatusIndicator = () => {
    switch (apiStatus) {
      case 'connected':
        return { icon: '🟢', text: 'Connected' }
      case 'error':
        return { icon: '🔴', text: 'Disconnected' }
      case 'checking':
      default:
        return { icon: '🟡', text: 'Connecting...' }
    }
  }

  const status = getStatusIndicator()

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <span className="logo-icon">🎬</span>
          <div>
            <h1>Netflix AI Analyzer</h1>
            <div className="status-indicator">
              <span className="status-icon">{status.icon}</span>
              <span className="status-text">{status.text}</span>
            </div>
          </div>
        </div>
        <div className="header-subtitle">
          <p>⚡ Lightning-fast analysis of Netflix's 10-K filing using Google Gemini AI</p>
          <p className="header-description">
            Ask any question about Netflix's financial data, business strategy, or performance metrics
          </p>
        </div>
      </div>
    </header>
  )
}

export default Header
