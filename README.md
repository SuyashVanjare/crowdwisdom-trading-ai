🎯 CrowdWisdom Trading AI Agent

A multi-agent AI system that unifies prediction market data from multiple platforms and provides intelligent analysis through a RAG-powered chatbot.

🌟 Features

Multi-Platform Scraping: Collect data from Polymarket, Kalshi, Prediction-Market, and Manifold

AI-Powered Unification: Uses Gemini 2.0 Flash to identify and match similar products across platforms

Comprehensive CSV Output: Generates analysis-ready datasets with confidence scores

RAG Chatbot: Interactive chat interface for querying market data

Professional Logging: Complete error handling and execution tracking

Arbitrage Detection: Identify price differences across platforms

🏗️ Architecture

This project is built using the CrewAI framework with three specialized agents:

Data Collector Agent → Scrapes prediction market websites

Product Identification Agent → Uses AI to match similar products

Data Arrangement Agent → Creates CSV outputs and analytics

📋 Prerequisites

Python 3.9+

Google Gemini API key

Virtual environment (recommended)

🚀 Installation

Clone the repository:

git clone https://github.com/SuyashVanjare/crowdwisdom-trading-ai.git
cd crowdwisdom-trading-ai


Create a virtual environment:

python -m venv venv
# macOS/Linux
source venv/bin/activate  
# Windows
venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Set up API key:

# macOS/Linux
export GEMINI_API_KEY="your-api-key-here"  

# Windows CMD
set GEMINI_API_KEY=your-api-key-here       

# Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"    

💻 Usage

Run the complete pipeline:

python main.py

Options:
1 - Run data pipeline only  
2 - Launch chat interface only  
3 - Run pipeline then chat  
4 - Exit  

📁 Project Structure
crowdwisdom-trading-ai/
├── agents/
│   ├── data_collector.py      # Scraping agent
│   ├── identify_products.py   # AI matching agent
│   ├── rearrange_data.py      # CSV generation agent
│   └── rag_chat_agent.py      # Chat interface
├── utils/
│   └── logger.py              # Logging utilities
├── outputs/
│   ├── final_products.csv     # Main results
│   ├── raw_data.json          # Scraped data
│   └── unified_data.json      # Processed data
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
└── README.md                  # Documentation

📊 Sample Output Files
File	Description	Purpose
final_products.csv	Main analysis-ready dataset	Trading analysis
unified_data.json	AI-processed market data	Data pipeline
analysis_reports.json	Platform analytics	Market insights
🤖 Chat Interface

You can ask:

"What Tesla prediction markets are available?"

"Find arbitrage opportunities with >5% spreads"

"Which platform has the highest volume?"

"Show me markets with 90%+ confidence scores"

🤝 Contributing

Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License

This project is licensed under the MIT License – see the LICENSE
 file for details.

📧 Contact

Email: suyashvanjare23@gmail.com

GitHub: @SuyashVanjare

⭐ If this project helped you, please give it a star!
