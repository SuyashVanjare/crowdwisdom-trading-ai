import os
from typing import List
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_chroma import Chroma
from agents.rag_knowledge_base import PredictionMarketKnowledgeBase
from utils.logger import log_info, log_success, log_error

class PredictionMarketChatBot:
    """Interactive chatbot for prediction market data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.knowledge_base = PredictionMarketKnowledgeBase()
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Custom prompt template
        self.prompt_template = """
You are an expert prediction market analyst with access to comprehensive market data from multiple platforms including Polymarket, Kalshi, Prediction-Market, and Manifold.

Use the following context to answer questions about prediction markets, trading opportunities, arbitrage possibilities, and market analysis:

Context: {context}
Chat History: {chat_history}
Question: {question}

Instructions:
- Provide accurate, data-driven responses based on the retrieved market data
- When discussing prices, always mention which platform(s) the data comes from
- Highlight arbitrage opportunities when price differences exist across platforms
- Explain confidence scores when relevant
- Be conversational and helpful
- If you don't have specific data to answer a question, say so clearly

Answer:"""

    def initialize(self):
        """Initialize the chatbot with knowledge base and LLM"""
        log_info("🤖 Initializing Prediction Market ChatBot...")
        
        try:
            # Load or build knowledge base
            self.vectorstore = self.knowledge_base.load_existing_knowledge_base()
            
            # FIXED: Better check for vectorstore
            if self.vectorstore is None:
                log_error("❌ Failed to load knowledge base")
                return False
            
            log_success("✅ Knowledge base loaded successfully")
            
            # Initialize LLM
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=self.api_key,
                temperature=0.7
            )
            
            # Create custom prompt
            custom_prompt = PromptTemplate(
                template=self.prompt_template,
                input_variables=["context", "chat_history", "question"]
            )
            
            # Create conversational retrieval chain
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": custom_prompt},
                verbose=True
            )
            
            log_success("✅ ChatBot initialized successfully!")
            return True
            
        except Exception as e:
            log_error(f"❌ Failed to initialize ChatBot: {e}")
            return False
    
    def chat(self, question: str) -> str:
        """Process a chat message and return response"""
        if not self.qa_chain:
            return "❌ ChatBot not initialized. Please run initialize() first."
        
        try:
            log_info(f"💬 Processing question: {question}")
            
            response = self.qa_chain({"question": question})
            answer = response.get("answer", "Sorry, I couldn't generate an answer.")
            
            log_info("✅ Generated response successfully")
            return answer
            
        except Exception as e:
            log_error(f"❌ Error processing question: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_market_summary(self) -> str:
        """Get a quick summary of available markets"""
        return self.chat("Give me a summary of all available prediction markets, including the number of platforms and categories covered.")
    
    def find_arbitrage_opportunities(self) -> str:
        """Find potential arbitrage opportunities"""
        return self.chat("What are the best arbitrage opportunities available? Show me markets with significant price differences across platforms.")
    
    def get_platform_comparison(self) -> str:
        """Compare platforms"""
        return self.chat("Compare the different prediction market platforms. Which ones have the most markets and highest volumes?")
    
    def search_markets(self, query: str) -> str:
        """Search for specific markets"""
        return self.chat(f"Find prediction markets related to: {query}")

def main():
    """Test the chatbot"""
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    # Initialize chatbot
    chatbot = PredictionMarketChatBot(api_key)
    
    if not chatbot.initialize():
        print("❌ Failed to initialize chatbot")
        return
    
    print("🤖 Prediction Market ChatBot initialized!")
    print("Type 'quit' to exit, 'summary' for market overview, 'arbitrage' for opportunities")
    print("-" * 60)
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye! Happy trading!")
            break
        elif user_input.lower() == 'summary':
            response = chatbot.get_market_summary()
        elif user_input.lower() == 'arbitrage':
            response = chatbot.find_arbitrage_opportunities()
        else:
            response = chatbot.chat(user_input)
        
        print(f"\n🤖 Bot: {response}")

if __name__ == "__main__":
    main()
