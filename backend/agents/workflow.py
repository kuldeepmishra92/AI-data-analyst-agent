import os
import pandas as pd
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END

# Import agents and database helpers
from backend.agents.cleaning_agent import CleaningAgent
from backend.agents.profiling_agent import ProfilingAgent
from backend.agents.visualization_agent import VisualizationAgent
from backend.agents.sql_agent import SQLAgent
from backend.agents.insight_agent import InsightAgent
from backend.agents.dashboard_agent import DashboardAgent
from backend.agents.report_agent import ReportAgent

from backend.database import save_df_to_db, save_analysis_history
from backend.tools.excel_tool import read_excel_file, sanitize_sheet_name

# Define the State of our Analysis Pipeline
class AnalysisState(TypedDict):
    file_path: str
    filename: str
    table_name: str
    sheets_found: List[str]
    # Intermediate & Output artifacts
    cleaning_summary: Dict[str, Any]
    profile_summary: Dict[str, Any]
    charts_list: List[str]
    default_queries: List[Dict[str, str]]
    insights: Dict[str, Any]
    dashboard_recommendations: Dict[str, Any]
    report_path: str

# 1. Clean Data Node
def clean_data_node(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- CLEANING DATA: {state['filename']} ---")
    sheets = read_excel_file(state['file_path'])
    
    # We will process the first sheet for the analytical pipeline
    first_sheet_name = list(sheets.keys())[0]
    df = sheets[first_sheet_name]
    
    cleaner = CleaningAgent()
    cleaned_df, cleaning_summary = cleaner.clean_sheet(df)
    
    # Sanitize sheet name for SQL table storage
    table_name = f"data_{sanitize_sheet_name(state['filename'].split('.')[0])}"
    
    # Save cleaned dataframe to SQLite
    save_df_to_db(cleaned_df, table_name)
    
    return {
        "table_name": table_name,
        "cleaning_summary": cleaning_summary,
        "sheets_found": list(sheets.keys())
    }

# 2. Profile Data Node
def profile_data_node(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- PROFILING DATA: {state['table_name']} ---")
    # Read the cleaned data from database to ensure consistency
    from backend.database import run_query
    conn_result = run_query(f"SELECT * FROM {state['table_name']}")
    df = pd.DataFrame(conn_result["rows"], columns=conn_result["columns"])
    
    profiler = ProfilingAgent()
    profile_summary = profiler.profile_sheet(df)
    
    return {
        "profile_summary": profile_summary
    }

# 3. Visualize Data Node
def visualize_data_node(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- GENERATING VISUALIZATIONS ---")
    from backend.database import run_query
    conn_result = run_query(f"SELECT * FROM {state['table_name']}")
    df = pd.DataFrame(conn_result["rows"], columns=conn_result["columns"])
    
    visualizer = VisualizationAgent()
    charts_list = visualizer.plan_and_generate_charts(
        df=df,
        profile=state["profile_summary"],
        table_name=state["table_name"]
    )
    
    return {
        "charts_list": charts_list
    }

# 4. SQL Generator Node
def sql_generator_node(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- GENERATING SQL QUERY SUGGESTIONS ---")
    sql_agent = SQLAgent()
    default_queries = sql_agent.generate_default_queries(state["table_name"])
    
    return {
        "default_queries": default_queries
    }

# 5. Insight Extractor Node
def insight_extractor_node(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- EXTRACTING BUSINESS INSIGHTS ---")
    insight_agent = InsightAgent()
    insights = insight_agent.generate_insights(
        profile=state["profile_summary"],
        cleaning_summary=state["cleaning_summary"],
        filename=state["filename"]
    )
    return {
        "insights": insights
    }

# 6. Dashboard Recommender Node
def dashboard_recommender_node(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- GENERATING POWER BI RECOMMENDATIONS ---")
    dashboard_agent = DashboardAgent()
    recs = dashboard_agent.recommend_dashboard(
        profile=state["profile_summary"],
        filename=state["filename"]
    )
    return {
        "dashboard_recommendations": recs
    }

# 7. Report Writer Node
def report_writer_node(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- WRITING MARKDOWN REPORT ---")
    report_agent = ReportAgent()
    report_path = report_agent.generate_and_save_report(
        filename=state["filename"],
        cleaning_summary=state["cleaning_summary"],
        profile_summary=state["profile_summary"],
        sql_queries=state["default_queries"],
        insights=state["insights"],
        dashboard_recommendations=state["dashboard_recommendations"],
        charts_list=state["charts_list"]
    )
    
    # Save the run in SQLite history table
    save_analysis_history(
        filename=state["filename"],
        rows=state["profile_summary"].get("total_rows", 0),
        cols=state["profile_summary"].get("total_columns", 0),
        missing=state["profile_summary"].get("missing_values_count", 0),
        duplicates=state["profile_summary"].get("duplicate_count", 0),
        report_path=report_path
    )
    
    return {
        "report_path": report_path
    }

# Build LangGraph workflow
def build_workflow() -> StateGraph:
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("clean", clean_data_node)
    workflow.add_node("profile", profile_data_node)
    workflow.add_node("visualize", visualize_data_node)
    workflow.add_node("sql", sql_generator_node)
    workflow.add_node("insight", insight_extractor_node)
    workflow.add_node("dashboard", dashboard_recommender_node)
    workflow.add_node("report", report_writer_node)
    
    # Setup execution edges
    workflow.set_entry_point("clean")
    workflow.add_edge("clean", "profile")
    workflow.add_edge("profile", "visualize")
    workflow.add_edge("visualize", "sql")
    workflow.add_edge("sql", "insight")
    workflow.add_edge("insight", "dashboard")
    workflow.add_edge("dashboard", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()

def run_analysis_pipeline(file_path: str, filename: str) -> Dict[str, Any]:
    """Execute the full data analysis pipeline end to end."""
    app_graph = build_workflow()
    initial_state = {
        "file_path": file_path,
        "filename": filename,
        "table_name": "",
        "sheets_found": [],
        "cleaning_summary": {},
        "profile_summary": {},
        "charts_list": [],
        "default_queries": [],
        "insights": {},
        "dashboard_recommendations": {},
        "report_path": ""
    }
    # Invoke LangGraph
    final_output = app_graph.invoke(initial_state)
    return final_output
