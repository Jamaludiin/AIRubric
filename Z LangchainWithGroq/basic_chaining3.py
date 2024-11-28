from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import os
import json

api_key = os.getenv('GROQ_API_KEY')  # Get the API key from the environment
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Define the output schema
response_schemas = [
    ResponseSchema(name="question", description="The generated question about the topic"),
    ResponseSchema(name="category", description="The category or domain of the question"),
    ResponseSchema(name="difficulty", description="The difficulty level of the question (easy/medium/hard)"),
    ResponseSchema(name="bloom_taxon", description="Bloom's Taxonomy level (1-6)"),
    ResponseSchema(name="answer", description="The correct answer to the question")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

# Initialize the ChatGroq model
llm = ChatGroq(
    model="llama-3.2-90b-vision-preview",
    temperature=0.9,
    max_tokens=1024,
)

prompt = PromptTemplate(
    input_variables=["topic"],
    template="""Generate a question about {topic}. 
    
{format_instructions}

Make sure to format the response as specified above.""",
    partial_variables={"format_instructions": format_instructions}
)

chain = LLMChain(llm=llm, 
                 prompt=prompt,
                 verbose=False)

# Run the chain and parse the output
response = chain.run("mobile programming using android")
try:
    parsed_output = output_parser.parse(response)
    #print(json.dumps(parsed_output, indent=2))

    # only print the question
    print("\n\n")

    print(parsed_output)
    print("\n\n")
    print("Question: " + parsed_output["question"])
    print("\nCategory: " + parsed_output["category"])
    print("\nDifficulty: " + parsed_output["difficulty"])
    print("\nBloom's Taxon: " + parsed_output["bloom_taxon"])
    print("\nAnswer: " + parsed_output["answer"])
    print("\n\n")



except Exception as e:
    print("Raw response:", response)
    print("Error parsing response:", str(e))