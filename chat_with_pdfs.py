import warnings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Clean terminal
warnings.filterwarnings("ignore")

CHROMA_PATH = "chroma_db"

def format_docs(docs):
    # This takes the retrieved document chunks and joins them into a single string
    return "\n\n".join(doc.page_content for doc in docs)

def start_chat():
    print("Booting up the Audit AI (Llama 3)...")
    
    # Initialize the embedding model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load the existing Vector Database
    print("Loading the Knowledge Base (ChromaDB)...")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # Set the retriever to fetch the top 3 most relevant chunks
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Initialize the LLM 
    llm = ChatOllama(model="llama3", temperature=0)

    # System Prompt
    template = """You are a strict Corporate Audit Assistant.
    Answer the user's question based ONLY on the following context (which contains company policies).
    If the answer is not in the context, say "I cannot find this in the corporate policies."
    Do not make up any rules.

    Context:
    {context}

    Question: {question}

    Answer:"""
    prompt = ChatPromptTemplate.from_template(template)

    # RAG Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("\nSystem Ready! Type 'exit' to quit.")
    print("-" * 50)

    # The interactive chat loop
    while True:
        user_input = input("\n You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Shutting down...")
            break
            
        print("Auditor: ", end="", flush=True)
        

        for chunk in rag_chain.stream(user_input):
            print(chunk, end="", flush=True)
        print() 

def query_policy(question: str) -> str:
    """Non-blocking RAG query for LangGraph"""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    llm = ChatOllama(model="llama3", temperature=0)
    
    template = """You are a strict Corporate Audit Assistant.
    Answer the user's question based ONLY on the following context.
    Context: {context}
    Question: {question}
    Answer:"""
    prompt = ChatPromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(question)

if __name__ == "__main__":
    start_chat()
