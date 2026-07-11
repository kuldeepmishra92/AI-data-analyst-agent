import os
from typing import List, Dict, Any
from fastapi import UploadFile
from backend.config import UPLOAD_DIR
from backend.tools.excel_tool import get_excel_metadata

class UploadAgent:
    def __init__(self):
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
    async def process_uploads(self, upload_files: List[UploadFile]) -> List[Dict[str, Any]]:
        """
        Processes and validates uploaded files, saves them, and returns metadata.
        """
        results = []
        
        for file in upload_files:
            if not file.filename:
                continue
                
            filename = file.filename
            
            # 1. Format validation
            if not (filename.endswith('.xlsx') or filename.endswith('.csv')):
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": "Unsupported file format. Only Excel (.xlsx) and CSV (.csv) files are allowed."
                })
                continue
                
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            try:
                # Save the file
                content = await file.read()
                if len(content) == 0:
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": "The uploaded file is empty."
                    })
                    continue
                    
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # Retrieve sheets and file details using metadata tool
                metadata = get_excel_metadata(file_path)
                
                # Extract first sheet preview
                import pandas as pd
                import numpy as np
                preview_data = {"columns": [], "rows": []}
                if metadata["sheet_names"]:
                    if file_path.endswith('.csv'):
                        df_preview = pd.read_csv(file_path).head(10)
                    else:
                        df_preview = pd.read_excel(file_path, sheet_name=metadata["sheet_names"][0]).head(10)
                    df_preview = df_preview.replace({pd.NA: None, np.nan: None})
                    preview_data = {
                        "columns": [str(c) for c in df_preview.columns],
                        "rows": [[str(x) if x is not None else "" for x in row] for row in df_preview.values.tolist()]
                    }
                
                results.append({
                    "filename": filename,
                    "success": True,
                    "file_path": file_path,
                    "file_size": metadata["file_size_bytes"],
                    "sheets": metadata["sheet_names"],
                    "sheets_count": metadata["sheets_count"],
                    "preview": preview_data
                })
                
            except Exception as e:
                # If error, try to clean up partial file
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": f"Failed to save and validate file: {str(e)}"
                })
            finally:
                # Reset file position pointer for any future read
                await file.seek(0)
                
        return results
