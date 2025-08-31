
import json
import os
from dotenv import load_dotenv
import litellm
from crewai import Agent, Task, Crew
from crewai.flow import Flow, start, listen
from utils.logger import log_info, log_error, log_warning, log_success, log_step
import re
import difflib
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class ProductIdentifierFlow(Flow):
    """CrewAI Flow for product identification and unification"""
    
    def __init__(self):
        super().__init__()
        self.agent = Agent(
            role="Senior Market Intelligence Analyst",
            goal="Expertly identify, analyze, and unify similar prediction market products across multiple platforms using advanced NLP and market knowledge",
            backstory="""You are a world-class market intelligence analyst with a PhD in Economics and 
            expertise in prediction markets, natural language processing, and financial market analysis. 
            You have spent years studying how different platforms phrase similar market questions and 
            can identify semantic equivalence even when the wording varies significantly. 
            
            Your expertise includes:
            - Deep understanding of prediction market terminology
            - Advanced pattern recognition for market questions
            - Statistical confidence modeling
            - Cross-platform market analysis
            - Semantic similarity detection""",
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            memory=True
        )
        
        # Configure LiteLLM for Gemini
        if GEMINI_API_KEY:
            os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    
    @start()
    def initiate_identification(self):
        """Start the product identification process"""
        log_step("INITIATING PRODUCT IDENTIFICATION FLOW")
        
        task = Task(
            description="""
            Perform sophisticated analysis and unification of prediction market products:
            
            1. Load and analyze raw prediction market data from multiple sources
            2. Apply advanced NLP techniques to identify semantically similar markets
            3. Use both rule-based and AI-powered matching algorithms
            4. Calculate confidence scores for each product unification
            5. Handle edge cases and ambiguous matches intelligently
            6. Create unified product groups with standardized naming
            
            Matching Criteria:
            - Semantic similarity (AI-powered analysis)
            - Keyword overlap and synonyms
            - Temporal alignment (same time periods)
            - Market type consistency
            - Category matching
            
            Output Requirements:
            - High confidence matches (>0.8) should be automatically unified
            - Medium confidence matches (0.6-0.8) should be flagged for review
            - Low confidence matches (<0.6) should remain separate
            - Each unified group needs a confidence score
            - Preserve all original market metadata
            """,
            agent=self.agent,
            expected_output="A sophisticated JSON structure with unified product groups, confidence scores, and detailed matching metadata"
        )
        
        return self.execute_identification_task(task)
    
    def normalize_product_name(self, product_name: str) -> str:
        """Advanced normalization of product names"""
        if not product_name:
            return ""
            
        # Convert to lowercase
        normalized = product_name.lower().strip()
        
        # Remove special characters but keep important ones
        normalized = re.sub(r'[^\w\s\-\?\!]', ' ', normalized)
        
        # Standardize common terms and synonyms
        replacements = {
            # Political terms
            'trump': 'donald trump',
            'biden': 'joe biden', 
            'harris': 'kamala harris',
            'democrats': 'democratic party',
            'republicans': 'republican party',
            'gop': 'republican party',
            'dems': 'democratic party',
            
            # Government terms
            'senate': 'us senate',
            'house': 'us house',
            'congress': 'us congress',
            'presidency': 'president',
            'presidential': 'president',
            
            # Time terms
            '2024': '2024 election',
            '2025': '2025',
            'next': 'upcoming',
            
            # Action terms
            'win': 'victory',
            'wins': 'victory',
            'elected': 'victory',
            'control': 'majority',
            'controls': 'majority',
            
            # Market terms
            'above': 'over',
            'below': 'under',
            'reaches': 'hits',
            'exceeds': 'over'
        }
        
        for old, new in replacements.items():
            normalized = re.sub(r'\b' + re.escape(old) + r'\b', new, normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text"""
        # Normalize first
        normalized = self.normalize_product_name(text)
        
        # Split into words
        words = normalized.split()
        
        # Remove common stop words but keep important market terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'will', 'be', 'is', 'are', 'was', 'were'}
        
        keywords = set()
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.add(word)
        
        return keywords
    
    def calculate_similarity_llm(self, product1: str, product2: str) -> Dict:
        """Calculate similarity using Gemini LLM"""
        try:
            if not GEMINI_API_KEY:
                return self.calculate_similarity_rule_based(product1, product2)
            
            prompt = f"""
            You are an expert prediction market analyst. Compare these two prediction market questions and determine if they refer to the same underlying event.
            
            Question 1: "{product1}"
            Question 2: "{product2}"
            
            Consider:
            - Semantic meaning and intent
            - Time periods mentioned
            - Specific entities (people, organizations)
            - Market outcomes being predicted
            - Logical equivalence even with different wording
            
            Respond with valid JSON only:
            {{
                "same_event": true/false,
                "confidence": 0.0-1.0,
                "unified_name": "standardized event name",
                "reasoning": "brief explanation"
            }}
            
            Examples of same events:
            - "Trump wins 2024" and "Republican victory 2024 presidential election" = same (if Trump is nominee)
            - "Bitcoin above $100k" and "BTC over $100,000" = same
            - "Democrats control Senate" and "Democratic Senate majority" = same
            """
            
            response = litellm.completion(
                model="gemini/gemini-2.0-flash-exp",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                log_warning("Could not parse LLM JSON response, falling back to rule-based")
                return self.calculate_similarity_rule_based(product1, product2)
            
        except Exception as e:
            log_warning(f"LLM similarity calculation failed: {str(e)}, using rule-based fallback")
            return self.calculate_similarity_rule_based(product1, product2)
    
    def calculate_similarity_rule_based(self, product1: str, product2: str) -> Dict:
        """Rule-based similarity calculation"""
        # Extract keywords
        keywords1 = self.extract_keywords(product1)
        keywords2 = self.extract_keywords(product2)
        
        # Calculate Jaccard similarity
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # Calculate sequence similarity using difflib
        sequence_similarity = difflib.SequenceMatcher(None, product1.lower(), product2.lower()).ratio()
        
        # Combined similarity score
        combined_similarity = (jaccard_similarity * 0.7 + sequence_similarity * 0.3)
        
        # Determine if same event
        same_event = combined_similarity > 0.65
        
        # Create unified name
        unified_name = product1 if len(product1) <= len(product2) else product2
        
        return {
            "same_event": same_event,
            "confidence": round(combined_similarity, 3),
            "unified_name": unified_name,
            "reasoning": f"Rule-based matching: {round(jaccard_similarity, 2)} keyword + {round(sequence_similarity, 2)} sequence similarity"
        }
    
    def match_products(self, raw_data: List[Dict]) -> Dict:
        """Advanced product matching and unification"""
        log_info("🔍 Starting advanced product matching algorithm...")
        
        if not raw_data:
            return {}
        
        unified_products = {}
        processed_indices = set()
        match_count = 0
        
        for i, entry1 in enumerate(raw_data):
            if i in processed_indices:
                continue
            
            current_group = {
                'unified_name': entry1['product'],
                'products': [entry1],
                'confidence': 1.0,
                'match_reasoning': 'Primary product'
            }
            
            # Compare with remaining entries
            for j, entry2 in enumerate(raw_data[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                # Calculate similarity
                similarity_result = self.calculate_similarity_llm(
                    entry1['product'], 
                    entry2['product']
                )
                
                # Match if confidence is high enough
                if similarity_result['same_event'] and similarity_result['confidence'] > 0.65:
                    current_group['products'].append(entry2)
                    current_group['unified_name'] = similarity_result['unified_name']
                    current_group['confidence'] = min(current_group['confidence'], similarity_result['confidence'])
                    current_group['match_reasoning'] = similarity_result.get('reasoning', 'AI-powered matching')
                    processed_indices.add(j)
                    match_count += 1
                    
                    log_info(f"✅ Match found: '{entry1['product'][:50]}...' ↔ '{entry2['product'][:50]}...' (confidence: {similarity_result['confidence']})")
            
            processed_indices.add(i)
            
            # Create unified entry with all platform data
            unified_entry = {
                'confidence': round(current_group['confidence'], 3),
                'match_reasoning': current_group['match_reasoning'],
                'product_count': len(current_group['products']),
                'platforms': {}
            }
            
            # Aggregate data from all matched products
            for product in current_group['products']:
                site = product['site']
                if site not in unified_entry['platforms']:
                    unified_entry['platforms'][site] = []
                
                unified_entry['platforms'][site].append({
                    'original_product': product['product'],
                    'price': product['price'],
                    'volume': product.get('volume', 0),
                    'category': product.get('category', 'General'),
                    'market_id': product.get('market_id', ''),
                    'description': product.get('description', '')
                })
            
            unified_products[current_group['unified_name']] = unified_entry
        
        log_success(f"Product matching completed: {len(raw_data)} → {len(unified_products)} unified products")
        log_info(f"🔗 Total matches found: {match_count}")
        return unified_products
    
    def execute_identification_task(self, task):
        """Execute the product identification process"""
        log_info("🧠 ProductIdentifierFlow: Starting product identification...")
        
        try:
            # Read raw data
            if not os.path.exists("outputs/raw_data.json"):
                log_error("❌ Raw data file not found. Run data collection first.")
                return {"success": False, "error": "Raw data file missing"}
            
            with open("outputs/raw_data.json", "r", encoding='utf-8') as f:
                data_with_metadata = json.load(f)
            
            # Extract raw data from metadata structure
            if 'data' in data_with_metadata:
                raw_data = data_with_metadata['data']
                metadata = {k: v for k, v in data_with_metadata.items() if k != 'data'}
            else:
                raw_data = data_with_metadata
                metadata = {}
            
            if not raw_data:
                log_error("❌ No raw data to process")
                return {"success": False, "error": "No data to process"}
            
            log_info(f"📊 Processing {len(raw_data)} market entries...")
            
            # Match and unify products
            unified_data = self.match_products(raw_data)
            
            # Add processing metadata
            processing_metadata = {
                "processing_timestamp": str(pd.Timestamp.now()),
                "original_markets": len(raw_data),
                "unified_groups": len(unified_data),
                "compression_ratio": round(len(unified_data) / len(raw_data), 3) if raw_data else 0,
                "high_confidence_matches": len([p for p in unified_data.values() if p['confidence'] > 0.8]),
                "original_metadata": metadata,
                "unified_products": unified_data
            }
            
            # Save unified data with metadata
            with open("outputs/unified_data.json", "w", encoding='utf-8') as f:
                json.dump(processing_metadata, f, indent=2, ensure_ascii=False)
            
            log_success(f"Product unification completed: {len(raw_data)} → {len(unified_data)} groups")
            log_info(f"📈 Compression ratio: {processing_metadata['compression_ratio']}")
            log_info(f"🎯 High confidence matches: {processing_metadata['high_confidence_matches']}")
            
            return {
                "success": True,
                "unified_groups": len(unified_data),
                "compression_ratio": processing_metadata['compression_ratio'],
                "output_file": "outputs/unified_data.json"
            }
            
        except Exception as e:
            log_error(f"❌ ProductIdentifierFlow execution error: {str(e)}")
            return {"success": False, "error": str(e)}

def run():
    """Main function to run the product identifier"""
    log_step("PRODUCT IDENTIFICATION PHASE")
    
    try:
        # Use the new Flow-based approach
        flow = ProductIdentifierFlow()
        result = flow.initiate_identification()
        
        if result.get("success"):
            log_success("Product identification completed successfully")
            log_info(f"📊 Unified groups: {result.get('unified_groups', 0)}")
            log_info(f"📉 Compression ratio: {result.get('compression_ratio', 0)}")
            return True
        else:
            log_error("Product identification failed")
            log_error(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        log_error(f"❌ Critical error in product identification: {str(e)}")
        return False

# Import pandas for timestamp
import pandas as pd
