import sqlite3
import pandas as pd
from datetime import datetime
from backend.config import DATABASE_PATH

def get_db_connection():
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create analysis history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_time TEXT NOT NULL,
            rows INTEGER NOT NULL,
            columns INTEGER NOT NULL,
            missing_values INTEGER NOT NULL,
            duplicates INTEGER NOT NULL,
            report_path TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def save_analysis_history(filename: str, rows: int, cols: int, missing: int, duplicates: int, report_path: str):
    """Save metadata of a completed analysis run to history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO analysis_history (filename, upload_time, rows, columns, missing_values, duplicates, report_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (filename, upload_time, rows, cols, missing, duplicates, report_path))
    
    conn.commit()
    conn.close()

def get_analysis_history():
    """Retrieve previous analysis history entries ordered by date desc."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, filename, upload_time, rows, columns, missing_values, duplicates, report_path 
        FROM analysis_history 
        ORDER BY id DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def save_df_to_db(df: pd.DataFrame, table_name: str):
    """Store the cleaned DataFrame as a dynamic SQL table for querying."""
    conn = get_db_connection()
    try:
        # Save DataFrame to table; replace if exists
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    finally:
        conn.close()

def run_query(query: str):
    """Run an arbitrary SQL query and return columns and records."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn)
        return {
            "columns": list(df.columns),
            "rows": df.values.tolist(),
            "count": len(df)
        }
    except Exception as e:
        raise Exception(f"SQL execution error: {str(e)}")
    finally:
        conn.close()
