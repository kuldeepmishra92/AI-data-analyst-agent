import os
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.config import UPLOAD_DIR, CHART_DIR, REPORT_DIR, HOST, PORT
from backend.database import init_db, get_analysis_history
from backend.agents.upload_agent import UploadAgent
from backend.agents.workflow import run_analysis_pipeline
from backend.agents.sql_agent import SQLAgent
from backend.tools.sql_tool import get_database_schema

# Initialize DB on server start
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="AI Data Analyst Agent API",
    description="Backend service for processing and analyzing Excel data with LangGraph agents.",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve generated charts
os.makedirs(CHART_DIR, exist_ok=True)
app.mount("/charts", StaticFiles(directory=str(CHART_DIR)), name="charts")

# Input models
class AnalyzeRequest(BaseModel):
    filename: str

class AskRequest(BaseModel):
    question: str

# Endpoints
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload one or multiple Excel files."""
    agent = UploadAgent()
    results = await agent.process_uploads(files)
    
    # Check if any file uploaded successfully
    success = any(r["success"] for r in results)
    if not success:
        return JSONResponse(status_code=400, content={"message": "No valid files were uploaded.", "results": results})
        
    return {"message": "Files uploaded successfully", "results": results}

@app.post("/analyze")
async def analyze_file(request: AnalyzeRequest):
    """Run the complete agentic analysis pipeline on an uploaded file."""
    filename = request.filename
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in uploads folder.")
        
    try:
        # Run LangGraph pipeline
        result = run_analysis_pipeline(file_path, filename)
        
        # Prepare client response (remove full paths for security/cleanliness)
        client_response = {
            "filename": result["filename"],
            "table_name": result["table_name"],
            "sheets_found": result["sheets_found"],
            "cleaning_summary": result["cleaning_summary"],
            "profile_summary": result["profile_summary"],
            "default_queries": result["default_queries"],
            # Return relative charts urls so the frontend can easily load them
            "charts": [f"/charts/{os.path.basename(c)}" for c in result["charts_list"]],
            "insights": result["insights"],
            "dashboard_recommendations": result["dashboard_recommendations"],
            "report_path": result["report_path"]
        }
        return client_response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.post("/ask")
async def ask_question(request: AskRequest):
    """Ask natural language questions about the uploaded dataset."""
    schema = get_database_schema()
    if not schema:
        raise HTTPException(
            status_code=400, 
            detail="No analyzed tables found in the database. Please analyze a dataset first."
        )
        
    try:
        agent = SQLAgent()
        result = agent.answer_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@app.get("/history")
async def get_history():
    """Return previous analysis history metadata."""
    try:
        history = get_analysis_history()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@app.get("/download-report")
async def download_report(path: str = Query(..., description="Absolute path of the markdown report")):
    """Download the generated Markdown report."""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report file not found.")
    
    filename = os.path.basename(path)
    return FileResponse(path, media_type="text/markdown", filename=filename)

# Mount frontend files at the root
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"Warning: Frontend directory '{FRONTEND_DIR}' not found. Serving API routes only.")
