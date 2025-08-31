import json
import csv
import os
from crewai import Agent, Task, Crew
from crewai.flow import Flow, start, listen
from utils.logger import log_info, log_error, log_success, log_step
import pandas as pd
from typing import Dict, List, Any

class DataArrangerFlow(Flow):
    """CrewAI Flow for data arrangement and CSV generation"""
    
    def __init__(self):
        super().__init__()
        self.agent = Agent(
            role="Senior Data Architecture Specialist",
            goal="Transform unified prediction market data into professional, analysis-ready CSV formats with comprehensive metrics and insights",
            backstory="""You are an elite data architecture specialist with extensive experience in 
            financial data processing, business intelligence, and data visualization preparation. 
            You excel at creating clean, professional datasets that are perfect for analysis, 
            reporting, and decision-making.
            
            Your expertise includes:
            - Advanced data structuring and normalization
            - Financial metrics calculation and analysis
            - Multi-platform data reconciliation
            - Professional report generation
            - Data quality assurance and validation""",
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True
        )
    
    @start()
    def initiate_arrangement(self):
        """Start the data arrangement process"""
        log_step("INITIATING DATA ARRANGEMENT FLOW")
        
        task = Task(
            description="""
            Create comprehensive, professional CSV outputs from unified prediction market data:
            
            1. Load and validate unified prediction market data
            2. Design optimal CSV structure for analysis and reporting
            3. Calculate advanced metrics and insights
            4. Handle missing data and edge cases gracefully
            5. Generate multiple CSV formats for different use cases
            6. Create summary statistics and metadata reports
            
            Required Outputs:
            - Main comprehensive CSV with all data points
            - Simplified CSV for quick analysis
            - Price comparison matrix
            - Volume analysis report
            - Platform coverage statistics
            - Market category breakdown
            
            Data Quality Requirements:
            - Consistent formatting across all platforms
            - Proper handling of missing values
            - Accurate price and volume calculations
            - Clear confidence scoring
            - Professional naming conventions
            """,
            agent=self.agent,
            expected_output="Multiple professional CSV files and comprehensive data analysis reports ready for business use"
        )
        
        return self.execute_arrangement_task(task)
    
    def calculate_advanced_metrics(self, platforms_data: Dict) -> Dict:
        """Calculate advanced metrics from platform data"""
        metrics = {
            'price_stats': {},
            'volume_stats': {},
            'platform_coverage': {},
            'best_opportunities': {}
        }
        
        # Extract prices and volumes
        prices = []
        volumes = []
        platform_prices = {}
        
        for platform, data_list in platforms_data.items():
            if isinstance(data_list, list) and data_list:
                # Take the first entry if multiple markets from same platform
                data = data_list[0]
                
                # FIXED: Convert price to float with proper error handling
                try:
                    price = float(data.get('price', 0))
                except (ValueError, TypeError):
                    price = 0.0
                
                # FIXED: Convert volume to float with proper error handling
                try:
                    volume = float(data.get('volume', 0))
                except (ValueError, TypeError):
                    volume = 0.0
                
                if price > 0:
                    prices.append(price)
                    platform_prices[platform] = price
                if volume > 0:
                    volumes.append(volume)
        
        # Price statistics
        if prices:
            metrics['price_stats'] = {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': sum(prices) / len(prices),
                'price_spread': max(prices) - min(prices) if len(prices) > 1 else 0,
                'price_variance': sum((p - sum(prices)/len(prices))**2 for p in prices) / len(prices)
            }
            
            # Find best price (highest probability)
            if platform_prices:
                best_platform = max(platform_prices, key=platform_prices.get)
                metrics['best_opportunities'] = {
                    'highest_probability_platform': best_platform,
                    'highest_probability_price': platform_prices[best_platform],
                    'arbitrage_opportunity': max(prices) - min(prices) > 0.05
                }
        
        # Volume statistics
        if volumes:
            metrics['volume_stats'] = {
                'total_volume': sum(volumes),
                'avg_volume': sum(volumes) / len(volumes),
                'max_volume': max(volumes)
            }
        
        # Platform coverage
        metrics['platform_coverage'] = {
            'platforms_count': len(platforms_data),
            'platforms_list': list(platforms_data.keys())
        }
        
        return metrics
    
    def create_comprehensive_csv(self, unified_data: Dict) -> List[Dict]:
        """Create comprehensive CSV data structure"""
        log_info("📊 Creating comprehensive CSV structure...")
        
        csv_data = []
        
        for product_name, product_data in unified_data.items():
            platforms = product_data.get('platforms', {})
            confidence = product_data.get('confidence', 0.0)
            
            # Calculate advanced metrics
            metrics = self.calculate_advanced_metrics(platforms)
            
            # Initialize row with base information
            row = {
                'Product_Name': product_name,
                'Confidence_Score': confidence,
                'Product_Count': product_data.get('product_count', 1),
                'Match_Reasoning': product_data.get('match_reasoning', ''),
                
                # Platform prices (initialize as empty)
                'Polymarket_Price': None,
                'Kalshi_Price': None,
                'Prediction_Market_Price': None,
                'Manifold_Price': None,
                
                # Platform volumes
                'Polymarket_Volume': None,
                'Kalshi_Volume': None,
                'Prediction_Market_Volume': None,
                'Manifold_Volume': None,
                
                # Categories
                'Primary_Category': 'General',
                
                # Advanced metrics
                'Min_Price': metrics['price_stats'].get('min_price'),
                'Max_Price': metrics['price_stats'].get('max_price'),
                'Avg_Price': metrics['price_stats'].get('avg_price'),
                'Price_Spread': metrics['price_stats'].get('price_spread'),
                'Price_Variance': metrics['price_stats'].get('price_variance'),
                
                'Total_Volume': metrics['volume_stats'].get('total_volume', 0),
                'Avg_Volume': metrics['volume_stats'].get('avg_volume'),
                'Max_Volume': metrics['volume_stats'].get('max_volume'),
                
                'Platform_Count': metrics['platform_coverage']['platforms_count'],
                'Available_Platforms': ', '.join(metrics['platform_coverage']['platforms_list']),
                
                'Best_Price_Platform': metrics['best_opportunities'].get('highest_probability_platform'),
                'Best_Price_Value': metrics['best_opportunities'].get('highest_probability_price'),
                'Arbitrage_Opportunity': metrics['best_opportunities'].get('arbitrage_opportunity', False),
                
                # Market IDs for reference
                'Market_IDs': ''
            }
            
            # Fill in platform-specific data
            market_ids = []
            categories = set()
            
            for platform, data_list in platforms.items():
                if isinstance(data_list, list) and data_list:
                    # Use first entry if multiple
                    data = data_list[0]
                    
                    # FIXED: Convert price and volume to proper types
                    try:
                        price = float(data.get('price', 0)) if data.get('price') is not None else None
                    except (ValueError, TypeError):
                        price = None
                    
                    try:
                        volume = float(data.get('volume', 0)) if data.get('volume') is not None else None
                    except (ValueError, TypeError):
                        volume = None
                    
                    category = data.get('category', 'General')
                    market_id = data.get('market_id', '')
                    
                    categories.add(category)
                    if market_id:
                        market_ids.append(f"{platform}:{market_id}")
                    
                    # Map to appropriate columns
                    if platform == 'Polymarket':
                        row['Polymarket_Price'] = price
                        row['Polymarket_Volume'] = volume
                    elif platform == 'Kalshi':
                        row['Kalshi_Price'] = price
                        row['Kalshi_Volume'] = volume
                    elif platform == 'Prediction-Market':
                        row['Prediction_Market_Price'] = price
                        row['Prediction_Market_Volume'] = volume
                    elif platform == 'Manifold':
                        row['Manifold_Price'] = price
                        row['Manifold_Volume'] = volume
            
            # Set primary category and market IDs
            row['Primary_Category'] = list(categories)[0] if categories else 'General'
            row['Market_IDs'] = ' | '.join(market_ids)
            
            csv_data.append(row)
        
        return csv_data
    
    def create_simplified_csv(self, csv_data: List[Dict]) -> List[Dict]:
        """Create simplified CSV for quick analysis"""
        log_info("📋 Creating simplified CSV structure...")
        
        simplified_data = []
        
        for row in csv_data:
            simple_row = {
                'Product': row['Product_Name'],
                'Polymarket': row['Polymarket_Price'] if row['Polymarket_Price'] is not None else '-',
                'Kalshi': row['Kalshi_Price'] if row['Kalshi_Price'] is not None else '-',
                'Prediction_Market': row['Prediction_Market_Price'] if row['Prediction_Market_Price'] is not None else '-',
                'Manifold': row['Manifold_Price'] if row['Manifold_Price'] is not None else '-',
                'Best_Price': row['Best_Price_Value'] if row['Best_Price_Value'] is not None else '-',
                'Price_Spread': row['Price_Spread'] if row['Price_Spread'] is not None else '-',
                'Confidence': row['Confidence_Score'],
                'Category': row['Primary_Category'],
                'Platforms': row['Platform_Count']
            }
            simplified_data.append(simple_row)
        
        return simplified_data
    
    def create_analysis_reports(self, csv_data: List[Dict]) -> Dict:
        """Create comprehensive analysis reports"""
        log_info("📈 Generating analysis reports...")
        
        reports = {}
        
        # Platform coverage analysis
        platform_stats = {
            'Polymarket': {'count': 0, 'total_volume': 0},
            'Kalshi': {'count': 0, 'total_volume': 0},
            'Prediction_Market': {'count': 0, 'total_volume': 0},
            'Manifold': {'count': 0, 'total_volume': 0}
        }
        
        # Category analysis
        category_stats = {}
        
        # Confidence analysis
        confidence_ranges = {
            'High (0.8-1.0)': 0,
            'Medium (0.6-0.8)': 0,
            'Low (0.0-0.6)': 0
        }
        
        for row in csv_data:
            # Platform coverage
            for platform in platform_stats:
                price = row.get(f'{platform}_Price')
                volume = row.get(f'{platform}_Volume')
                
                if price is not None:
                    platform_stats[platform]['count'] += 1
                
                # FIXED: Convert volume to float before adding
                if volume is not None:
                    try:
                        volume_float = float(volume)
                        platform_stats[platform]['total_volume'] += volume_float
                    except (ValueError, TypeError):
                        pass  # Skip invalid volumes
            
            # Category analysis
            category = row['Primary_Category']
            category_stats[category] = category_stats.get(category, 0) + 1
            
            # Confidence analysis
            confidence = row['Confidence_Score']
            if confidence >= 0.8:
                confidence_ranges['High (0.8-1.0)'] += 1
            elif confidence >= 0.6:
                confidence_ranges['Medium (0.6-0.8)'] += 1
            else:
                confidence_ranges['Low (0.0-0.6)'] += 1
        
        reports['platform_coverage'] = platform_stats
        reports['category_breakdown'] = category_stats
        reports['confidence_distribution'] = confidence_ranges
        reports['total_products'] = len(csv_data)
        
        return reports
    
    def save_all_outputs(self, csv_data: List[Dict], simplified_data: List[Dict], reports: Dict) -> bool:
        """Save all CSV files and reports"""
        try:
            # Convert to DataFrames for better formatting
            df_comprehensive = pd.DataFrame(csv_data)
            df_simplified = pd.DataFrame(simplified_data)
            
            # Sort by confidence and total volume
            df_comprehensive = df_comprehensive.sort_values(
                ['Confidence_Score', 'Total_Volume'], 
                ascending=[False, False]
            )
            
            df_simplified = df_simplified.sort_values(
                ['Confidence'], 
                ascending=[False]
            )
            
            # Save comprehensive CSV
            df_comprehensive.to_csv('outputs/final_products_comprehensive.csv', index=False)
            log_success("✅ Saved comprehensive CSV: outputs/final_products_comprehensive.csv")
            
            # Save simplified CSV
            df_simplified.to_csv('outputs/final_products_simple.csv', index=False)
            log_success("✅ Saved simplified CSV: outputs/final_products_simple.csv")
            
            # Save main CSV (alias for simplified)
            df_simplified.to_csv('outputs/final_products.csv', index=False)
            log_success("✅ Saved main CSV: outputs/final_products.csv")
            
            # Save analysis reports
            with open('outputs/analysis_reports.json', 'w', encoding='utf-8') as f:
                json.dump(reports, f, indent=2, ensure_ascii=False)
            log_success("✅ Saved analysis reports: outputs/analysis_reports.json")
            
            # Create summary statistics CSV
            summary_data = []
            for metric, value in reports.items():
                if isinstance(value, dict):
                    for sub_metric, sub_value in value.items():
                        summary_data.append({
                            'Metric_Category': metric,
                            'Metric_Name': sub_metric,
                            'Value': sub_value
                        })
                else:
                    summary_data.append({
                        'Metric_Category': 'General',
                        'Metric_Name': metric,
                        'Value': value
                    })
            
            pd.DataFrame(summary_data).to_csv('outputs/summary_statistics.csv', index=False)
            log_success("✅ Saved summary statistics: outputs/summary_statistics.csv")
            
            return True
            
        except Exception as e:
            log_error(f"❌ Error saving outputs: {str(e)}")
            return False
    
    def execute_arrangement_task(self, task):
        """Execute the data arrangement process"""
        log_info("📊 DataArrangerFlow: Starting data arrangement...")
        
        try:
            # Read unified data
            if not os.path.exists("outputs/unified_data.json"):
                log_error("❌ Unified data file not found. Run product identification first.")
                return {"success": False, "error": "Unified data file missing"}
            
            with open("outputs/unified_data.json", "r", encoding='utf-8') as f:
                data_with_metadata = json.load(f)
            
            # Extract unified data
            if 'unified_products' in data_with_metadata:
                unified_data = data_with_metadata['unified_products']
                metadata = {k: v for k, v in data_with_metadata.items() if k != 'unified_products'}
            else:
                unified_data = data_with_metadata
                metadata = {}
            
            if not unified_data:
                log_error("❌ No unified data to process")
                return {"success": False, "error": "No data to process"}
            
            log_info(f"📊 Processing {len(unified_data)} unified product groups...")
            
            # Create comprehensive CSV structure
            csv_data = self.create_comprehensive_csv(unified_data)
            
            # Create simplified CSV
            simplified_data = self.create_simplified_csv(csv_data)
            
            # Generate analysis reports
            reports = self.create_analysis_reports(csv_data)
            
            # Add metadata to reports
            reports['processing_metadata'] = metadata
            reports['generation_timestamp'] = str(pd.Timestamp.now())
            
            # Save all outputs
            save_success = self.save_all_outputs(csv_data, simplified_data, reports)
            
            if save_success:
                log_success(f"Data arrangement completed: {len(csv_data)} products processed")
                log_info(f"📊 Platform coverage: {reports['platform_coverage']}")
                log_info(f"🏷️  Categories: {list(reports['category_breakdown'].keys())}")
                
                return {
                    "success": True,
                    "products_processed": len(csv_data),
                    "platforms": len([p for p in reports['platform_coverage'] if reports['platform_coverage'][p]['count'] > 0]),
                    "categories": len(reports['category_breakdown']),
                    "output_files": [
                        "outputs/final_products.csv",
                        "outputs/final_products_comprehensive.csv", 
                        "outputs/final_products_simple.csv",
                        "outputs/analysis_reports.json",
                        "outputs/summary_statistics.csv"
                    ]
                }
            else:
                return {"success": False, "error": "Failed to save outputs"}
            
        except Exception as e:
            log_error(f"❌ DataArrangerFlow execution error: {str(e)}")
            return {"success": False, "error": str(e)}

def run():
    """Main function to run the data arranger"""
    log_step("DATA ARRANGEMENT PHASE")
    
    try:
        # Use the new Flow-based approach
        flow = DataArrangerFlow()
        result = flow.initiate_arrangement()
        
        if result.get("success"):
            log_success("Data arrangement completed successfully")
            log_info(f"📊 Products processed: {result.get('products_processed', 0)}")
            log_info(f"🔗 Platforms covered: {result.get('platforms', 0)}")
            log_info(f"🏷️  Categories found: {result.get('categories', 0)}")
            log_info("📁 Output files:")
            for file in result.get('output_files', []):
                log_info(f"   - {file}")
            return True
        else:
            log_error("Data arrangement failed")
            log_error(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        log_error(f"❌ Critical error in data arrangement: {str(e)}")
        return False
