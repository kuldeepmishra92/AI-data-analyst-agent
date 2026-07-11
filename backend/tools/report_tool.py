import os
import datetime
from typing import Dict, Any, List
from backend.config import REPORT_DIR

def build_markdown_report(
    filename: str,
    cleaning_summary: Dict[str, Any],
    profile_summary: Dict[str, Any],
    sql_queries: List[Dict[str, str]],
    insights: Dict[str, Any],
    dashboard_recommendations: Dict[str, Any],
    charts_list: List[str]
) -> str:
    """
    Builds a markdown structure representing the analysis report
    and returns the final Markdown content.
    """
    # Build sections
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Title Header
    md = []
    md.append(f"# AI Data Analysis Report: {filename}")
    md.append(f"**Generated On:** {now}")
    md.append("\n---")
    
    # 2. Dataset Overview
    md.append("## 📊 Dataset Overview")
    md.append(f"- **Filename:** {filename}")
    md.append(f"- **Total Rows (Cleaned):** {profile_summary.get('total_rows', 0)}")
    md.append(f"- **Total Columns:** {profile_summary.get('total_columns', 0)}")
    md.append(f"- **Duplicate Records Found:** {profile_summary.get('duplicate_count', 0)}")
    md.append(f"- **Total Missing Values:** {profile_summary.get('missing_values_count', 0)}")
    md.append("\n")

    # 3. Cleaning Summary
    md.append("## 🧹 Data Cleaning Summary")
    clean_actions = cleaning_summary.get("actions_taken", [])
    if clean_actions:
        for action in clean_actions:
            md.append(f"- {action}")
    else:
        md.append("- No cleaning actions required. Dataset was pristine.")
    md.append("\n")

    # 4. Profiling Summary
    md.append("## 📈 Data Profiling Summary")
    md.append("### Columns and Data Types")
    md.append("| Column Name | Data Type | Non-Null Count | Nulls | Unique Values |")
    md.append("| --- | --- | --- | --- | --- |")
    for col_info in profile_summary.get("columns", []):
        md.append(
            f"| {col_info['name']} | {col_info['type']} | {col_info['non_null_count']} | "
            f"{col_info['null_count']} | {col_info['unique_count']} |"
        )
    md.append("\n")
    
    # 5. Visualizations Section
    if charts_list:
        md.append("## 🖼️ Generated Charts")
        md.append("Visual patterns identified in the dataset:")
        for chart in charts_list:
            chart_filename = os.path.basename(chart)
            # Standard markdown image embed pointing relative to the reports dir or backend/charts.
            # In the API we will serve charts statically so the report preview can display them.
            md.append(f"### {chart_filename.split('.')[0].replace('_', ' ').title()}")
            # Use absolute path to the local chart image for standalone render or custom route
            md.append(f"![{chart_filename}](../charts/{chart_filename})")
            md.append("\n")
            
    # 6. SQL Queries
    if sql_queries:
        md.append("## 💻 Automatically Generated SQL Queries")
        md.append("The following SQL scripts were synthesized to query the dataset:")
        for query_info in sql_queries:
            title = query_info.get("title", "Query")
            query = query_info.get("query", "")
            md.append(f"### {title}")
            md.append(f"```sql\n{query}\n```")
            md.append("\n")
            
    # 7. Business Insights
    md.append("## 💡 Business Insights & Recommendations")
    
    # Insights bullet sections
    md.append("### Key Observations")
    key_obs = insights.get("key_observations", [])
    if isinstance(key_obs, list):
        for obs in key_obs:
            md.append(f"- {obs}")
    else:
        md.append(str(key_obs))
    md.append("\n")
    
    md.append("### Actionable Business Recommendations")
    recs = insights.get("recommendations", [])
    if isinstance(recs, list):
        for rec in recs:
            md.append(f"- {rec}")
    else:
        md.append(str(recs))
    md.append("\n")

    # 8. Dashboard Recommendations
    md.append("## 🖥️ Power BI Dashboard Recommendations")
    db_rec = dashboard_recommendations
    
    md.append("### Recommended KPIs")
    kpis = db_rec.get("kpis", [])
    for kpi in kpis:
        md.append(f"- **{kpi.get('name', 'KPI')}:** {kpi.get('description', '')} (Measure: `{kpi.get('formula', '')}`)")
    md.append("\n")
    
    md.append("### Suggested Visualizations")
    visuals = db_rec.get("visuals", [])
    for visual in visuals:
        md.append(f"- **{visual.get('title', 'Visual')}:** {visual.get('description', '')} (Type: {visual.get('type', '')})")
    md.append("\n")
    
    md.append("### Suggested Filters & Slicers")
    filters = db_rec.get("filters", [])
    for flt in filters:
        md.append(f"- **{flt.get('column', 'Column')}:** {flt.get('reason', '')}")
    md.append("\n")

    return "\n".join(md)

def save_markdown_report(report_md: str, filename: str) -> str:
    """Save the markdown report to the reports directory."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_filepath = os.path.join(REPORT_DIR, filename)
    with open(report_filepath, "w", encoding="utf-8") as f:
        f.write(report_md)
    return report_filepath
