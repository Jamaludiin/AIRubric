# Load web page
import argparse
import os
import sys
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain import hub

def main():
    try:
        # Check for API key
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set. Please set it with: export GROQ_API_KEY='your-key'")

        # Set default URL and allow override
        default_url = 'https://python.langchain.com/docs/how_to/output_parser_custom/'
        parser = argparse.ArgumentParser(description='Process URL for RAG.')
        parser.add_argument('--url', type=str, default=default_url, help='The URL to process (default: LangChain docs)')

        args = parser.parse_args()
        url = args.url
        print(f"Using URL: {url}")

        # Load and process the webpage
        print("Loading webpage...")
        loader = WebBaseLoader(url)
        data = loader.load()

        # Split into chunks 
        print("Splitting content into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        all_splits = text_splitter.split_documents(data)
        print(f"Split into {len(all_splits)} chunks")

        # Create vector store with HuggingFace embeddings
        print("Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(
            documents=all_splits,
            embedding=embeddings
        )
        print(f"Loaded {len(data)} documents into vector store")

        # Initialize Groq model
        print("Initializing Groq model...")
        model_name = "llama-3.2-90b-vision-preview"
        llm = ChatGroq(
            model=model_name,
            temperature=0.7,
            max_tokens=2048,
            verbose=True
        )
        print(f"Initialized Groq LLM with model: {model_name}")

        # RAG prompt
        print("Setting up RAG chain...")
        QA_CHAIN_PROMPT = hub.pull("rlm/rag-prompt-llama")

        # QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        )

        # Ask a question
        question = f"What are the main topics discussed on {url}? Please provide a detailed summary."
        print("\nQuestion:", question)
        print("\nGenerating response...")
        result = qa_chain({"query": question})
        print("\nAnswer:", result["result"])

    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
