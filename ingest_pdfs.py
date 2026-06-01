import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "chroma_db"
# The folder containing our policy PDFs
DATA_PATH = "audit_files/policies"

def generate_data_store():
    print("Starting Document Ingestion Pipeline...")
    
    # Load the PDFs
    print(f"Scanning directory: {DATA_PATH} for PDFs...")
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")

    # Chunk the Text
    # We split the text into smaller chunks so the LLM doesn't get overwhelmed
    print("Chunking documents into smaller readable pieces...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # Create the Embeddings Model 
    # This downloads a tiny, highly efficient embedding model to run locally 
    print("Initializing Local Embedding Model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Save to ChromaDB
    print(f"Saving vectors to local ChromaDB at {CHROMA_PATH}...")
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)
        
    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print("Ingestion Complete! The Knowledge Base is ready.")

if __name__ == "__main__":
    generate_data_store()