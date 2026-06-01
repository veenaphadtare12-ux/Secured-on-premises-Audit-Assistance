import re
import matplotlib.pyplot as plt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama
from sql_tools import final_chain as sql_chain
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from planner_node import planner_chain  
from sql_tools import final_chain as sql_chain
from receipt_parser import extract_receipt_data
from chat_with_pdfs import query_policy
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser


# Defining the Shared Memory (The Graph State)
class BIState(TypedDict):
    query: str
    intent: str
    execution_plan: List[str]
    raw_data: dict
    final_output: str

# The Planner Node Function
def generate_plan(state: BIState):
    print(f"[Planner Node] Analyzing Query: '{state['query']}'")
    # Call the LLM to get the structured JSON plan
    plan = planner_chain.invoke({"query": state["query"]})
    
    # Update the state with the LLM's decisions
    return {"intent": plan.intent, "execution_plan": plan.steps}

def visualization_lane(state: BIState):
    print(f"[Viz Lane] Processing Query: '{state['query']}'")
    
    # Step 1: Fetch the Data using the SQL tools
    print("   -> Fetching data from SQLite ledger...")
    sql_response = sql_chain.invoke({"question": state["query"]})
    raw_data = sql_response['result']
    print(f"   -> Raw Data Retrieved: {raw_data}")
    
    # Step 2: Use Llama 3 to structure the raw data into chart-ready JSON
    print("   -> Structuring data for Matplotlib...")
    llm = ChatOllama(model="llama3", temperature=0, format="json")
    
    prompt = ChatPromptTemplate.from_template("""
    You are a data visualization expert.
    Convert the following raw SQLite database result into a strict JSON format for plotting.
    The user wants to answer this question: {question}

    Return ONLY a valid JSON object with these exact keys:
    "title" (string, a professional title for the chart),
    "labels" (list of strings, the categories/names),
    "values" (list of numbers, the data points),
    "chart_type" (string, either "pie" or "bar" depending on the user's query).

    Raw SQLite Result: {raw_data}
    """)
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        chart_data = chain.invoke({
            "question": state["query"], 
            "raw_data": str(raw_data)
        })
    except Exception as e:
        return {"final_output": f"❌ Error parsing chart data: {e}"}

    # Step 3: Deterministically render the chart using Matplotlib
    print(f"   -> Rendering modern {chart_data['chart_type']} chart...")
    
    background_color = '#1e1e2e'
    text_color = '#cdd6f4'
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=background_color)
    
    if chart_data["chart_type"] == "pie":
        
        colors = ['#89b4fa', '#a6e3a1', '#f38ba8', '#f9e2af', '#cba6f7']

        total = sum(chart_data["values"])
        def label_format(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f"{pct:.1f}%\n(${absolute:,})" if pct > 3 else ""
            
        wedges, texts, autotexts = ax.pie(
            chart_data["values"], 
            autopct=lambda pct: label_format(pct, chart_data["values"]),
            textprops=dict(color=background_color, fontsize=10, fontweight='bold'),
            colors=colors,
            startangle=140,
            wedgeprops=dict(width=0.4, edgecolor=background_color, linewidth=3),
            pctdistance=0.78
        )
        
        ax.text(0, 0, f"TOTAL\n${total:,.2f}", ha='center', va='center', 
                fontsize=18, fontweight='bold', color=text_color)
        
        ax.legend(wedges, chart_data["labels"], title="Categories", loc="center left", 
                  bbox_to_anchor=(1, 0, 0.5, 1), frameon=False, labelcolor=text_color, title_fontsize=12)

    else:
        # Fallback
        ax.bar(chart_data["labels"], chart_data["values"], color='#89b4fa', edgecolor='none')
        ax.set_facecolor(background_color)
        ax.tick_params(colors=text_color, bottom=False, left=False)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        for i, v in enumerate(chart_data["values"]):
            ax.text(i, v + (max(chart_data["values"])*0.02), f"${v:,.2f}", 
                    ha='center', color=text_color, fontweight='bold')

    plt.title(chart_data["title"], pad=20, fontsize=20, fontweight='bold', color=text_color)
    plt.tight_layout()

    # Saving the generated file
    save_path = "audit_files/generated_chart.png"
    plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()

    return {"final_output": f"Success! {chart_data['title']} saved to {save_path}"}

def analysis_lane(state: BIState):
    print(f"[Analysis Lane] Processing Query: '{state['query']}'")
    
    # Fetch Data (SQLite)
    print("   -> Fetching data from SQLite ledger...")
    try:
        sql_response = sql_chain.invoke({"question": state["query"]})
        raw_data = sql_response['result']
        print(f"      [DB] Raw Data: {raw_data}")
    except Exception as e:
        return {"final_output": f"❌ Error fetching data for analysis: {e}"}
    
    # Synthesize Analysis (Llama 3)
    print("   -> Generating business analysis...")
    llm = ChatOllama(model="llama3", temperature=0.2) # Slight temp increase for better narrative flow
    
    analysis_prompt = ChatPromptTemplate.from_template("""
    You are a sharp, highly analytical Business Intelligence AI.
    The user asked the following question: {query}
    
    Based ONLY on the following raw database results, write a concise, professional business analysis.
    Compare the metrics, highlight any percentage differences, and state the clear takeaway. 
    Keep it strictly under 4 sentences.
    
    Raw Database Results: {raw_data}
    
    Business Analysis:
    """)
    
    analysis_chain = analysis_prompt | llm | StrOutputParser()
    
    try:
        final_analysis = analysis_chain.invoke({
            "query": state["query"],
            "raw_data": str(raw_data)
        })
    except Exception as e:
        return {"final_output": f"Error generating analysis: {e}"}
        
    return {"final_output": f" Analysis Complete:\n\n{final_analysis}"}

def audit_lane(state: BIState):
    print(f"[Audit Lane] Processing Query: '{state['query']}'")
    
    # Extract the Transaction ID from the query
    # Using regex for fast, deterministic extraction
    match = re.search(r'(TXN-\d+)', state['query'].upper())
    if not match:
        return {"final_output": "Error: Could not identify a valid Transaction ID (e.g., TXN-1004) in your query."}
    
    txn_id = match.group(1)
    print(f"   -> Target Identified: {txn_id}")
    
    # Fetch Ledger Data (SQLite)
    print("   -> Fetching database records...")
    sql_query = f"What is the logged amount and vendor for {txn_id}?"
    sql_response = sql_chain.invoke({"question": sql_query})
    db_data = sql_response['answer']
    print(f"      [DB] {db_data}")
    
    # Fetch Visual OCR Data (Florence-2)
    print("   -> Scanning physical receipt...")
    image_path = f"audit_files/receipts/receipt_{txn_id}.png"
    try:
        receipt_data = extract_receipt_data(image_path)
        receipt_summary = f"Vendor: {receipt_data.get('vendor')}, Amount: {receipt_data.get('amount')}"
        print(f"      [VLM] {receipt_summary}")
    except Exception as e:
        receipt_summary = f"Could not read receipt image: {e}"
        print(f"      [VLM] {receipt_summary}")

    # Fetch Corporate Policy (ChromaDB RAG)
    print("   -> Checking corporate policies...")
    policy_query = "What is the policy for receipt discrepancies, matching amounts, and manual review thresholds?"
    policy_data = query_policy(policy_query)
    
    # Synthesize the Final Audit Report using Llama 3
    print("   -> Synthesizing final audit report...")
    llm = ChatOllama(model="llama3", temperature=0)
    
    synthesis_prompt = ChatPromptTemplate.from_template("""
    You are a sharp, conversational AI Audit Assistant interacting with a user via a chat interface.
    Review the data for transaction {txn_id}.
    Compare the Database Ledger Record against the Physical Receipt OCR.
    
    Write a natural, concise, and direct response. 
    DO NOT use letter formatting, headers, "To/From", or signatures.
    Simply state what you found, if it violates policy, and your final verdict (APPROVED or FLAGGED FOR REVIEW).

    1. Database Ledger Record: {db_data}
    2. Physical Receipt OCR: {receipt_data}
    3. Corporate Policy: {policy_data}

    Response:
    """)
    
    synthesis_chain = synthesis_prompt | llm | StrOutputParser()
    
    final_report = synthesis_chain.invoke({
        "txn_id": txn_id,
        "db_data": db_data,
        "receipt_data": receipt_summary,
        "policy_data": policy_data
    })
    
    return {"final_output": f"\n{final_report}"}

# The Routing Logic
def route_intent(state: BIState) -> str:
    intent = state["intent"]
    if intent == "visualization":
        return "visualization_lane"
    elif intent == "analysis":
        return "analysis_lane"
    elif intent == "audit":
        return "audit_lane"
    else:
        return END

# LangGraph State Machine
workflow = StateGraph(BIState)

# Nodes (python functions)
workflow.add_node("planner", generate_plan)
workflow.add_node("visualization_lane", visualization_lane)
workflow.add_node("analysis_lane", analysis_lane)
workflow.add_node("audit_lane", audit_lane)


workflow.set_entry_point("planner")

# Conditional edges (the router)
workflow.add_conditional_edges(
    "planner",
    route_intent,
    {
        "visualization_lane": "visualization_lane",
        "analysis_lane": "analysis_lane",
        "audit_lane": "audit_lane",
    }
)

# Every lane currently just ends the graph after execution
workflow.add_edge("visualization_lane", END)
workflow.add_edge("analysis_lane", END)
workflow.add_edge("audit_lane", END)

master_agent = workflow.compile()

if __name__ == "__main__":

    test_query = "Create a pie chart of expenses in March for travel, infrastructure, salaries and food & beverage."
    
    print("Booting BI Assistant...\n" + "="*50)
    
    # Run the graph
    final_state = master_agent.invoke({
        "query": test_query,
        "intent": "",
        "execution_plan": [],
        "raw_data": {},
        "final_output": ""
    })
    
    print("=" * 50)
    print(f"Final Output: {final_state['final_output']}")