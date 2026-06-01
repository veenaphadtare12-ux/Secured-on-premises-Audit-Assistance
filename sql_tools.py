import re
from operator import itemgetter
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Old SQLite connetion
# db_path = "sqlite:///corporate_ledger.db"
# db = SQLDatabase.from_uri(db_path)

db_path = "postgresql+psycopg2://audit_admin:secure_password_123@localhost:5432/corporate_ledger"
db = SQLDatabase.from_uri(db_path)

# Initialize Llama 3
llm = ChatOllama(model="llama3", temperature=0)

# SQL Generation Prompt
sql_prompt = PromptTemplate.from_template(
    "You are a precise PostgreSQL expert. Given the following database schema:\n{schema}\n\n"
    "Write a valid PostgreSQL query to answer the following question: {question}\n\n"
    "IMPORTANT RULES:\n"
    "1. Return ONLY the raw SQL query. Do not use markdown blocks (```sql), quotes, or explanations.\n"
    "2. When aggregating or grouping categories, ALWAYS return multiple rows with exactly two columns (e.g., Category Name, Amount).\n"
    "3. NEVER return pivoted or flattened single-row results.\n"
    "4. The 'date' column is stored as TEXT ('YYYY-MM-DD'). You MUST cast it to DATE (e.g., CAST(date AS DATE)) before using date functions like EXTRACT."
)
# Helpers
def get_schema(_):
    return db.get_table_info()

def clean_sql(response) -> str:
    query = response.content
    return query.replace("```sql", "").replace("```", "").strip()

# SQL generation chain
sql_generation_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | sql_prompt
    | llm
    | clean_sql
)

# Execution tool
execute_query = QuerySQLDatabaseTool(db=db)

# The Answering Prompt & Chain
answer_prompt = PromptTemplate.from_template(
    "You are an AI financial audit assistant. "
    "Given the user's question, the SQL query used to find the data, and the raw database result, "
    "write a concise, professional, and natural language answer.\n\n"
    "Question: {question}\n"
    "SQL Query: {query}\n"
    "Raw Result: {result}\n\n"
    "Final Answer:"
)

answering_chain = answer_prompt | llm | StrOutputParser()

# Final master chain
final_chain = (
    RunnablePassthrough.assign(query=sql_generation_chain)
    .assign(result=itemgetter("query") | execute_query)
    .assign(answer=answering_chain) # This pipes the context into the answering chain
)

if __name__ == "__main__":
    test_question = "What is the amount logged for transaction TXN-1004? and What is the amount logged for transaction TXN-1003?"
    print(f"Question: {test_question}")
    print("-" * 40)
    
    try:
        response = final_chain.invoke({"question": test_question})
        print(f"Generated SQL: {response['query']}")
        print(f"Raw DB Result: {response['result']}")
        print("-" * 40)
        print(f"Final AI Answer: {response['answer']}")
    except Exception as e:
        print(f"Error during execution: {e}")