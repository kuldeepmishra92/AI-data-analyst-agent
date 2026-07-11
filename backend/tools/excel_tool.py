import os
import pandas as pd
from typing import Dict, List, Any

def read_excel_file(file_path: str) -> Dict[str, pd.DataFrame]:
    """
    Read an Excel or CSV file and return a dictionary of DataFrames,
    where keys are sheet names and values are the sheets as DataFrames.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.endswith('.csv'):
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            return {"csv_data": df}
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")
            
    if not file_path.endswith('.xlsx'):
        raise ValueError("Unsupported file format. Only .xlsx and .csv files are allowed.")
    
    try:
        # Load all sheets as DataFrames
        excel_file = pd.ExcelFile(file_path)
        sheets = {}
        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name)
            sheets[sheet_name] = df
        return sheets
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {str(e)}")

def get_excel_metadata(file_path: str) -> Dict[str, Any]:
    """Get metadata about the Excel/CSV file like size, sheets, etc."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    stats = os.stat(file_path)
    
    if file_path.endswith('.csv'):
        return {
            "file_name": os.path.basename(file_path),
            "file_size_bytes": stats.st_size,
            "sheet_names": ["csv_data"],
            "sheets_count": 1
        }
        
    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
    except Exception:
        sheet_names = []
        
    return {
        "file_name": os.path.basename(file_path),
        "file_size_bytes": stats.st_size,
        "sheet_names": sheet_names,
        "sheets_count": len(sheet_names)
    }

def sanitize_sheet_name(name: str) -> str:
    """Sanitize sheet name to make it suitable for a SQL table name."""
    sanitized = "".join(c if c.isalnum() else "_" for c in name)
    # Ensure it starts with a letter or underscore
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized.lower()
