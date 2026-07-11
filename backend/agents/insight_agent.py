from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.agents.llm import get_llm

class BusinessInsights(BaseModel):
    key_observations: List[str] = Field(
        description="Key trends, highest/lowest performing categories, revenue or quantity developments found in the data"
    )
    data_quality_notes: List[str] = Field(
        description="Observations regarding missing values, clean up actions, duplicate rows, data type distributions or inconsistencies"
    )
    recommendations: List[str] = Field(
        description="Actionable business strategy recommendations based on the insights in the dataset"
    )

class InsightAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        
    def generate_insights(self, profile: Dict[str, Any], cleaning_summary: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """
        Takes profiling metrics and cleaning actions, and asks Gemini
        to extract business insights and quality diagnostics.
        """
        # Build prompt context
        columns_text = []
        for col in profile.get("columns", []):
            stats = col.get("statistics", {})
            stats_str = ", ".join([f"{k}: {v}" for k, v in stats.items()])
            columns_text.append(
                f"- Column '{col['name']}' ({col['type']}): Uniques: {col['unique_count']}, Missing: {col['null_count']}, Stats: {{{stats_str}}}"
            )
        columns_summary = "\n".join(columns_text)
        
        cleaning_actions = "\n".join([f"- {a}" for a in cleaning_summary.get("actions_taken", [])])
        if not cleaning_actions:
            cleaning_actions = "- No major cleaning actions taken."
            
        prompt = f"""
You are an expert Business Intelligence Analyst and Data Strategist.
Analyze the profiling results and data cleaning steps for the uploaded dataset '{filename}':

Dataset Shape: {profile.get('total_rows')} rows, {profile.get('total_columns')} columns
Data Cleaning Actions Performed:
{cleaning_actions}

Column Summaries & Statistics:
{columns_summary}

Based on this structural profile, write:
1. Key Observations: Highlight highest performing categories, patterns, trends, outliers, or notable values.
2. Data Quality Notes: Comment on the cleanliness of the data, integrity, any missing values or duplicates, and what that means for reliability.
3. Business Recommendations: Provide 3-4 highly actionable, strategic business suggestions based on what the numbers show.

Return the response in JSON format matching the schema:
{{
  "key_observations": ["Observation 1", "Observation 2", ...],
  "data_quality_notes": ["Note 1", "Note 2", ...],
  "recommendations": ["Recommendation 1", "Recommendation 2", ...]
}}
"""
        try:
            structured_llm = self.llm.with_structured_output(BusinessInsights)
            insights = structured_llm.invoke(prompt)
            return {
                "key_observations": insights.key_observations,
                "data_quality_notes": insights.data_quality_notes,
                "recommendations": insights.recommendations
            }
        except Exception as e:
            print(f"Failed to generate insights using LLM: {str(e)}")
            return {
                "key_observations": ["Could not calculate insights due to AI extraction failure."],
                "data_quality_notes": [f"Analysis pipeline encountered an error: {str(e)}"],
                "recommendations": ["Verify your GEMINI_API_KEY config or try standardizing your columns manually."]
            }
Definition: "Create backend/agents/insight_agent.py to extract business observations."
