"""
Netflix PDF Analyzer - LIGHTNING FAST
Direct text search + LLM analysis without embedding overhead
"""
import os
import json
import re
import PyPDF2
from pathlib import Path
from crewai import Agent, Task, Crew, LLM

# Set your Google API key
os.environ["GOOGLE_API_KEY"] = "your_google_gemini_api_key_here"

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
    
    # Split by major sections
    sections = []
    
    # Look for major headings/sections
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
            
        # Check if this line is a section header
        is_header = False
        for pattern in section_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Save previous section
                if current_section.strip():
                    sections.append({
                        'title': section_title,
                        'content': current_section.strip()
                    })
                
                # Start new section
                section_title = line[:100]  # First 100 chars as title
                current_section = line + "\n"
                is_header = True
                break
        
        if not is_header:
            current_section += line + "\n"
    
    # Add final section
    if current_section.strip():
        sections.append({
            'title': section_title,
            'content': current_section.strip()
        })
    
    print(f"📚 Created {len(sections)} smart sections")
    return sections

def find_relevant_sections(chunks, question, max_sections=3):
    """Fast text-based relevance search"""
    question_lower = question.lower()
    
    # Keywords to look for
    keywords = question_lower.split()
    keywords = [w for w in keywords if len(w) > 2]  # Skip short words
    
    scored_sections = []
    
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        title_lower = chunk['title'].lower()
        
        # Score based on keyword matches
        score = 0
        
        # Higher weight for title matches
        for keyword in keywords:
            score += title_lower.count(keyword) * 3
            score += content_lower.count(keyword) * 1
        
        # Bonus for financial terms
        financial_terms = ['revenue', 'income', 'cost', 'profit', 'margin', 'cash', 'debt', 'subscriber']
        for term in financial_terms:
            if term in question_lower and term in content_lower:
                score += 2
        
        if score > 0:
            scored_sections.append((score, chunk))
    
    # Return top sections
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
    print("🔍 Finding relevant sections...")
    relevant_sections = find_relevant_sections(chunks, question)
    
    if not relevant_sections:
        return "❌ No relevant information found in the document."
    
    # Combine relevant content
    context = "\n\n".join([
        f"SECTION: {section['title']}\n{section['content'][:2000]}"  # Limit content
        for section in relevant_sections
    ])
    
    print("🧠 Analyzing with AI...")
    try:
        result = crew.kickoff(inputs={
            "question": question,
            "context": context[:8000]  # Stay within token limits
        })
        return result
    except Exception as e:
        return f"❌ Analysis error: {e}"

def main():
    print("🚀 Netflix PDF Analyzer - LIGHTNING EDITION")
    print("⚡ Direct search + AI analysis = Ultra Fast!")
    print("=" * 60)
    
    # Check API key
    if os.environ["GOOGLE_API_KEY"] == "your-gemini-api-key-here":
        print("❌ Please set your Google API key first!")
        return
    
    # Load PDF data
    text, chunks = extract_and_cache_pdf()
    if not text or not chunks:
        print("❌ Failed to load PDF data")
        return
    
    # Create crew
    print("🤖 Creating lightning-fast crew...")
    crew = create_lightning_crew()
    
    # Demo question
    demo_q = "What is Netflix's 2024 total revenue?"
    print(f"\n🔍 Demo: {demo_q}")
    
    import time
    start = time.time()
    result = ask_lightning_question(crew, chunks, demo_q)
    elapsed = time.time() - start
    
    print(f"\n⚡ LIGHTNING RESULT ({elapsed:.1f}s):")
    print("=" * 50)
    print(result)
    
    # Interactive mode
    print(f"\n🎯 Analysis completed in {elapsed:.1f} seconds!")
    choice = input("\n🤔 Try interactive lightning mode? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes']:
        print("\n⚡ Lightning Interactive Mode")
        print("Type 'quit' to exit")
        print("-" * 40)
        
        while True:
            question = input("\n❓ Ask about Netflix: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
            
            start = time.time()
            result = ask_lightning_question(crew, chunks, question)
            elapsed = time.time() - start
            
            print(f"\n⚡ RESULT ({elapsed:.1f}s):")
            print("-" * 30)
            print(result)
    else:
        print("👋 Thanks for using Lightning Netflix Analyzer!")

if __name__ == "__main__":
    main()
