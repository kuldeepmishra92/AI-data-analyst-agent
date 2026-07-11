import os
import plotly.express as px
import pandas as pd
from typing import Dict, Any, Optional
from backend.config import CHART_DIR

# Set Plotly template for premium professional looks
# Plotly's default theme is okay, but we can set a clean custom layout style.
THEME_COLOR_SEQUENCE = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

def generate_and_save_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: Optional[str] = None,
    title: str = "Chart",
    filename: str = "chart.png"
) -> str:
    """
    Generate a Plotly chart and save it as a PNG image.
    Returns the absolute path to the saved image.
    """
    os.makedirs(CHART_DIR, exist_ok=True)
    chart_path = os.path.join(CHART_DIR, filename)
    
    chart_type = chart_type.lower()
    
    # Ensure columns exist in DataFrame
    if x_col not in df.columns:
        raise ValueError(f"Column '{x_col}' does not exist in the DataFrame")
    if y_col and y_col not in df.columns:
        raise ValueError(f"Column '{y_col}' does not exist in the DataFrame")

    fig = None
    
    if chart_type == "bar":
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col, 
            title=title, 
            color_discrete_sequence=THEME_COLOR_SEQUENCE
        )
    elif chart_type == "line":
        fig = px.line(
            df, 
            x=x_col, 
            y=y_col, 
            title=title, 
            color_discrete_sequence=THEME_COLOR_SEQUENCE
        )
    elif chart_type == "pie":
        # For pie chart, y_col represents values, x_col represents names
        fig = px.pie(
            df, 
            names=x_col, 
            values=y_col, 
            title=title, 
            color_discrete_sequence=THEME_COLOR_SEQUENCE
        )
    elif chart_type == "histogram":
        fig = px.histogram(
            df, 
            x=x_col, 
            title=title, 
            color_discrete_sequence=THEME_COLOR_SEQUENCE
        )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
        
    # Styling for professional corporate look (clean margins, grid colors, font styling)
    fig.update_layout(
        font=dict(family="Inter, Outfit, sans-serif", size=12, color="#1E293B"),
        title=dict(font=dict(size=16, color="#0F172A", weight="bold")),
        plot_bgcolor="#F8FAFC",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(gridcolor="#E2E8F0", showline=True, linecolor="#CBD5E1"),
        yaxis=dict(gridcolor="#E2E8F0", showline=True, linecolor="#CBD5E1")
    )
    
    # Save as PNG
    fig.write_image(chart_path, engine="kaleido", width=800, height=500, scale=2)
    return chart_path
