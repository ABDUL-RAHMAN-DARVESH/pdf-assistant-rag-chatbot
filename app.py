import os
import tempfile
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

groq_api_key = os.getenv("Groq_Api_Key")
if not groq_api_key:
    raise ValueError("Groq API Key is missing! Set it in your .env file or environment variables.")

def process_pdf(uploaded_file):
    """Processes the uploaded PDF file and initializes the document retriever."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        pdf_path = tmp_file.name

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
    vector = FAISS.from_documents(final_documents, embeddings)
    
    llm = ChatGroq(model_name="llama3-70b-8192", api_key=groq_api_key)
    
    prompt_template = ChatPromptTemplate.from_template(
        """
        Answer the question based on the provided context only.
        Please provide the most accurate response based on the question.
        If the user's query does not match the provided context, then simply say:
        *I don't understand your query. Please check your prompt.*
        <context>
        {context}
        </context>
        Question: {input}
        """
    )

    document_chain = create_stuff_documents_chain(llm, prompt_template)
    retriever = vector.as_retriever()
    retriever_chain = create_retrieval_chain(retriever, document_chain)

    os.unlink(pdf_path)  # Remove temporary file
    return retriever_chain
