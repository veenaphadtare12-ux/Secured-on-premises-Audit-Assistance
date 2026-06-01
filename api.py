from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from master_agent import master_agent, BIState
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI(title="Local BI Assistant API")

# Mounting the audit_files directory so the frontend can fetch the generated charts
app.mount("/files", StaticFiles(directory="audit_files"), name="files")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defining the data structure the frontend will send
class QueryRequest(BaseModel):
    query: str

# Defining the data structure the API will return
class QueryResponse(BaseModel):
    intent: str
    text_output: str
    image_url: str | None = None

@app.post("/ask", response_model=QueryResponse)
async def ask_assistant(request: QueryRequest):
    print(f"Received query from UI: {request.query}")
    
    try:
        # 1. Feed the query into the LangGraph orchestrator
        final_state = master_agent.invoke({
            "query": request.query,
            "intent": "",
            "execution_plan": [],
            "raw_data": {},
            "final_output": ""
        })
        
        intent = final_state.get("intent", "unknown")
        output_text = final_state.get("final_output", "No output generated.")
        image_url = None
        
        # 2. Passing the generated chart path to the frontend
        if intent == "visualization":
            chart_path = "audit_files/generated_chart.png"
            if os.path.exists(chart_path):
                image_url = os.path.abspath(chart_path)
                
        return QueryResponse(
            intent=intent,
            text_output=output_text,
            image_url=image_url
        )
        
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Booting Local API Daemon on port 8123...")
    uvicorn.run(app, host="127.0.0.1", port=8123)