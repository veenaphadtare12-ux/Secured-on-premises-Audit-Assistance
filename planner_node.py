from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Defining the strict JSON schema we want Llama 3 to output
class ExecutionPlan(BaseModel):
    intent: Literal["visualization", "analysis", "audit"] = Field(
        description="The category of the user's request: 'visualization' for charts, 'analysis' for data comparisons, or 'audit' for policy/receipt checks."
    )
    steps: List[str] = Field(
        description="The exact sequence of tools to call. Choose ONLY from this list: [fetch_sql_data, generate_chart, compare_metrics, generate_summary, fetch_receipt_vision, check_policy_rag, generate_audit_report]"
    )

# Setting up the parser based on our Pydantic model
parser = PydanticOutputParser(pydantic_object=ExecutionPlan)

# System Prompt
planner_prompt = PromptTemplate(
    template="""You are the core routing intelligence for an On-Prem AI Data Assistant.
Your job is to read the user's query and generate a strict execution plan.

{format_instructions}

User Query: {query}

Generate the execution plan now:""",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Initialize the local LLM 
llm = ChatOllama(model="llama3", temperature=0, format="json")

# Planner Chain
planner_chain = planner_prompt | llm | parser

if __name__ == "__main__":
    test_queries = [
        "Create a pie chart of expenses in March for travel, infrastructure, salaries and food & beverage.",
        "Compare the sales of September and October and write a short analysis on it.",
        "Audit TXN-004 and check if it violates any company policies."
    ]

    print("Initializing Planner Node Test...\n" + "="*50)
    
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            # Invoke the chain
            plan = planner_chain.invoke({"query": query})
            print(f"Detected Intent: {plan.intent}")
            print(f"Execution Steps: {plan.steps}")
        except Exception as e:
            print(f"Failed to parse output: {e}")
        print("-" * 50)