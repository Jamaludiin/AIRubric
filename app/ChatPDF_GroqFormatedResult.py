from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
import os
import json
from groq import Groq

# Get API key and validate
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Define the output schema for rubric assessment
response_schemas = [
    ResponseSchema(name="student_info", description="Student information including name, ID, and assignment title"),
    ResponseSchema(name="categories", description="List of assessment categories with scores and feedback"),
    ResponseSchema(name="total_score", description="Total score including percentage"),
    ResponseSchema(name="overall_remarks", description="Overall remarks about the submission"),
    ResponseSchema(name="html_output", description="Complete assessment formatted in HTML")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

# Initialize ChatGroq
groq_llm = ChatGroq(
    model="llama-3.2-90b-vision-preview",
    temperature=0.7,
    max_tokens=8192,
    timeout=10,
    max_retries=2,
)

# Create the prompt template with formatting instructions
assessment_template = """Based on the provided PDF content, please create a detailed assessment following this rubric:

Content to assess: {context}

Question/Task: {question}

Please provide a detailed assessment following these requirements:

1. Student Information:
   - Student Name (from the document)
   - Student ID (from the document)
   - Assignment Title (from the document)

2. For each category or question assessed:
   - Score breakdown (Excellent/Good/Fair/Needs Improvement with numerical scores)
   - Specific feedback with evidence from the submission
   - Strengths (correct statements)
   - Areas for improvement (incorrect statements)
   - Practical suggestions for improvement

3. Include for each category:
   - Total Marks (e.g., 9/12 - 75%)
   - Criticism (specific incorrect statements)
   - Improvement suggestions
   - Strengths (specific correct statements)
   - Remarks

4. Format the output in HTML with appropriate tags and Bootstrap classes:
   <div class="assessment-container">


     <h1 class="text-primary mb-4">Assessment Report</h1>
     
     <div class="student-info card mb-4">
       <div class="card-header bg-info text-white">
         <h2 class="h4 mb-0">Student Information</h2>
       </div>
       <div class="card-body">
         [Student name here]
         [Student id here]
         [Student details here]
       </div>
     </div>

     <div class="categories-section">
       <h2 class="text-success mb-3">Assessment Criteria</h2>
       <div class="table-responsive">
         <table class="table table-bordered">
           <thead class="bg-light">
             <tr>
               <th>Criteria</th>
               <th>Score</th>
               <th>Feedback</th>
             </tr>
           </thead>
           <tbody>
             [Category rows here]
           </tbody>
         </table>
       </div>
     </div>

     <div class="total-score card mb-4">
       <div class="card-header bg-success text-white">
         <h2 class="h4 mb-0">Total Score</h2>
       </div>
       <div class="card-body">
         <h3 class="display-4 text-center">[Score]/[Total]</h3>
       </div>
     </div>

     <div class="remarks card">
       <div class="card-header bg-primary text-white">
         <h2 class="h4 mb-0">Overall Remarks</h2>
       </div>
       <div class="card-body">
         [Overall remarks here]
       </div>
     </div>
   </div>

{format_instructions}

Remember to:
1. Be specific about correct and incorrect statements
2. Provide actionable feedback
3. Use proper HTML formatting with Bootstrap classes
4. Include numerical scores and percentages
5. Give constructive overall remarks

Answer in the specified JSON format."""

PROMPT = PromptTemplate(
    template=assessment_template,
    input_variables=["question", "context"],
    partial_variables={"format_instructions": format_instructions}
)

def assess_pdf(pdf_path, assessment_prompt):
    try:
        # Extract text from PDF
        with open(pdf_path, "rb") as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

        # Split text into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1500,
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

        if assessment_prompt:
            # Get relevant documents
            docs = knowledge_base.similarity_search(assessment_prompt)
            context = " ".join([doc.page_content for doc in docs])
            
            # Format the prompt
            formatted_prompt = PROMPT.format(
                question=assessment_prompt,
                context=context
            )
            
            # Get response from Groq
            response = groq_llm.invoke(formatted_prompt)
            
            try:
                # Parse the response into structured format
                parsed_response = output_parser.parse(response.content)
                
                # Return both JSON and HTML
                return {
                    "json_response": json.dumps(parsed_response, indent=2),
                    "html_output": parsed_response.get("html_output", "HTML output not available")
                }
            except Exception as e:
                return {
                    "error": f"Failed to parse response: {str(e)}",
                    "raw_response": response.content
                }

        return {"error": "No assessment prompt provided"}
    
    except Exception as e:
        return {
            "error": f"An error occurred: {str(e)}",
            "details": str(e.__class__.__name__)
        }

# Example usage
if __name__ == "__main__":
    pdf_path = "student_submission.pdf"
    assessment_prompt = "Assess this assignment focusing on the technical implementation and documentation."
    result = assess_pdf(pdf_path, assessment_prompt)
    
    # Print JSON response
    print("\nJSON Response:")
    print(result.get("json_response", result.get("error", "Unknown error")))
    
    # Print HTML output
    print("\nHTML Output:")
    print(result.get("html_output", "HTML not available"))
