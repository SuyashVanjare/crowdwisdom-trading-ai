import json
import os
from crewai import Agent, Task, Crew
from crewai.flow import Flow, start, listen
from utils.scraper import collect_all_data
from utils.logger import log_info, log_error, log_success, log_step

class DataCollectorFlow(Flow):
    """CrewAI Flow for data collection"""
    
    def __init__(self):
        super().__init__()
        self.agent = Agent(
            role="Senior Data Collection Specialist",
            goal="Efficiently collect comprehensive prediction market data from multiple premium sources including Polymarket, Kalshi, and other leading platforms",
            backstory="""You are an elite data collection expert with deep expertise in prediction markets, 
            financial data scraping, and market analysis. You have years of experience gathering data from 
            platforms like Polymarket, Kalshi, Manifold Markets, and other prediction market sources. 
            You understand the nuances of each platform's data structure and can efficiently extract 
            high-quality, structured information.""",
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True
        )
    
    @start()
    def initiate_collection(self):
        """Start the data collection process"""
        log_step("INITIATING DATA COLLECTION FLOW")
        
        task = Task(
            description="""
            Execute comprehensive data collection from multiple prediction market platforms:
            
            1. Scrape Polymarket for trending prediction markets
            2. Collect data from Kalshi's active contracts  
            3. Gather information from other prediction market sources
            4. Ensure data quality and consistency across all sources
            5. Structure the collected data in a standardized JSON format
            
            Focus on markets related to:
            - Politics (elections, policy outcomes)
            - Economics (market predictions, inflation, GDP)
            - Technology (AI milestones, crypto prices)
            - Sports (major events, championships)
            - Entertainment (awards, box office)
            
            Each market entry should include:
            - Platform source
            - Market question/description
            - Current price/probability
            - Trading volume
            - Category classification
            - Market ID/identifier
            """,
            agent=self.agent,
            expected_output="A comprehensive JSON file containing structured prediction market data from all sources with proper categorization and metadata"
        )
        
        return self.execute_collection_task(task)
    
    def execute_collection_task(self, task):
        """Execute the actual data collection"""
        log_info("🎯 DataCollectorFlow: Beginning data collection execution...")
        
        try:
            # Ensure outputs directory exists
            os.makedirs('outputs', exist_ok=True)
            
            # Collect data from all sources
            log_info("📡 Connecting to prediction market data sources...")
            raw_data = collect_all_data()
            
            if not raw_data:
                log_error("❌ No data collected from any source")
                return {"success": False, "error": "No data collected"}
            
            # Add metadata to the dataset
            dataset_metadata = {
                "collection_timestamp": str(pd.Timestamp.now()),
                "total_markets": len(raw_data),
                "sources": list(set(item['site'] for item in raw_data)),
                "categories": list(set(item.get('category', 'General') for item in raw_data)),
                "data": raw_data
            }
            
            # Save raw data to JSON with metadata
            with open("outputs/raw_data.json", "w", encoding='utf-8') as f:
                json.dump(dataset_metadata, f, indent=2, ensure_ascii=False)
            
            log_success(f"Successfully collected and saved {len(raw_data)} market entries")
            log_info(f"📊 Data sources: {', '.join(dataset_metadata['sources'])}")
            log_info(f"🏷️  Categories found: {', '.join(dataset_metadata['categories'])}")
            
            return {
                "success": True, 
                "markets_collected": len(raw_data),
                "sources": dataset_metadata['sources'],
                "output_file": "outputs/raw_data.json"
            }
            
        except Exception as e:
            log_error(f"❌ DataCollectorFlow execution error: {str(e)}")
            return {"success": False, "error": str(e)}

class DataCollectorAgent:
    """Legacy wrapper for backwards compatibility"""
    
    def __init__(self):
        self.flow = DataCollectorFlow()
    
    def execute_collection(self):
        """Execute the data collection process"""
        result = self.flow.initiate_collection()
        return result.get("success", False)

def run():
    """Main function to run the data collector"""
    log_step("DATA COLLECTION PHASE")
    
    try:
        # Use the new Flow-based approach
        flow = DataCollectorFlow()
        result = flow.initiate_collection()
        
        if result.get("success"):
            log_success("Data collection completed successfully")
            log_info(f"📈 Markets collected: {result.get('markets_collected', 0)}")
            log_info(f"🔗 Sources: {', '.join(result.get('sources', []))}")
            return True
        else:
            log_error("Data collection failed")
            log_error(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        log_error(f"❌ Critical error in data collection: {str(e)}")
        return False

# Import pandas for timestamp
import pandas as pd
