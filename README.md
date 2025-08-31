# 🎯 CrowdWisdom Trading AI Agent

A multi-agent AI system that unifies prediction market data from multiple platforms and provides intelligent analysis through a RAG-powered chatbot.

## 🌟 Features

- **Multi-Platform Scraping**: Collect data from Polymarket, Kalshi, Prediction-Market, and Manifold
- **AI-Powered Unification**: Uses Gemini 2.0 Flash to identify and match similar products across platforms
- **Comprehensive CSV Output**: Generates analysis-ready datasets with confidence scores
- **RAG Chatbot**: Interactive chat interface for querying market data
- **Professional Logging**: Complete error handling and execution tracking
- **Arbitrage Detection**: Identify price differences across platforms

## 🏗️ Architecture

The system uses CrewAI framework with three specialized agents:

1. **Data Collector Agent** - Scrapes prediction market websites
2. **Product Identification Agent** - Uses AI to match similar products 
3. **Data Arrangement Agent** - Creates professional CSV outputs and analytics

## 📋 Prerequisites

- Python 3.9+
- Google Gemini API key
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
git clone https://github.com/SuyashVanjare/crowdwisdom-trading-ai.git
cd crowdwisdom-trading-ai

text

2. **Create virtual environment**
python -m venv venv
source venv/bin/activate # On macOS/Linux
venv\Scripts\activate # On Windows

text

3. **Install dependencies**
pip install -r requirements.txt

text

4. **Set up API key**

Get your API key from https://aistudio.google.com/

export GEMINI_API_KEY="your-api-key-here" # macOS/Linux
set GEMINI_API_KEY=your-api-key-here # Windows CMD
$env:GEMINI_API_KEY="your-api-key-here" # Windows PowerShell

text

## 💻 Usage

### Run the complete pipeline:
python main.py

text

### Options:
- **1** - Run data pipeline only
- **2** - Launch chat interface only  
- **3** - Run pipeline then chat
- **4** - Exit

### Sample Output:
📊 Products processed: 21
🔗 Platforms covered: 4
🏷️ Categories found: 10

text

## 📁 Project Structure

crowdwisdom-trading-ai/
├── main.py # Main orchestrator
├── agents/
│ ├── data_collector.py # Scraping agent
│ ├── identify_products.py # AI matching agent
│ ├── rearrange_data.py # CSV generation agent
│ └── rag_chat_agent.py # Chat interface
├── utils/
│ └── logger.py # Logging utilities
├── outputs/
│ ├── final_products.csv # Main results
│ ├── raw_data.json # Scraped data
│ └── unified_data.json # Processed data
├── requirements.txt # Dependencies
└── README.md # This file

text

## 📊 Sample Output Files

| File | Description | Size |
|------|-------------|------|
| `final_products.csv` | Main analysis-ready dataset | ~2KB |
| `final_products_comprehensive.csv` | Detailed metrics | ~5KB |
| `unified_data.json` | AI-processed market data | ~16KB |
| `analysis_reports.json` | Platform analytics | ~3KB |

## 🤖 Chat Interface

Ask questions like:
- "What Tesla prediction markets are available?"
- "Find arbitrage opportunities with >5% spreads"
- "Which platform has the highest volume?"
- "Show me markets with 90%+ confidence scores"

## 🔧 Configuration

Edit `main.py` to customize:
- API keys and models
- Scraping intervals
- Output formats
- Chat interface options

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

- **Email**: suyashvanjare23@gmail.com
- **LinkedIn**: [SuyashVanjare](https://www.linkedin.com/in/suyash-vanjare-7a97b0338/)
- **GitHub**: [@SuyashVanjare](https://github.com/SuyashVanjare)

---

⭐ If this project helped you, please give it a star!
