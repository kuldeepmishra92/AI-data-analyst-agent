from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.agents.llm import get_llm

class KPIDescription(BaseModel):
    name: str = Field(description="Name of the KPI, e.g., Total Revenue")
    description: str = Field(description="What this KPI measures")
    formula: str = Field(description="Suggested DAX formula or column aggregation, e.g., SUM(sales_revenue)")

class VisualDescription(BaseModel):
    title: str = Field(description="Title of the visual")
    type: str = Field(description="Power BI visual type, e.g., Stacked Bar Chart, Line Chart, KPI Card, Treemap")
    description: str = Field(description="Column mappings for Axes, Legend, Values, and what the visual reveals")

class FilterDescription(BaseModel):
    column: str = Field(description="Column name to use for slicer/filter")
    reason: str = Field(description="Why this column is highly relevant for interactive analysis")

class PowerBIDashboardRecommendation(BaseModel):
    kpis: List[KPIDescription] = Field(description="Key metrics cards at the top of the dashboard")
    visuals: List[VisualDescription] = Field(description="Main charts and grids on the dashboard canvas")
    filters: List[FilterDescription] = Field(description="Interactive slicers and page filters")
    layout_description: str = Field(description="Overview advice on layout, color themes, tabs, and UX design")

class DashboardAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        
    def recommend_dashboard(self, profile: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """
        Synthesize dashboard layout and visualization recommendations
        specifically tailored to the columns and data types in the Excel file.
        """
        # Build prompt context with column details
        columns_text = []
        for col in profile.get("columns", []):
            columns_text.append(
                f"- Name: {col['name']}, Type: {col['type']}, Unique Values: {col['unique_count']}"
            )
        columns_summary = "\n".join(columns_text)
        
        prompt = f"""
You are an expert Power BI Solutions Architect and Dashboard Designer.
Recommend an interactive corporate Power BI dashboard layout based on the structure of the dataset '{filename}':

Dataset Metadata: {profile.get('total_rows')} rows, {profile.get('total_columns')} columns
Columns and Types:
{columns_summary}

Provide:
1. Recommended KPIs: 3-4 high-level KPI cards to place at the top of the canvas (include names, purposes, and simple DAX expressions).
2. Suggested Charts: 4-5 visual representations (e.g., column charts, matrix tables, scatter plots) specifying exactly what columns to assign to Axis, Legend, and Values.
3. Suggested Filters/Slicers: 2-3 interactive filter fields that would allow users to slice-and-dice data (e.g., regions, dates, statuses).
4. Layout and UX Flow: Design instructions (e.g., grid system, theme colors, navigation flow).

Return the response in JSON format matching the schema:
{{
  "kpis": [
    {{ "name": "KPI Card Name", "description": "What it tracks", "formula": "DAX Formula" }}
  ],
  "visuals": [
    {{ "title": "Chart Title", "type": "Stacked Bar Chart", "description": "Mapping columns and purpose" }}
  ],
  "filters": [
    {{ "column": "column_name", "reason": "Why it's useful to filter by this" }}
  ],
  "layout_description": "General layout advice"
}}
"""
        try:
            structured_llm = self.llm.with_structured_output(PowerBIDashboardRecommendation)
            rec = structured_llm.invoke(prompt)
            return {
                "kpis": [dict(kpi) for kpi in rec.kpis],
                "visuals": [dict(v) for v in rec.visuals],
                "filters": [dict(f) for f in rec.filters],
                "layout_description": rec.layout_description
            }
        except Exception as e:
            print(f"Failed to generate dashboard recommendations using LLM: {str(e)}")
            return {
                "kpis": [
                    {"name": "Total Records Count", "description": "Total records uploaded", "formula": "COUNTROWS('Table')"}
                ],
                "visuals": [
                    {"title": "Overview Table Grid", "type": "Table", "description": "Simple grid list of the raw dataset columns"}
                ],
                "filters": [
                    {"column": "No Slicers", "reason": "Default fallback config"}
                ],
                "layout_description": "Clean grid, standard Power BI light corporate theme."
            }
