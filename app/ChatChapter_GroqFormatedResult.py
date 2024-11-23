import os
from langchain_groq import ChatGroq
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.output_parsers import ResponseSchema
import json

# Check for Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize Groq client
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="mixtral-8x7b-32768"
)

# Define the output schema for question generation
question_schemas = [
    ResponseSchema(name="question", description="The generated question"),
    ResponseSchema(name="answer", description="The correct answer to the question"),
    ResponseSchema(name="level", description="Difficulty level (easy, medium, hard)"),
    ResponseSchema(name="bloom_taxon", description="Bloom's Taxonomy level (1-6)"),
    ResponseSchema(name="topic", description="The specific topic of the question"),
    ResponseSchema(name="subject", description="The subject area of the question"),
    ResponseSchema(name="chapter", description="The chapter number or name")
]

def generate_questions(pdf_path):
    """
    Generate questions from a PDF document using Groq API.
    Returns a list of dictionaries containing question details.
    """
    # Load and split PDF
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(pages)
    
    # Question generation prompt template
    prompt_template = """
    You are an expert educator tasked with generating high-quality assessment questions. Generate 3 questions from the following text, ensuring each question:
    1. Tests different cognitive levels (use a mix of easy, medium, and hard difficulty)
    2. Maps to Bloom's Taxonomy (1=Remember, 2=Understand, 3=Apply, 4=Analyze, 5=Evaluate, 6=Create)
    3. Has a comprehensive, accurate answer
    4. Relates to a specific topic from the text
    
    Text to analyze: {text}
    
    Format your response as a valid JSON object with this exact structure:
    {{
        "questions": [
            {{
                "question": "Clear, well-formed question",
                "answer": "Detailed, accurate answer",
                "level": "easy|medium|hard",
                "bloom_taxon": "1-6",
                "topic": "specific topic from text",
                "subject": "general subject area",
                "chapter": "chapter identifier"
            }}
        ]
    }}
    
    Ensure all JSON fields are present and properly formatted.
    """
    
    all_questions = []
    
    for chunk in chunks:
        try:
            # Generate questions for each chunk
            prompt = prompt_template.format(text=chunk.page_content)
            response = llm.invoke(prompt)
            
            # Parse the response
            try:
                result = json.loads(response.content)
                # Extract chapter information from the page metadata
                chapter = f"Chapter {chunk.metadata.get('page', 1)}"
                
                # Validate and process each question
                if "questions" in result and isinstance(result["questions"], list):
                    for question in result["questions"]:
                        # Ensure all required fields are present
                        required_fields = ["question", "answer", "level", "bloom_taxon", "topic", "subject"]
                        if all(field in question for field in required_fields):
                            question["chapter"] = chapter
                            all_questions.append(question)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {str(e)}")
                continue
                
        except Exception as e:
            print(f"Error generating questions for chunk: {str(e)}")
            continue
    
    return all_questions

def format_bloom_taxonomy(level):
    """Helper function to format Bloom's Taxonomy level."""
    taxonomy = {
        1: "Remember",
        2: "Understand",
        3: "Apply",
        4: "Analyze",
        5: "Evaluate",
        6: "Create"
    }
    return f"Level {level} - {taxonomy.get(level, 'Unknown')}"

# Example usage
if __name__ == "__main__":
    pdf_path = "chapter_document.pdf"
    questions = generate_questions(pdf_path)
    print(json.dumps(questions, indent=2))
