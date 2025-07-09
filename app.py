#!/usr/bin/env python3
"""
Chatty - Workers' Compensation Chatbot
Streamlit application for AI-powered workers' compensation assistance
"""

import streamlit as st
import json
from typing import List, Dict, Any
import time

# Import our modules
from config import Config
from database.supabase_client import SupabaseClient
from utils.embedding_service import EmbeddingService
from utils.llm_service import LLMService

# Page configuration
st.set_page_config(
    page_title="Chatty - Workers' Compensation Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .source-citation {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 5px;
        padding: 0.5rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_services():
    """Initialize and cache services"""
    try:
        Config.validate()
        return {
            'supabase': SupabaseClient(),
            'embedding': EmbeddingService(),
            'llm': LLMService()
        }
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        return None

def format_sources(chunks: List[Dict[str, Any]]) -> str:
    """Format source citations for display"""
    sources = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        filename = metadata.get("filename", "Unknown")
        title = metadata.get("title", filename)
        similarity = chunk.get("similarity", 0)
        
        sources.append(f"[{i}] {title} ({filename}) - Similarity: {similarity:.2f}")
    
    return "\n".join(sources)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Chatty</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI Assistant for Australian Workers\' Compensation</p>', unsafe_allow_html=True)
    
    # Initialize services
    services = initialize_services()
    if not services:
        st.error("Failed to initialize services. Please check your configuration.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Knowledge Base")
        
        # Show uploaded documents
        try:
            documents = services['supabase'].get_all_documents()
            if documents:
                st.subheader("Uploaded Documents")
                for doc in documents:
                    chunk_count = services['supabase'].get_chunk_count(doc['id'])
                    st.write(f"📄 {doc['title']}")
                    st.caption(f"Chunks: {chunk_count} | Size: {doc['file_size']:,} bytes")
            else:
                st.info("No documents uploaded yet.")
        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")
        
        st.divider()
        
        # Configuration
        st.subheader("⚙️ Configuration")
        st.write(f"Model: {Config.LLM_MODEL}")
        st.write(f"Temperature: {Config.TEMPERATURE}")
        st.write(f"Max Results: {Config.TOP_K_RESULTS}")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources"):
                    st.text(message["sources"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about workers' compensation..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Show thinking indicator
                with st.spinner("🔍 Searching knowledge base..."):
                    # Get embedding for the question
                    question_embedding = services['embedding'].get_embedding(prompt)
                    
                    # Search for similar chunks
                    similar_chunks = services['supabase'].search_similar_chunks(question_embedding)
                
                if not similar_chunks:
                    response = "I don't have enough information in my knowledge base to answer your question accurately. Please ensure relevant workers' compensation documents have been uploaded."
                    sources = "No relevant sources found."
                else:
                    with st.spinner("🤖 Generating response..."):
                        # Generate response using LLM
                        response = services['llm'].generate_response(prompt, similar_chunks)
                    
                    # Format sources
                    sources = format_sources(similar_chunks)
                
                # Display response
                message_placeholder.markdown(response)
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "sources": sources
                })
                
                # Show sources in expander
                if similar_chunks:
                    with st.expander("📚 View Sources"):
                        st.text(sources)
                
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_message
                })
    
    # Clear chat button
    if st.session_state.messages and st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main() 