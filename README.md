# Netflix 10-K PDF Analyzer 🚀

A lightning-fast AI-powered Netflix 10-K financial document analyzer with a modern React frontend and Flask backend. Get instant insights from Netflix's financial reports using advanced AI analysis.

![Project Banner](https://img.shields.io/badge/Netflix-PDF%20Analyzer-red?style=for-the-badge&logo=netflix)

## ✨ Features

- **Lightning Fast Analysis**: Optimized PDF processing with smart chunking and caching
- **AI-Powered Insights**: Uses Google Gemini and CrewAI for intelligent document analysis
- **Modern UI**: Beautiful, responsive React frontend built with Vite
- **Real-time Updates**: Live status indicators and instant results
- **Smart Caching**: Reduces analysis time with intelligent caching system
- **RESTful API**: Clean Flask backend with comprehensive endpoints

## 🏗️ Architecture

```
├── backend/           # Flask API server
│   ├── app.py        # Main Flask application
│   ├── knowledge/    # PDF documents storage
│   └── requirements.txt
├── frontend/         # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   └── App.jsx
│   └── package.json
├── .env             # Environment variables
└── .gitignore       # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API Key

### 1. Clone and Setup

```bash
git clone <repository-url>
```

### 2. Environment Configuration

Copy `.env` file and add your API keys:

```bash
cp .env .env.local
# Edit .env.local with your actual API keys
```

Required environment variables:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv netflix_ai_env

# Activate virtual environment (Windows)
netflix_ai_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

Backend will be available at `http://localhost:5000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Analyze Document
```http
POST /analyze
Content-Type: application/json

{
  "question": "What was Netflix's revenue in 2023?"
}
```

### Get Analysis Statistics
```http
GET /stats
```

### Sample Questions
```http
GET /sample-questions
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API Key | Required |
| `FLASK_PORT` | Backend server port | 5000 |
| `REACT_APP_API_URL` | Frontend API URL | http://localhost:5173 |
| `CACHE_ENABLED` | Enable response caching | true |
| `MAX_CHUNK_SIZE` | PDF chunk size | 4000 |

### Frontend Configuration

The frontend automatically connects to the backend API. Update `REACT_APP_API_URL` in `.env` if deploying to different hosts.

## 🎨 UI Features

- **Full-page Layout**: Maximizes screen real estate
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Live Status**: Real-time backend connection indicator
- **Modern Styling**: Clean, Netflix-inspired color scheme
- **Loading States**: Smooth loading animations
- **Error Handling**: User-friendly error messages

## 🧠 AI Analysis

The system uses:
- **Google Gemini**: Advanced language model for document analysis
- **CrewAI**: Orchestrates AI agents for comprehensive analysis
- **Smart Chunking**: Efficiently processes large PDF documents
- **Contextual Search**: Finds relevant sections for each query

## 📊 Performance

- **Caching**: Responses cached to reduce API calls
- **Chunking**: Smart text segmentation for optimal processing
- **Concurrent Processing**: Parallel analysis of document sections
- **Memory Optimization**: Efficient PDF loading and processing

## 🔒 Security

- **Environment Variables**: Sensitive data stored in `.env`
- **CORS Protection**: Configured for development and production
- **Input Validation**: Sanitized user inputs
- **Error Handling**: Secure error messages

## 🚀 Deployment

### Backend (Flask)

```bash
# Production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend (React)

```bash
npm run build
# Deploy dist/ folder to your hosting provider
```

### Environment Setup

For production:
1. Set `FLASK_ENV=production`
2. Update `REACT_APP_API_URL` to production backend URL
3. Configure CORS origins for production domains

## 📁 File Structure

```
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── knowledge/
│   │   └── Netflix.pdf        # Netflix 10-K document
│   ├── lightning_cache.json   # Response cache (auto-generated)
│   ├── netflix_ai_env/        # Python virtual environment
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── QueryInput.jsx
│   │   │   ├── ResultDisplay.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── .env                       # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🛠️ Troubleshooting

### Common Issues

**Backend won't start:**
- Check if virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

**Frontend connection issues:**
- Verify backend is running on port 5000
- Check CORS configuration in `app.py`
- Confirm `REACT_APP_API_URL` in `.env`

**API key errors:**
- Verify `GOOGLE_API_KEY` is set in `.env`
- Check API key permissions and quotas
- Ensure `.env` file is not in `.gitignore`

**PDF not found:**
- Verify `Netflix.pdf` exists in `backend/knowledge/`
- Check file permissions
- Ensure file is not corrupted

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
FLASK_DEBUG=True
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed description

---

Built with ❤️ using React, Flask, and AI
