import json
import os
from typing import List, Dict
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from utils.logger import log_info, log_success, log_error


class PredictionMarketKnowledgeBase:
    """Create a knowledge base from your prediction market data"""
    
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def clean_metadata(self, metadata):
        """Clean metadata to only include simple types that ChromaDB supports"""
        cleaned = {}
        for key, value in metadata.items():
            if isinstance(value, list):
                # Convert lists to comma-separated strings
                cleaned[key] = ', '.join(str(item) for item in value)
            elif isinstance(value, dict):
                # Convert dicts to JSON strings
                cleaned[key] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)) or value is None:
                # Keep simple types as-is
                cleaned[key] = value
            else:
                # Convert everything else to string
                cleaned[key] = str(value)
        return cleaned
        
    def load_market_data(self) -> List[Document]:
        """Load and convert your market data to documents"""
        documents = []
        
        # Load your generated files
        data_files = [
            ("outputs/unified_data.json", "unified_markets"),
            ("outputs/raw_data.json", "raw_markets"),
            ("outputs/analysis_reports.json", "analysis")
        ]
        
        for file_path, doc_type in data_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if doc_type == "unified_markets":
                        documents.extend(self._create_unified_market_docs(data))
                    elif doc_type == "raw_markets":
                        documents.extend(self._create_raw_market_docs(data))
                    elif doc_type == "analysis":
                        documents.extend(self._create_analysis_docs(data))
                        
                    log_info(f"📄 Loaded {file_path} for knowledge base")
                except Exception as e:
                    log_error(f"❌ Failed to load {file_path}: {e}")
        
        return documents
    
    def _create_unified_market_docs(self, data: Dict) -> List[Document]:
        """Convert unified market data to documents"""
        documents = []
        
        unified_products = data.get('unified_products', data)
        
        for product_name, product_data in unified_products.items():
            platforms = product_data.get('platforms', {})
            confidence = product_data.get('confidence', 0)
            
            # Create comprehensive text about this market
            content = f"""Product: {product_name}
Confidence Score: {confidence}
Available Platforms: {', '.join(platforms.keys())}

Platform Details:
"""
            for platform, markets in platforms.items():
                if isinstance(markets, list) and markets:
                    market = markets[0]
                    price = market.get('price', 'N/A')
                    volume = market.get('volume', 'N/A')
                    category = market.get('category', 'General')
                    
                    content += f"""
- {platform}:
  Price: {price}
  Volume: {volume}  
  Category: {category}
  Market ID: {market.get('market_id', 'N/A')}
"""
            
            # Add metadata (FIXED: Convert lists to strings)
            metadata = {
                'type': 'unified_market',
                'product_name': product_name,
                'confidence': confidence,
                'platforms': ', '.join(platforms.keys()),  # Convert list to string
                'platform_count': len(platforms)
            }
            
            # Clean metadata to ensure compatibility
            metadata = self.clean_metadata(metadata)
            
            documents.append(Document(
                page_content=content.strip(),
                metadata=metadata
            ))
        
        return documents
    
    def _create_raw_market_docs(self, data: List[Dict]) -> List[Document]:
        """Convert raw market data to documents"""
        documents = []
        
        for market in data:
            # FIXED: Handle string entries in raw data
            if isinstance(market, str):
                continue
                
            content = f"""Market: {market.get('market_name', 'Unknown')}
Platform: {market.get('platform', 'Unknown')}
Price: {market.get('price', 'N/A')}
Volume: {market.get('volume', 'N/A')}
Category: {market.get('category', 'General')}
Description: {market.get('description', 'No description available')}
Market ID: {market.get('market_id', 'N/A')}
"""
            
            metadata = {
                'type': 'raw_market',
                'platform': market.get('platform', 'Unknown'),
                'category': market.get('category', 'General'),
                'market_name': market.get('market_name', 'Unknown')
            }
            
            # Clean metadata
            metadata = self.clean_metadata(metadata)
            
            documents.append(Document(
                page_content=content.strip(),
                metadata=metadata
            ))
        
        return documents
    
    def _create_analysis_docs(self, data: Dict) -> List[Document]:
        """Convert analysis reports to documents"""
        documents = []
        
        # Platform coverage analysis
        if 'platform_coverage' in data:
            content = "Platform Coverage Analysis:\n"
            for platform, stats in data['platform_coverage'].items():
                content += f"- {platform}: {stats.get('count', 0)} markets, Total Volume: {stats.get('total_volume', 0)}\n"
            
            documents.append(Document(
                page_content=content,
                metadata={'type': 'analysis', 'category': 'platform_coverage'}
            ))
        
        # Category breakdown
        if 'category_breakdown' in data:
            content = "Category Breakdown:\n"
            for category, count in data['category_breakdown'].items():
                content += f"- {category}: {count} markets\n"
            
            documents.append(Document(
                page_content=content,
                metadata={'type': 'analysis', 'category': 'category_breakdown'}
            ))
        
        return documents
    
    def build_knowledge_base(self) -> Chroma:
        """Build the complete knowledge base"""
        log_info("🔍 Building RAG knowledge base from your market data...")
        
        # Load documents
        documents = self.load_market_data()
        
        if not documents:
            log_error("❌ No documents found to build knowledge base")
            return None
        
        log_info(f"📚 Loaded {len(documents)} documents")
        
        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)
        log_info(f"📄 Created {len(texts)} text chunks")
        
        # FIXED: Filter complex metadata before creating vectorstore
        from langchain_community.vectorstores.utils import filter_complex_metadata
        filtered_texts = filter_complex_metadata(texts)
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=filtered_texts,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        # Persist the database
        vectorstore.persist()
        
        log_success(f"✅ Knowledge base built successfully with {len(filtered_texts)} chunks")
        return vectorstore
    
    def load_existing_knowledge_base(self) -> Chroma:
        """Load existing knowledge base"""
        if os.path.exists(self.persist_directory):
            log_info("📚 Loading existing knowledge base...")
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            log_success("✅ Knowledge base loaded successfully")
            return vectorstore
        else:
            log_info("🔧 No existing knowledge base found, building new one...")
            return self.build_knowledge_base()
