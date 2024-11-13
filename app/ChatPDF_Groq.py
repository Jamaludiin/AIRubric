from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from groq import Groq

# Get API key and validate
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Initialize ChatGroq
groq_llm = ChatGroq(
    #model="mixtral-8x7b-32768", # good sometimes dispay in table and sometimes not
    #model="gemma-7b-it", # good but result not formatted in table
    #model="llama3-8b-8192", # very good consistent results in table.
    #model="llama3-70b-8192", # very very good consistent results in table.
    model="llama-3.2-90b-vision-preview", # very good consistent results in table.
    #model="gemma2-9b-it", # very critical good but result not formatted in table
    #model="llama-3.1-70b-versatile", # cannot aceess this model.
    #model="llama-3.1-8b-instant", # 8000 tokens maximum.
    #model="whisper-large-v3-turbo", # does not support chat completions
    temperature=0.7,
    max_tokens=8192,
    timeout=10,
    max_retries=2,
)

def ask_pdf(pdf_path, user_input):
    # Extract text from PDF
    with open(pdf_path, "rb") as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # Split text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Create embeddings using HuggingFace
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    
    # Create knowledge base
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    # Process user question
    if user_input:
        docs = knowledge_base.similarity_search(user_input)
        
        # Load QA chain with Groq
        chain = load_qa_chain(groq_llm, chain_type="stuff")
        
        # Get response
        response = chain.run(input_documents=docs, question=user_input)
        return response

    return "No question provided"



