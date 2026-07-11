import os
import json
import pandas as pd
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from backend.agents.llm import get_llm
from backend.tools.chart_tool import generate_and_save_chart

class ChartRecommendation(BaseModel):
    chart_type: str = Field(description="The type of chart: 'bar', 'line', 'pie', or 'histogram'")
    x_col: str = Field(description="Column name for the X axis (or names for pie chart)")
    y_col: str = Field(default="", description="Column name for the Y axis (or values for pie chart, leave empty string for histogram)")
    title: str = Field(description="Short descriptive title for the chart")
    filename: str = Field(description="Filename ending in .png, e.g., sales_by_region_bar.png")

class VisualizationPlan(BaseModel):
    charts: List[ChartRecommendation] = Field(description="List of recommended chart configurations (ideally 1 bar, 1 line, 1 pie, and 1 histogram)")

class VisualizationAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        
    def plan_and_generate_charts(self, df: pd.DataFrame, profile: Dict[str, Any], table_name: str) -> List[str]:
        """
        Ask Gemini to recommend 4 appropriate charts (bar, line, pie, histogram),
        then generate and save them. Returns a list of paths to the saved PNGs.
        """
        # Build prompt context with column names and types
        columns_summary = []
        for col in profile.get("columns", []):
            columns_summary.append(
                f"- Name: {col['name']}, Type: {col['type']}, Unique Values: {col['unique_count']}"
            )
        columns_text = "\n".join(columns_summary)
        
        prompt = f"""
You are an expert Data Visualizer. Your task is to recommend exactly 4 distinct charts for the dataset table '{table_name}':
1. One 'bar' chart (e.g., comparing numerical values across categories)
2. One 'line' chart (e.g., tracking a metric over time or a sequence)
3. One 'pie' chart (e.g., breakdown of a total by categories with low cardinality, e.g., < 10 categories)
4. One 'histogram' chart (e.g., distribution of a single numerical column)

Here are the details of the dataset columns:
Shape: {profile.get('total_rows')} rows, {profile.get('total_columns')} columns
Columns:
{columns_text}

Guidelines:
- Choose columns that actually exist.
- For 'histogram', leave 'y_col' as an empty string.
- For 'pie' chart, use a categorical column for 'x_col' (representing names) and a numeric column for 'y_col' (representing values).
- For 'line' chart, try to find a date, time, or ordered column for 'x_col'.
- Output file names should be sanitized (using underscores instead of spaces) and end with '.png'.

Return the response in JSON format matching the schema:
{{
  "charts": [
    {{
      "chart_type": "bar" | "line" | "pie" | "histogram",
      "x_col": "column_name",
      "y_col": "column_name_or_empty_string",
      "title": "Descriptive Chart Title",
      "filename": "chart_name.png"
    }}
  ]
}}
"""
        saved_paths = []
        try:
            # We can use LLM's structured output or direct prompt formatting
            structured_llm = self.llm.with_structured_output(VisualizationPlan)
            plan = structured_llm.invoke(prompt)
            
            # If kaleido or plotly generation fails for a specific chart, we catch it and continue
            for recommendation in plan.charts:
                try:
                    x = recommendation.x_col
                    y = recommendation.y_col if recommendation.y_col != "" else None
                    chart_type = recommendation.chart_type
                    title = recommendation.title
                    # Prepend table name to filename to avoid overwrites for multi-file imports
                    filename = f"{table_name}_{recommendation.filename}"
                    
                    # Generate and save chart
                    path = generate_and_save_chart(
                        df=df,
                        chart_type=chart_type,
                        x_col=x,
                        y_col=y,
                        title=title,
                        filename=filename
                    )
                    saved_paths.append(path)
                except Exception as e:
                    print(f"Error generating recommended chart ({recommendation.chart_type}): {str(e)}")
                    
        except Exception as e:
            print(f"Failed to plan visualization using LLM: {str(e)}")
            # Fallback - programmatically generate default charts if LLM fails
            saved_paths = self._generate_fallback_charts(df, profile, table_name)
            
        return saved_paths

    def _generate_fallback_charts(self, df: pd.DataFrame, profile: Dict[str, Any], table_name: str) -> List[str]:
        """Programmatic fallback if the AI model planning fails."""
        saved_paths = []
        numeric_cols = [col["name"] for col in profile.get("columns", []) if "int" in col["type"] or "float" in col["type"]]
        categorical_cols = [col["name"] for col in profile.get("columns", []) if "object" in col["type"] or "category" in col["type"]]
        date_cols = [col["name"] for col in profile.get("columns", []) if "datetime" in col["type"]]
        
        # 1. Fallback Histogram
        if numeric_cols:
            try:
                p = generate_and_save_chart(df, "histogram", numeric_cols[0], title=f"Distribution of {numeric_cols[0]}", filename=f"{table_name}_fallback_hist.png")
                saved_paths.append(p)
            except Exception:
                pass
                
        # 2. Fallback Bar Chart
        if categorical_cols and numeric_cols:
            try:
                # Group by categorical, aggregate first numeric
                summary_df = df.groupby(categorical_cols[0])[numeric_cols[0]].mean().reset_index().head(10)
                p = generate_and_save_chart(summary_df, "bar", categorical_cols[0], numeric_cols[0], title=f"Avg {numeric_cols[0]} by {categorical_cols[0]}", filename=f"{table_name}_fallback_bar.png")
                saved_paths.append(p)
            except Exception:
                pass

        # 3. Fallback Pie Chart
        if categorical_cols and numeric_cols:
            try:
                summary_df = df.groupby(categorical_cols[0])[numeric_cols[0]].sum().reset_index().head(5)
                p = generate_and_save_chart(summary_df, "pie", categorical_cols[0], numeric_cols[0], title=f"Breakdown of {numeric_cols[0]} by {categorical_cols[0]}", filename=f"{table_name}_fallback_pie.png")
                saved_paths.append(p)
            except Exception:
                pass

        # 4. Fallback Line Chart
        if date_cols and numeric_cols:
            try:
                summary_df = df.groupby(date_cols[0])[numeric_cols[0]].mean().reset_index().sort_values(by=date_cols[0])
                p = generate_and_save_chart(summary_df, "line", date_cols[0], numeric_cols[0], title=f"{numeric_cols[0]} Trend Over Time", filename=f"{table_name}_fallback_line.png")
                saved_paths.append(p)
            except Exception:
                pass
                
        return saved_paths
