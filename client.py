import streamlit as st
from app import process_pdf

def initialize_session():
    st.session_state.chat_history = []
    st.session_state.file_processed = False
    st.session_state.last_input = None

# Page Configuration
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="\U0001F4DA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .main { padding: 2rem; }
        .stButton > button { width: 100%; background-color: #FF9900; color: white; }
        .stButton > button:hover { background-color: #FF8000; color: white; }
        .upload-text { text-align: center; padding: 2rem; border: 2px dashed #FF9900; border-radius: 10px; margin-bottom: 2rem; }
        .chat-message { padding: 1rem; border-radius: 10px; margin-bottom: 1rem; background-color: #f0f2f6; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    initialize_session()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/chat.png", width=100)
    st.title("PDF Chat Assistant")
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("""
    1. Upload your PDF document
    2. Wait for processing
    3. Ask questions about your document
    4. Get AI-powered responses
    """)
    st.markdown("---")
    if st.button("Clear Chat History"):
        initialize_session()
        st.rerun()

# Main content
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.file_processed:
        st.markdown("""
            <div class="upload-text">
                <h2>\U0001F4C4 Upload Your PDF Document</h2>
                <p>Upload a PDF file to start chatting about its contents</p>
            </div>
        """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type="pdf")

# Process uploaded file
if uploaded_file is not None and not st.session_state.file_processed:
    with st.spinner("Processing your document... Please wait."):
        st.session_state.retriever_chain = process_pdf(uploaded_file)
        st.session_state.file_processed = True
    st.success("\u2705 Document processed successfully!")
    st.rerun()

# Chat interface
if st.session_state.file_processed:
    st.markdown("### Chat with your PDF")
    
    for message in st.session_state.chat_history:
        st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")
        st.markdown("---")
    
    user_prompt = st.text_input("Ask a question about your document:")
    
    if user_prompt and user_prompt != st.session_state.last_input:
        with st.spinner("Thinking..."):
            response = st.session_state.retriever_chain.invoke({"input": user_prompt})
            
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
            
            st.session_state.last_input = user_prompt
            st.rerun()

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center'><p>Made with ❤️ by Darvesh</p></div>", unsafe_allow_html=True)
