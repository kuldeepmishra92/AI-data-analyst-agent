import os
from typing import Dict, Any, List
from backend.tools.report_tool import build_markdown_report, save_markdown_report

class ReportAgent:
    def __init__(self):
        pass
        
    def generate_and_save_report(
        self,
        filename: str,
        cleaning_summary: Dict[str, Any],
        profile_summary: Dict[str, Any],
        sql_queries: List[Dict[str, str]],
        insights: Dict[str, Any],
        dashboard_recommendations: Dict[str, Any],
        charts_list: List[str]
    ) -> str:
        """
        Compiles the results from all agent steps into a structured Markdown document,
        writes it to the reports folder, and returns the absolute file path.
        """
        report_content = build_markdown_report(
            filename=filename,
            cleaning_summary=cleaning_summary,
            profile_summary=profile_summary,
            sql_queries=sql_queries,
            insights=insights,
            dashboard_recommendations=dashboard_recommendations,
            charts_list=charts_list
        )
        
        # Set report name, replacing space with underscore
        base_name = os.path.splitext(filename)[0]
        report_name = f"{base_name}_report.md".replace(" ", "_")
        
        report_path = save_markdown_report(report_content, report_name)
        return report_path
