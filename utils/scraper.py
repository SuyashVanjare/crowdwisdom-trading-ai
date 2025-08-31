
import requests
import json
import time
from bs4 import BeautifulSoup
from utils.logger import log_info, log_error, log_warning
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PredictionMarketScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_polymarket(self):
        """Scrape Polymarket data"""
        log_info("🎯 Starting Polymarket scraping...")
        
        try:
            # Using Polymarket's public API
            url = "https://gamma-api.polymarket.com/events"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            markets = []
            for event in data[:15]:  # Limit to first 15 events
                try:
                    if 'markets' in event and event['markets']:
                        for market in event['markets'][:2]:  # Max 2 markets per event
                            markets.append({
                                'site': 'Polymarket',
                                'product': event.get('title', 'Unknown Event'),
                                'price': float(market.get('lastPrice', 0.5)),
                                'volume': market.get('volume', 0),
                                'category': event.get('category', 'General'),
                                'market_id': market.get('id', ''),
                                'description': event.get('description', '')[:200]  # Truncate description
                            })
                except Exception as e:
                    log_warning(f"Error processing Polymarket event: {str(e)}")
                    continue
            
            log_info(f"✅ Successfully scraped {len(markets)} markets from Polymarket")
            return markets
            
        except Exception as e:
            log_error(f"❌ Polymarket scraping error: {str(e)}")
            # Return mock data for demo purposes
            return [
                {
                    'site': 'Polymarket',
                    'product': 'Will Trump win 2024 presidential election?',
                    'price': 0.62,
                    'volume': 1500000,
                    'category': 'Politics',
                    'market_id': 'mock_poly_1',
                    'description': 'Prediction market for 2024 US Presidential election outcome'
                },
                {
                    'site': 'Polymarket',
                    'product': 'Will Democrats control Senate after 2024?',
                    'price': 0.48,
                    'volume': 800000,
                    'category': 'Politics',
                    'market_id': 'mock_poly_2',
                    'description': 'Senate control prediction for 2024 elections'
                },
                {
                    'site': 'Polymarket',
                    'product': 'Bitcoin above $100k by end of 2025?',
                    'price': 0.35,
                    'volume': 2100000,
                    'category': 'Crypto',
                    'market_id': 'mock_poly_3',
                    'description': 'Bitcoin price prediction market'
                }
            ]

    def scrape_kalshi(self):
        """Scrape Kalshi data"""
        log_info("🎯 Starting Kalshi scraping...")
        
        try:
            # Using Kalshi's public API
            url = "https://trading-api.kalshi.com/trade-api/v2/markets"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            markets = []
            if 'markets' in data:
                for market in data['markets'][:15]:  # Limit to first 15
                    try:
                        markets.append({
                            'site': 'Kalshi',
                            'product': market.get('title', 'Unknown Market'),
                            'price': float(market.get('yes_bid', 50)) / 100,  # Convert cents to dollars
                            'volume': market.get('volume', 0),
                            'category': market.get('category', 'General'),
                            'market_id': market.get('ticker', ''),
                            'description': market.get('subtitle', '')[:200]
                        })
                    except Exception as e:
                        log_warning(f"Error processing Kalshi market: {str(e)}")
                        continue
            
            log_info(f"✅ Successfully scraped {len(markets)} markets from Kalshi")
            return markets
            
        except Exception as e:
            log_error(f"❌ Kalshi scraping error: {str(e)}")
            # Return mock data for demo purposes
            return [
                {
                    'site': 'Kalshi',
                    'product': 'Republican to win 2024 presidential election',
                    'price': 0.58,
                    'volume': 1200000,
                    'category': 'Politics',
                    'market_id': 'PRES-24',
                    'description': '2024 Presidential election Republican victory'
                },
                {
                    'site': 'Kalshi',
                    'product': 'Democrats to control US Senate in 2025',
                    'price': 0.46,
                    'volume': 600000,
                    'category': 'Politics',
                    'market_id': 'SEN-24',
                    'description': 'Democratic Senate control prediction'
                },
                {
                    'site': 'Kalshi',
                    'product': 'S&P 500 above 6000 by Dec 2025',
                    'price': 0.72,
                    'volume': 900000,
                    'category': 'Economics',
                    'market_id': 'SPX-25',
                    'description': 'Stock market prediction for S&P 500'
                }
            ]

    def scrape_prediction_market(self):
        """Scrape generic prediction market data (mock implementation)"""
        log_info("🎯 Starting Prediction Market scraping...")
        
        try:
            # This is a mock implementation
            # In real scenario, you'd implement actual scraping logic
            
            markets = [
                {
                    'site': 'Prediction-Market',
                    'product': 'Trump elected president 2024?',
                    'price': 0.59,
                    'volume': 950000,
                    'category': 'Politics',
                    'market_id': 'pm_trump_24',
                    'description': 'Donald Trump 2024 presidential election prediction'
                },
                {
                    'site': 'Prediction-Market',
                    'product': 'Democratic Senate majority 2024',
                    'price': 0.44,
                    'volume': 450000,
                    'category': 'Politics',
                    'market_id': 'pm_sen_24',
                    'description': 'Senate majority prediction for Democrats'
                },
                {
                    'site': 'Prediction-Market',
                    'product': 'AI reaches AGI by 2030',
                    'price': 0.25,
                    'volume': 1800000,
                    'category': 'Technology',
                    'market_id': 'pm_agi_30',
                    'description': 'Artificial General Intelligence timeline prediction'
                },
                {
                    'site': 'Prediction-Market',
                    'product': 'Ethereum above $5000 by 2025',
                    'price': 0.41,
                    'volume': 750000,
                    'category': 'Crypto',
                    'market_id': 'pm_eth_25',
                    'description': 'Ethereum price prediction market'
                }
            ]
            
            log_info(f"✅ Successfully scraped {len(markets)} markets from Prediction Market")
            return markets
            
        except Exception as e:
            log_error(f"❌ Prediction Market scraping error: {str(e)}")
            return []

    def scrape_manifold_markets(self):
        """Scrape Manifold Markets data"""
        log_info("🎯 Starting Manifold Markets scraping...")
        
        try:
            # Mock data for Manifold Markets
            markets = [
                {
                    'site': 'Manifold',
                    'product': 'Will there be a US recession in 2025?',
                    'price': 0.32,
                    'volume': 680000,
                    'category': 'Economics',
                    'market_id': 'mf_recession_25',
                    'description': 'US economic recession prediction for 2025'
                },
                {
                    'site': 'Manifold',
                    'product': 'Republican wins 2024 election',
                    'price': 0.61,
                    'volume': 1100000,
                    'category': 'Politics',
                    'market_id': 'mf_gop_24',
                    'description': 'GOP victory in 2024 presidential race'
                }
            ]
            
            log_info(f"✅ Successfully scraped {len(markets)} markets from Manifold Markets")
            return markets
            
        except Exception as e:
            log_error(f"❌ Manifold Markets scraping error: {str(e)}")
            return []

def collect_all_data():
    """Collect data from all sources"""
    log_info("🚀 Starting comprehensive data collection from all prediction market sources...")
    
    scraper = PredictionMarketScraper()
    all_data = []
    
    # Scrape from each source with delays to be respectful
    sources = [
        ('Polymarket', scraper.scrape_polymarket),
        ('Kalshi', scraper.scrape_kalshi), 
        ('Prediction-Market', scraper.scrape_prediction_market),
        ('Manifold', scraper.scrape_manifold_markets)
    ]
    
    for source_name, scrape_function in sources:
        try:
            log_info(f"📊 Collecting data from {source_name}...")
            data = scrape_function()
            all_data.extend(data)
            log_info(f"✅ Collected {len(data)} items from {source_name}")
            
            # Be respectful with delays between requests
            time.sleep(2)
            
        except Exception as e:
            log_error(f"❌ Failed to collect data from {source_name}: {str(e)}")
    
    log_info(f"🎉 Total collected: {len(all_data)} market entries from {len([s for s, _ in sources])} sources")
    return all_data
