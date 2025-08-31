import os
import sys

# Fix Windows encoding issues
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# DIRECT API KEY SETTING - REPLACE WITH YOUR REAL KEY
os.environ['GEMINI_API_KEY'] = 'AIzaSyDAENolswXCr1E8sLF8O1l6GHY6kudTSbc'  # ← PUT YOUR REAL KEY HERE
os.environ['LITELLM_LOG'] = 'DEBUG'

from utils.logger import log_info, log_error, log_success, log_step
from agents.data_collector import run as collect_data
from agents.identify_products import run as identify_products  
from agents.rearrange_data import run as rearrange_data
import time

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                 🎯 CrowdWisdom Trading AI Agent                ║
║                                                              ║
║  Multi-Agent Prediction Market Data Collection & Analysis    ║
║  Powered by CrewAI + Gemini 2.0 Flash + LiteLLM            ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if all required environment variables are set"""
    log_info("Checking system requirements...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        log_error("❌ GEMINI_API_KEY not found")
        return False
    elif api_key == 'your-actual-gemini-api-key-here':
        log_error("❌ GEMINI_API_KEY is still the placeholder")
        log_error("Please replace 'your-actual-gemini-api-key-here' with your real API key in main.py")
        return False
    elif len(api_key) < 30:
        log_error("❌ GEMINI_API_KEY appears to be invalid (too short)")
        return False
    
    log_success(f"✅ All requirements satisfied - API key: {api_key[:20]}...")
    return True

def create_outputs_directory():
    """Ensure outputs directory exists"""
    os.makedirs('outputs', exist_ok=True)
    log_success("📁 Outputs directory ready")

def print_pipeline_summary():
    """Print pipeline execution summary"""
    summary = """
🔄 PIPELINE EXECUTION PLAN:
   
   Step 1: 📊 Data Collection
   ├─ Scrape Polymarket prediction markets
   ├─ Scrape Kalshi trading contracts  
   ├─ Scrape Prediction-Market data
   ├─ Scrape Manifold Markets
   └─ Save raw data to JSON
   
   Step 2: 🔍 Product Identification  
   ├─ Load raw market data
   ├─ Apply AI-powered product matching
   ├─ Calculate similarity confidence scores
   ├─ Unify similar products across platforms
   └─ Save unified data structure
   
   Step 3: 📋 Data Arrangement
   ├─ Create comprehensive CSV output
   ├─ Generate simplified analysis format
   ├─ Calculate advanced market metrics
   ├─ Produce summary statistics
   └─ Export multiple report formats
    """
    print(summary)

def print_results_summary():
    """Print final results summary"""
    log_step("PIPELINE EXECUTION COMPLETED")
    
    output_files = [
        ("outputs/raw_data.json", "Raw scraped data with metadata"),
        ("outputs/unified_data.json", "AI-unified product groups"),
        ("outputs/final_products.csv", "Main analysis-ready CSV"),
        ("outputs/final_products_comprehensive.csv", "Detailed CSV with all metrics"),
        ("outputs/final_products_simple.csv", "Simplified comparison table"),
        ("outputs/analysis_reports.json", "Platform & category analysis"),
        ("outputs/summary_statistics.csv", "Summary statistics table"),
        ("outputs/app.log", "Complete execution logs")
    ]
    
    print("\n📁 OUTPUT FILES GENERATED:")
    print("=" * 70)
    
    for filename, description in output_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            size_str = f"{file_size:,} bytes"
            print(f"✅ {filename:<35} │ {description:<25} │ {size_str}")
        else:
            print(f"❌ {filename:<35} │ {description:<25} │ Missing")
    
    print("=" * 70)

def run_pipeline_step(step_name, step_function, step_number, total_steps):
    """Run a single pipeline step with error handling"""
    print(f"\n{'='*60}")
    print(f"🚀 STEP {step_number}/{total_steps}: {step_name.upper()}")
    print(f"{'='*60}")
    
    log_step(f"STEP {step_number}/{total_steps}: {step_name.upper()}")
    
    start_time = time.time()
    
    try:
        success = step_function()
        end_time = time.time()
        duration = end_time - start_time
        
        if success:
            log_success(f"Step {step_number} completed successfully in {duration:.2f} seconds")
            return True
        else:
            log_error(f"Step {step_number} failed after {duration:.2f} seconds")
            return False
    
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        log_error(f"Step {step_number} crashed after {duration:.2f} seconds: {str(e)}")
        return False

def run_chat_interface():
    """Launch the chat interface"""
    print("\n🤖 Launching CrowdWisdom Trading AI Chat Interface...")
    print("Choose your preferred interface:")
    print("1. Terminal Chat (Simple)")
    print("2. Web Interface (Streamlit)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        # Terminal chat
        try:
            from agents.rag_chat_agent import main as terminal_chat
            terminal_chat()
        except ImportError as e:
            log_error(f"❌ Could not import chat module: {e}")
            print("❌ Chat module not found. Please create agents/simple_rag_chat.py first.")
    elif choice == "2":
        # Web interface
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "streamlit", "run", "simple_chat_web.py"])
        except Exception as e:
            log_error(f"❌ Could not launch Streamlit: {e}")
            print("❌ Could not launch web interface. Make sure Streamlit is installed.")
    else:
        print("Invalid choice. Launching terminal chat...")
        try:
            from agents.rag_chat_agent import main as terminal_chat
            terminal_chat()
        except ImportError:
            print("❌ Chat module not available.")

def run_pipeline():
    """Run the data collection and analysis pipeline"""
    # Check requirements first
    if not check_requirements():
        print("\n❌ System requirements not met.")
        print("\n🔧 TO FIX:")
        print("1. Go to https://aistudio.google.com/")
        print("2. Sign in and create an API key")
        print("3. Copy your API key")
        print("4. Replace the API key in main.py with your real key")
        return False
    
    # Create outputs directory
    create_outputs_directory()
    
    # Print pipeline plan
    print_pipeline_summary()
    
    # Confirm execution
    try:
        user_input = input("\n🤔 Ready to start pipeline execution? (y/N): ").strip().lower()
        if user_input not in ['y', 'yes']:
            print("Pipeline execution cancelled by user.")
            return False
    except KeyboardInterrupt:
        print("\nPipeline execution cancelled by user.")
        return False
    
    print(f"\n🎯 Starting CrowdWisdom Trading AI Agent pipeline...")
    log_step("CROWDWISDOM TRADING AI AGENT PIPELINE START")
    
    pipeline_start_time = time.time()
    
    try:
        # Pipeline steps
        steps = [
            ("Data Collection", collect_data),
            ("Product Identification", identify_products),
            ("Data Arrangement", rearrange_data)
        ]
        
        # Execute each step
        for i, (step_name, step_function) in enumerate(steps, 1):
            success = run_pipeline_step(step_name, step_function, i, len(steps))
            
            if not success:
                log_error(f"Pipeline failed at step {i}: {step_name}")
                print(f"\n❌ Pipeline failed at Step {i}: {step_name}")
                print("Check the logs in outputs/app.log for detailed error information.")
                return False
        
        # Calculate total execution time
        pipeline_end_time = time.time()
        total_duration = pipeline_end_time - pipeline_start_time
        
        # Success message
        print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total execution time: {total_duration:.2f} seconds")
        
        # Print results summary
        print_results_summary()
        
        # Final instructions
        print(f"\n📋 NEXT STEPS:")
        print(f"   • Open outputs/final_products.csv in Excel or Google Sheets")
        print(f"   • Review outputs/analysis_reports.json for insights")
        print(f"   • Check outputs/app.log for detailed execution logs")
        print(f"   • Use the data for prediction market analysis and trading decisions")
        
        log_success("CROWDWISDOM TRADING AI AGENT PIPELINE COMPLETED SUCCESSFULLY")
        return True
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Pipeline interrupted by user")
        log_error("Pipeline interrupted by user (Ctrl+C)")
        return False
        
    except Exception as e:
        pipeline_end_time = time.time()
        total_duration = pipeline_end_time - pipeline_start_time
        
        print(f"\n❌ CRITICAL PIPELINE ERROR after {total_duration:.2f} seconds")
        print(f"Error: {str(e)}")
        log_error(f"Critical pipeline error: {str(e)}")
        
        print(f"\n🔍 TROUBLESHOOTING:")
        print(f"   • Check your internet connection")
        print(f"   • Verify your Gemini API key is valid")
        print(f"   • Review outputs/app.log for detailed error information")
        print(f"   • Ensure all required packages are installed")
        
        return False

def main():
    """Main orchestrator function with chat integration"""
    print_banner()
    
    # Present user with options
    print("\n🎯 CrowdWisdom Trading AI Options:")
    print("1. Run Data Pipeline (Collect & Analyze Markets)")
    print("2. Chat with AI about Markets (RAG)")
    print("3. Both (Pipeline then Chat)")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1, 2, 3, or 4): ").strip()
        
        if choice == "1":
            # Run pipeline only
            log_info("User selected: Pipeline only")
            run_pipeline()
            
        elif choice == "2":
            # Run chat only
            log_info("User selected: Chat only")
            # Check if we have data to chat about
            if not os.path.exists("outputs/unified_data.json"):
                print("\n⚠️  No prediction market data found!")
                print("💡 Tip: Run the pipeline first (option 1) to collect data for the chat.")
                print("\nWould you like to run the pipeline first?")
                run_first = input("Run pipeline first? (y/N): ").strip().lower()
                
                if run_first in ['y', 'yes']:
                    if run_pipeline():
                        print("\n🎉 Pipeline completed! Now launching chat interface...")
                        run_chat_interface()
                    else:
                        print("❌ Pipeline failed. Cannot launch chat without data.")
                else:
                    print("❌ Cannot launch chat without market data.")
            else:
                run_chat_interface()
                
        elif choice == "3":
            # Run pipeline then chat
            log_info("User selected: Pipeline then chat")
            if run_pipeline():
                print("\n🎉 Pipeline completed successfully!")
                print("🚀 Now launching chat interface...")
                run_chat_interface()
            else:
                print("❌ Pipeline failed. Skipping chat interface.")
                
        elif choice == "4":
            # Exit
            print("👋 Thank you for using CrowdWisdom Trading AI!")
            sys.exit(0)
            
        else:
            print("❌ Invalid choice. Please select 1, 2, 3, or 4.")
            main()  # Restart menu
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using CrowdWisdom Trading AI!")
        sys.exit(0)
    except Exception as e:
        log_error(f"Unexpected error in main menu: {str(e)}")
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
