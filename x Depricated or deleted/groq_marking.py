from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from groq import Groq

# Get API key and validate
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize Groq client
client = Groq(api_key=api_key)

def process_pdf(pdf_path):
    """Extract and process text from PDF"""
    with open(pdf_path, "rb") as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def create_embeddings(text):
    """Create embeddings from text"""
    # Split text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    
    # Create knowledge base
    knowledge_base = FAISS.from_texts(chunks, embeddings)
    return knowledge_base

def mark_assignment(pdf_path):
    """Main function to mark assignments"""
    # Process PDF and create embeddings
    text = process_pdf(pdf_path)
    knowledge_base = create_embeddings(text)
    
    # Create marking prompt
    marking_prompt = """Using the rubric provided in the document, carefully evaluate each aspect of the Smartphone class assignment. Break down your assessment into categories as per the rubric: Object Design, Encapsulation, Main Class Implementation, Creativity and Object Choice, and Documentation and Comments."""
    
    # Get relevant context from knowledge base
    docs = knowledge_base.similarity_search(marking_prompt)
    
    # Initialize ChatGroq
    groq_llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.7,
        max_tokens=1150,
        timeout=10,
        max_retries=2,
    )
    
    # Create QA chain
    chain = load_qa_chain(groq_llm, chain_type="stuff")
    
    # Get marking result
    result = chain.run(
        input_documents=docs,
        question=marking_prompt
    )
    
    # Format the response as HTML
    html_response = f"""
    <div class="marking-results">
        <h1>Assignment Marking Results</h1>
        {result}
    </div>
    """
    
    return html_response

# Example usage
if __name__ == "__main__":
    try:
        result = mark_assignment("path/to/your/file.pdf")
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")