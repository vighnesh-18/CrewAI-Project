"""
Netflix PDF Analyzer - Flask Backend API
Provides REST API endpoints for the React frontend
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import os
import json
import re
import PyPDF2
from pathlib import Path
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify required environment variables
required_env_vars = ['GOOGLE_API_KEY']
missing_vars = []

for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file and ensure these variables are set.")
    exit(1)

# Configuration from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', 4000))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
MAX_CHUNKS_PER_QUERY = int(os.getenv('MAX_CHUNKS_PER_QUERY', 5))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Set API key for Google Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=cors_origins)

# Global variables for caching
pdf_chunks = None
crew = None
pdf_text = None

def extract_and_cache_pdf():
    """Extract PDF text and cache it"""
    cache_file = Path("lightning_cache.json")
    pdf_path = "knowledge/Netflix.pdf"
    
    # Check cache
    if cache_file.exists():
        try:
            pdf_modified = Path(pdf_path).stat().st_mtime
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            if cached.get('pdf_modified') == pdf_modified:
                print("⚡ Loading cached text (instant!)...")
                return cached['text'], cached['chunks']
        except:
            pass
    
    # Extract PDF
    print("📄 Extracting PDF (one-time setup)...")
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None
    
    # Create smart chunks by sections
    chunks = create_smart_chunks(text)
    
    # Cache everything
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'text': text,
                'chunks': chunks,
                'pdf_modified': Path(pdf_path).stat().st_mtime
            }, f, ensure_ascii=False)
        print(f"✅ Cached {len(text):,} chars in {len(chunks)} sections")
    except:
        print("⚠️ Couldn't cache (will re-extract next time)")
    
    return text, chunks

def create_smart_chunks(text):
    """Create intelligent chunks based on document structure"""
    print("✂️ Creating smart sections...")
    
    sections = []
    section_patterns = [
        r'Item \d+\.',  # SEC filing items
        r'PART [IVX]+',  # Parts
        r'Table of Contents',
        r'CONSOLIDATED STATEMENTS',
        r'Notes to Consolidated',
        r'Risk Factors',
        r'Management.s Discussion',
    ]
    
    current_section = ""
    section_title = "Introduction"
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        is_header = False
        for pattern in section_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                if current_section.strip():
                    sections.append({
                        'title': section_title,
                        'content': current_section.strip()
                    })
                
                section_title = line[:100]
                current_section = line + "\n"
                is_header = True
                break
        
        if not is_header:
            current_section += line + "\n"
    
    if current_section.strip():
        sections.append({
            'title': section_title,
            'content': current_section.strip()
        })
    
    print(f"📚 Created {len(sections)} smart sections")
    return sections

def find_relevant_sections(chunks, question, max_sections=None):
    """Fast text-based relevance search"""
    if max_sections is None:
        max_sections = MAX_CHUNKS_PER_QUERY
        
    question_lower = question.lower()
    keywords = [w for w in question_lower.split() if len(w) > 2]
    
    scored_sections = []
    
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        title_lower = chunk['title'].lower()
        
        score = 0
        for keyword in keywords:
            score += title_lower.count(keyword) * 3
            score += content_lower.count(keyword) * 1
        
        financial_terms = ['revenue', 'income', 'cost', 'profit', 'margin', 'cash', 'debt', 'subscriber']
        for term in financial_terms:
            if term in question_lower and term in content_lower:
                score += 2
        
        if score > 0:
            scored_sections.append((score, chunk))
    
    scored_sections.sort(reverse=True, key=lambda x: x[0])
    return [chunk for score, chunk in scored_sections[:max_sections]]

def create_lightning_crew():
    """Create minimal crew for fast analysis"""
    llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.0,
    )
    
    analyst = Agent(
        role="Netflix Analyst",
        goal="Answer questions about Netflix using provided context: {question}",
        backstory="Expert analyst who quickly extracts insights from Netflix financial data.",
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
    
    task = Task(
        description="""Using the provided Netflix context, answer: {question}
        
        Context: {context}
        
        Be concise and data-focused. Include specific numbers when available.""",
        expected_output="Direct, data-driven answer with key metrics.",
        agent=analyst
    )
    
    crew = Crew(
        agents=[analyst],
        tasks=[task],
        verbose=False,
    )
    
    return crew

def ask_lightning_question(crew, chunks, question):
    """Lightning-fast question answering"""
    relevant_sections = find_relevant_sections(chunks, question)
    
    if not relevant_sections:
        return "❌ No relevant information found in the document."
    
    # Combine relevant content
    context = "\n\n".join([
        f"SECTION: {section['title']}\n{section['content'][:2000]}"
        for section in relevant_sections
    ])
    
    try:
        result = crew.kickoff(inputs={
            "question": question,
            "context": context[:8000]
        })
        return result
    except Exception as e:
        return f"❌ Analysis error: {e}"

# API Routes
@app.route('/')
def serve():
    """Serve the React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Netflix Analyzer API is running"
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_question():
    """Analyze a question about Netflix"""
    global pdf_chunks, crew
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # Initialize if needed
        if pdf_chunks is None:
            text, pdf_chunks = extract_and_cache_pdf()
            if not pdf_chunks:
                return jsonify({"error": "Failed to load PDF data"}), 500
        
        if crew is None:
            crew = create_lightning_crew()
        
        start_time = time.time()
        result = ask_lightning_question(crew, pdf_chunks, question)
        processing_time = time.time() - start_time
        
        return jsonify({
            "answer": str(result),
            "processing_time": round(processing_time, 2),
            "question": question
        })
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/sample-questions')
def sample_questions():
    """Get sample questions for the UI"""
    questions = [
        "What is Netflix's total revenue for 2024?",
        "What are Netflix's main revenue streams?",
        "How many subscribers does Netflix have?",
        "What are Netflix's biggest risks?",
        "What is Netflix's content spending?",
        "How much cash does Netflix have?",
        "What are Netflix's operating margins?",
        "What markets is Netflix expanding into?"
    ]
    return jsonify({"questions": questions})

@app.route('/api/stats')
def get_stats():
    """Get analyzer statistics"""
    global pdf_chunks, pdf_text
    
    if pdf_chunks is None:
        return jsonify({"status": "not_initialized"})
    
    return jsonify({
        "total_sections": len(pdf_chunks),
        "total_characters": len(pdf_text) if pdf_text else 0,
        "status": "ready"
    })

if __name__ == '__main__':
    print("🚀 Starting Netflix PDF Analyzer API...")
    print("📄 Loading PDF data...")
    
    # Pre-load data    pdf_text, pdf_chunks = extract_and_cache_pdf()
    if pdf_chunks:
        print(f"✅ Loaded {len(pdf_chunks)} sections")
        crew = create_lightning_crew()
        print("🤖 AI crew ready")
    else:
        print("❌ Failed to load PDF")
    
    print("🌐 Starting Flask server...")
    print(f"📱 Frontend: http://localhost:5173")
    print(f"🔧 API: http://localhost:{FLASK_PORT}")
    print(f"🔑 Using Google Gemini API")
    print(f"💾 Cache enabled: {CACHE_ENABLED}")
    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=FLASK_PORT)
