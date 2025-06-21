"""
Netflix PDF Analyzer - Ultra Fast Version
Uses pre-processed knowledge for instant analysis
Run 'setup_netflix_knowledge.py' first to prepare the data
"""
import os
import json
from pathlib import Path
from crewai import Agent, Task, Crew, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

# Set your Google API key
os.environ["GOOGLE_API_KEY"] = "your_google_gemini_api_key_here"

def load_processed_knowledge():
    """Load pre-processed Netflix knowledge - instant loading!"""
    knowledge_file = Path("processed_knowledge/netflix_knowledge.json")
    
    if not knowledge_file.exists():
        print("❌ Processed knowledge not found!")
        print("🔧 Please run 'python setup_netflix_knowledge.py' first")
        return None
    
    print("⚡ Loading pre-processed Netflix knowledge (instant!)...")
    
    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create knowledge source from processed text
        knowledge_source = StringKnowledgeSource(
            content=data['full_text'],
            metadata=data['metadata']
        )
        
        print(f"✅ Loaded {data['metadata']['total_chars']:,} characters in {data['metadata']['total_chunks']} chunks")
        return knowledge_source, data['metadata']
        
    except Exception as e:
        print(f"❌ Error loading knowledge: {e}")
        return None

def create_crew(knowledge_source):
    """Create CrewAI crew with pre-loaded knowledge"""
    
    # Fast cloud LLM
    llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.1,
    )
    
    # Expert analyst agent
    analyst = Agent(
        role="Netflix Financial Analyst",
        goal="Provide accurate analysis of Netflix's 10-K filing to answer: {question}",
        backstory="""You are an expert financial analyst with deep knowledge of Netflix's business. 
        You have instant access to Netflix's complete 10-K filing and can extract specific data, 
        financial metrics, and strategic insights to answer questions with precision.""",
        knowledge_sources=[knowledge_source],
        llm=llm,
        verbose=True
    )
    
    # Analysis task
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
    
    # Create crew
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
    """Ask a question using the pre-loaded crew"""
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
        print("⚡ Using pre-processed knowledge (super fast!)...")
        
        result = ask_question(crew, question)
        if result:
            print("\n" + "="*60)
            print("📊 ANALYSIS RESULT:")
            print("="*60)
            print(result)
        else:
            print("❌ Analysis failed - please try a different question")

def main():
    print("🚀 Netflix PDF Analyzer - Ultra Fast Edition")
    print("✨ Cloud-powered with pre-processed knowledge!")
    print("=" * 60)
    
    # Check API key
    if os.environ["GOOGLE_API_KEY"] == "your-gemini-api-key-here":
        print("\n❌ Please set your Google API key first!")
        return
    
    # Load processed knowledge
    result = load_processed_knowledge()
    if result is None:
        return
    
    knowledge_source, metadata = result
    print(f"📈 Knowledge from: {metadata['source']}")
    
    # Create crew with loaded knowledge
    print("🤖 Initializing AI crew...")
    crew = create_crew(knowledge_source)
    
    # Default analysis
    default_question = "What are Netflix's total revenues for 2024 and what are the main revenue streams?"
    print(f"\n🔍 Default analysis: {default_question}")
    
    result = ask_question(crew, default_question)
    
    if result:
        print("\n" + "="*60)
        print("✅ NETFLIX ANALYSIS RESULT:")
        print("="*60)
        print(result)
        print("\n🎯 Ultra-fast analysis complete!")
        
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
        print("❌ Initial analysis failed")

if __name__ == "__main__":
    main()
