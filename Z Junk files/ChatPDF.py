
# this is working 
# WROTE BLOG POST https://learnpythoneasily.com/question-answering-langchain-and-ollama/

from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


def ask_pdf(pdf_path, user_input):

    # Set up the Ollama model with the LLaMA3 model
    ollama_llm = Ollama(
        model="llama2",  # Specify LLaMA3 model
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
    )

    # upload file

    #pdf_path = "/Users/jamalabdullahi/Downloads/CCN20203 NETWORK AND DATA SECURITY/chapter 9 security.pdf"

    # extract the text
    with open(pdf_path, "rb") as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # split into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # create embeddings
    ollama_embeddings = OllamaEmbeddings()  # Remove ollama_llm argument
    knowledge_base = FAISS.from_texts(chunks, ollama_embeddings)

    # show user input
    user_question = user_input
    if user_question:
        docs = knowledge_base.similarity_search(user_question)

        # load QA chain
        chain = load_qa_chain(ollama_llm, chain_type="stuff")

        # run the chain
        response = chain.run(input_documents=docs, question=user_question)

        #print(response)
        return response


