from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

api_key = os.getenv('GROQ_API_KEY')  # Get the API key from the environment
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize the ChatGroq model
llm = ChatGroq(
    model="llama-3.2-90b-vision-preview",
    temperature=0.9,
    max_tokens=1024,
)

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Give me one question about {topic}?",
)

chain = LLMChain(llm=llm, 
                 prompt=prompt,
                 verbose=False)

# Run the chain only specifying the input variable.
print(chain.run("mobile programming using android"))