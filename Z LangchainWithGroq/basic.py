from langchain_groq import ChatGroq
import os

# Get the API key from environment variable
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize the ChatGroq model
llm = ChatGroq(
    model="llama-3.2-90b-vision-preview",  # Using llama3 model
    temperature=0.7,
    max_tokens=1024,
)

# Run the query
response = llm.invoke("Tell me 5 facts about Roman history:")
print(response.content)