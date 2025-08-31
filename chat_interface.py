import streamlit as st
import os
from agents.rag_chat_agent import PredictionMarketChatBot
from utils.logger import log_info

# Page configuration
st.set_page_config(
    page_title="CrowdWisdom Trading AI - Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_chatbot():
    """Initialize the chatbot"""
    if 'chatbot' not in st.session_state:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("❌ Please set GEMINI_API_KEY environment variable")
            return None
        
        with st.spinner("🔧 Initializing ChatBot..."):
            chatbot = PredictionMarketChatBot(api_key)
            if chatbot.initialize():
                st.session_state.chatbot = chatbot
                st.success("✅ ChatBot initialized successfully!")
                return chatbot
            else:
                st.error("❌ Failed to initialize ChatBot")
                return None
    return st.session_state.chatbot

def main():
    """Main Streamlit app"""
    
    # Header
    st.title("🤖 CrowdWisdom Trading AI Chat")
    st.markdown("Chat with your prediction market data using AI!")
    
    # Sidebar with quick actions
    with st.sidebar:
        st.header("🚀 Quick Actions")
        
        if st.button("📊 Market Summary"):
            if 'chatbot' in st.session_state:
                with st.spinner("Generating summary..."):
                    response = st.session_state.chatbot.get_market_summary()
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        if st.button("💰 Find Arbitrage"):
            if 'chatbot' in st.session_state:
                with st.spinner("Finding arbitrage opportunities..."):
                    response = st.session_state.chatbot.find_arbitrage_opportunities()
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        if st.button("🏢 Compare Platforms"):
            if 'chatbot' in st.session_state:
                with st.spinner("Comparing platforms..."):
                    response = st.session_state.chatbot.get_platform_comparison()
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.markdown("---")
        
        # Example questions
        st.header("💡 Example Questions")
        example_questions = [
            "What Tesla-related prediction markets are available?",
            "Which platform has the best prices for election markets?", 
            "Show me all markets with >90% confidence scores",
            "What are the most liquid prediction markets?",
            "Compare prices for the same market across platforms"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{hash(question)}"):
                st.session_state.user_input = question
    
    # Initialize chatbot
    chatbot = initialize_chatbot()
    
    if not chatbot:
        st.stop()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "👋 Hi! I'm your CrowdWisdom Trading AI assistant. I can help you analyze prediction markets, find arbitrage opportunities, and answer questions about your market data. What would you like to know?"
            }
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    if prompt := st.chat_input("Ask me anything about prediction markets...") or st.session_state.user_input:
        if st.session_state.user_input:
            prompt = st.session_state.user_input
            st.session_state.user_input = ""
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.chat(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by CrowdWisdom Trading AI - Making prediction markets accessible through AI*")

if __name__ == "__main__":
    main()
