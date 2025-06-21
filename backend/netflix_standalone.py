"""
Netflix PDF Analyzer - Self-Contained Version
Extracts PDF once, caches it, then runs ultra-fast forever
No separate setup script needed!
"""
import os
import json
import PyPDF2
from pathlib import Path
from crewai import Agent, Task, Crew, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

# Set your Google API key
os.environ["GOOGLE_API_KEY"] = "your_google_gemini_api_key_here"

def extract_pdf_text(pdf_path):
    """Extract all text from PDF file"""
    print(f"📄 Extracting text from {pdf_path}...")
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"📖 Processing {total_pages} pages...")
            
            for i, page in enumerate(pdf_reader.pages, 1):
                if i % 10 == 0:  # Progress indicator
                    print(f"   📄 Page {i}/{total_pages}")
                text += f"\n--- PAGE {i} ---\n"
                text += page.extract_text()
                
        print(f"✅ Extracted {len(text):,} characters from PDF")
        return text
    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return None

def get_or_create_knowledge():
    """Get cached knowledge or extract from PDF if needed"""
    cache_dir = Path("knowledge_cache")
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / "netflix_extracted.json"
    pdf_path = "knowledge/Netflix.pdf"
    
    # Check if cache exists and PDF hasn't changed
    if cache_file.exists():
        try:
            # Check if PDF was modified after cache
            pdf_modified = Path(pdf_path).stat().st_mtime
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # If PDF wasn't modified, use cache
            if cached_data.get('pdf_modified_time') == pdf_modified:
                print("📁 Loading cached Netflix knowledge (instant!)...")
                knowledge_source = StringKnowledgeSource(
                    content=cached_data['full_text'],
                    metadata=cached_data['metadata']
                )
                print(f"✅ Loaded {len(cached_data['full_text']):,} characters from cache")
                return knowledge_source
            else:
                print("🔄 PDF was modified, re-extracting...")
        except Exception as e:
            print(f"⚠️ Cache corrupted ({e}), re-extracting...")
    
    # Extract from PDF (first time or PDF changed)
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found at {pdf_path}")
        print("Please ensure Netflix.pdf is in the knowledge/ folder")
        return None
    
    print("🔄 First time setup: Extracting PDF text...")
    print("💾 This will be cached for instant future use!")
    
    pdf_text = extract_pdf_text(pdf_path)
    if pdf_text is None:
        return None
    
    # Cache the extracted text
    try:
        cache_data = {
            'full_text': pdf_text,
            'pdf_modified_time': Path(pdf_path).stat().st_mtime,
            'metadata': {
                'source': 'Netflix 10-K Filing',
                'total_chars': len(pdf_text),
                'cached_date': str(Path(pdf_path).stat().st_mtime)
            }
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False)
        
        print("✅ PDF text cached for future instant loading!")
        
    except Exception as e:
        print(f"⚠️ Couldn't cache PDF (will re-extract next time): {e}")
    
    # Create knowledge source
    knowledge_source = StringKnowledgeSource(
        content=pdf_text,
        metadata=cache_data['metadata']
    )
    
    return knowledge_source

def create_crew(knowledge_source):
    """Create CrewAI crew with knowledge"""
    llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.1,
    )
    
    analyst = Agent(
        role="Netflix Financial Analyst",
        goal="Provide accurate analysis of Netflix's 10-K filing to answer: {question}",
        backstory="""You are an expert financial analyst with deep knowledge of Netflix's business. 
        You have access to Netflix's complete 10-K filing and can extract specific data, 
        financial metrics, and strategic insights to answer questions with precision.""",
        knowledge_sources=[knowledge_source],
        llm=llm,
        verbose=True
    )
    
    task = Task(
        description="""Analyze Netflix's 10-K filing to answer: {question}
        
        Provide a comprehensive response that includes:
        1. Direct answer to the question with specific numbers/data
        2. Relevant context from the filing
        3. Key insights and implications
        4. Specific quotes or references when applicable""",
        expected_output="A detailed, data-driven analysis with specific numbers and insights from Netflix's 10-K filing.",
        agent=analyst
    )
    
    crew = Crew(
        agents=[analyst],
        tasks=[task],
        verbose=True,
        embedder={
            "provider": "google",
            "config": {
                "model": "models/embedding-001",
                "api_key": os.environ["GOOGLE_API_KEY"]
            }
        }
    )
    
    return crew

def ask_question(crew, question):
    """Ask a question using the crew"""
    try:
        result = crew.kickoff(inputs={"question": question})
        return result
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

def interactive_mode(crew):
    """Interactive mode for multiple questions"""
    print("\n🎯 Interactive Netflix Analysis Mode")
    print("Type 'quit', 'exit', or 'q' to stop")
    print("-" * 60)
    
    while True:
        question = input("\n❓ Ask about Netflix's 10-K filing: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if not question:
            print("Please enter a question!")
            continue
            
        print(f"\n🔍 Analyzing: {question}")
        print("⚡ Using cached knowledge...")
        
        result = ask_question(crew, question)
        if result:
            print("\n" + "="*60)
            print("📊 ANALYSIS RESULT:")
            print("="*60)
            print(result)
        else:
            print("❌ Analysis failed - please try a different question")

def main():
    print("🚀 Netflix PDF Analyzer - Self-Contained Edition")
    print("✨ Extracts once, runs fast forever!")
    print("=" * 60)
    
    # Check API key
    if os.environ["GOOGLE_API_KEY"] == "your-gemini-api-key-here":
        print("\n❌ Please set your Google API key first!")
        return
    
    # Get or create knowledge (handles caching automatically)
    knowledge_source = get_or_create_knowledge()
    if knowledge_source is None:
        return
    
    # Create crew
    print("🤖 Initializing AI crew...")
    crew = create_crew(knowledge_source)
    
    # Default analysis
    default_question = "What are Netflix's total revenues for 2024 and what are the main revenue streams?"
    print(f"\n🔍 Running analysis: {default_question}")
    
    result = ask_question(crew, default_question)
    
    if result:
        print("\n" + "="*60)
        print("✅ NETFLIX ANALYSIS RESULT:")
        print("="*60)
        print(result)
        print("\n🎯 Analysis complete!")
        
        # Offer interactive mode
        while True:
            choice = input("\n🤔 Want to ask more questions? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                interactive_mode(crew)
                break
            elif choice in ['n', 'no']:
                print("👋 Thanks for using Netflix Analyzer!")
                break
            else:
                print("Please enter 'y' or 'n'")
    else:
        print("❌ Analysis failed")

if __name__ == "__main__":
    main()
