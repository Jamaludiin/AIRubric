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

# Initialize Groq client and LLM
client = Groq(api_key=groq_api_key)
groq_llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0.7,
    max_tokens=32767,
    timeout=10,
    max_retries=2,
)

def mark_assignment(pdf_path):
    """Process PDF and return marking results"""
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

    # Define marking prompt
    marking_prompt = """
    As a Professor marking this assignment, please evaluate the following aspects:

    1. Object Design (20%)
    2. Encapsulation (20%)
    3. Main Class Implementation (20%)
    4. Creativity and Object Choice (20%)
    5. Documentation and Comments (20%)

    For each category:
    - Assign a score (Excellent: 4/4, Good: 3/4, Fair: 2/4, Needs Improvement: 1/4)
    - Provide specific feedback
    - Highlight strengths and areas for improvement
    - Give practical suggestions

    Format the response in HTML with appropriate tags (<h2>, <p>, <ul>, etc.).
    Include a final score and overall remarks.
    """

    # Get relevant context
    docs = knowledge_base.similarity_search(marking_prompt)
    
    # Create QA chain
    chain = load_qa_chain(groq_llm, chain_type="stuff")
    
    # Get response
    response = chain.run(input_documents=docs, question=marking_prompt)
    
    # Format response as HTML
    html_response = f"""
    <div class="marking-results">
        <h1>Assignment Marking Results</h1>
        {response}
    </div>
    """
    
    return html_response
