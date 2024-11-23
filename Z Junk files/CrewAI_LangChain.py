# blog written
# https://learnpythoneasily.com/large-language-models-llms-for-code-generation-with-crewai/

from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq

import os
from groq import Groq

api_key = os.getenv('GROQ_API_KEY')  # Get the API key from the environment
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=api_key)



"""client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)"""


# Instantiate the ChatGroq model (replacing Ollama)
groq_llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0.7,
    max_tokens=1150,  # Limiting max tokens for brevity in response
    timeout=10,  # Optional: setting a timeout in case of slow responses
    max_retries=2,
)

def crew_result(user_input):
# Define your agents with roles and goals
  researcher = Agent(
      role='Researcher',
      #goal='Generate code based on the provided explanation.',
      goal='To provide what the users asked with detailed explanations',

      backstory="""
      You are a researcher. Using the information provided in the task, your goal is to give detailed response.
      """,
      verbose=True,
      allow_delegation=False,
      llm=groq_llm #ollama_llm
    )

  writer = Agent(
      role='Content writer',
      goal='Craft compelling content based on the provided answer script.',
      backstory="""You are a writer known for your ability to explain technical concepts in an engaging and informative way. 
      Your task is to create content that explains the generated answers to the audience.""",
      verbose=True,
      allow_delegation=True,
      llm= groq_llm # ollama_llm
    )

  # Prompt the user for the type of code they want
  #code_type = input("What type of code would you like to generate? (e.g., Python, JavaScript, HTML): ")
  code_type = "Python"

  # Explain the purpose of the code
  #explanation = input("Please explain what you want the code to achieve: ")
  explanation = "give one paragraphs about python"

  # Create a task based on the user input
  task = Task(
      #description=f"""Generate {user_input} code based on the following explanation:\n\n{explanation}""",
      description=f"""{user_input}""",
      expected_output=f"{code_type} answer was generated successfully",
      agent=researcher
   )

  # Instantiate your crew with a single task
  crew = Crew(
      agents=[researcher, writer],
      tasks=[task],
      #verbose=2  # Set verbose level
  ) 

  # Get your crew to work!

  print("Starting crew task...")  # Debugging message
  try:
        # Get your crew to work!
        result = crew.kickoff()
        print("Generated Result: ", result)  # Debugging output to see what result we get
        return result
  except Exception as e:
        print(f"Error in crew_result: {e}")
        return None


"""

# Call the function to run the tasks
result = crew_result()
print(result)"""


"""
# Write the result to a text file
with open("generated_code.txt", "w") as file:
    file.write(result)
"""
print("###########")
# print("Result written successfully.", crew_result())















