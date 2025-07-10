"""
Streamlit Web Interface for DocuMindAI
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import streamlit as st
from agents.research_agent import ResearchAgent

# Page config
st.set_page_config(
    page_title="DocuMindAI",
    page_icon="🧠",
    layout="wide"
)

# Initialize agent
@st.cache_resource
def get_agent():
    return ResearchAgent()

def main():
    st.title("🧠 DocuMindAI")
    st.markdown("*Document Intelligence & Research Platform*")
    
    # Sidebar
    with st.sidebar:
        st.header("Features")
        st.markdown("""
        - 🌐 Web Search
        - 📄 Document Analysis
        - 💭 Conversation Memory
        - 🤖 Multi-tool Agent
        """)
        
        # Document Upload Section
        st.header("📄 Document Upload")
        uploaded_files = st.file_uploader(
            "Upload documents for analysis", 
            type=["pdf", "txt"], 
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("Process Documents"):
            # Create documents directory if it doesn't exist
            os.makedirs("data/documents", exist_ok=True)
            
            # Save uploaded files
            for uploaded_file in uploaded_files:
                file_path = os.path.join("data/documents", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            # Process the uploaded documents
            with st.spinner("Processing documents..."):
                # Create a query to process the documents
                query = "Process all documents in the data/documents directory"
                response = st.session_state.agent.process_query(query)
                st.success(f"✅ Documents processed successfully!")
        
        if st.button("Clear Memory"):
            st.session_state.agent.clear_memory()
            st.success("Memory cleared!")
    
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = get_agent()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.agent.process_query(prompt)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()