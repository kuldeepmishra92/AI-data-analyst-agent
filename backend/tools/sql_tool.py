import sqlite3
from typing import Dict, Any, List
from backend.database import get_db_connection, run_query

def get_database_schema() -> Dict[str, List[Dict[str, str]]]:
    """
    Query the SQLite system tables to extract the schema of all active user tables.
    Returns:
        A dictionary mapping table names to list of columns with their data types.
        Example: {"data_sales": [{"name": "city", "type": "TEXT"}, ...]}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all table names, excluding system tables and analysis history
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'analysis_history'
        """)
        tables = [row["name"] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema[table] = [
                {"name": col["name"], "type": col["type"]}
                for col in columns
            ]
        return schema
    except Exception as e:
        raise Exception(f"Failed to fetch schema: {str(e)}")
    finally:
        conn.close()

def format_sql_result_for_llm(result: Dict[str, Any]) -> str:
    """Format query results in Markdown table format for LLM context."""
    if not result["rows"]:
        return "No rows returned."
        
    cols = result["columns"]
    rows = result["rows"]
    
    markdown_lines = []
    # Header
    markdown_lines.append("| " + " | ".join(cols) + " |")
    markdown_lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
    # Rows
    for row in rows[:50]:  # Limit to 50 rows for LLM safety
        str_row = [str(val) if val is not None else "NULL" for val in row]
        markdown_lines.append("| " + " | ".join(str_row) + " |")
        
    if len(rows) > 50:
        markdown_lines.append(f"\n*(Truncated: showing first 50 of {len(rows)} records)*")
        
    return "\n".join(markdown_lines)
