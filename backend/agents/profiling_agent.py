import pandas as pd
from typing import Dict, Any, List

class ProfilingAgent:
    def __init__(self):
        pass
        
    def profile_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate statistical summary, columns types, missing rates,
        and value distributions for a sheet.
        """
        total_rows = len(df)
        total_columns = len(df.columns)
        
        # Calculate overall counts
        missing_count = int(df.isna().sum().sum())
        duplicate_count = int(df.duplicated().sum())
        
        columns_info = []
        
        for col in df.columns:
            series = df[col]
            dtype_str = str(series.dtype)
            non_null = int(series.count())
            nulls = int(series.isna().sum())
            uniques = int(series.nunique())
            
            # Sample of unique values (up to 10)
            sample_vals = series.dropna().unique()
            sample_list = [str(v) for v in sample_vals[:10]]
            
            # Formulate stats
            stats = {}
            if pd.api.types.is_numeric_dtype(series):
                # Ensure no NaN is written to json payload
                stats = {
                    "mean": float(series.mean()) if non_null > 0 else 0.0,
                    "min": float(series.min()) if non_null > 0 else 0.0,
                    "max": float(series.max()) if non_null > 0 else 0.0,
                    "std": float(series.std()) if non_null > 1 else 0.0,
                    "25%": float(series.quantile(0.25)) if non_null > 0 else 0.0,
                    "50%": float(series.quantile(0.50)) if non_null > 0 else 0.0,
                    "75%": float(series.quantile(0.75)) if non_null > 0 else 0.0,
                }
                # Handle inf or nan floats if any
                for k, v in stats.items():
                    import math
                    if math.isnan(v) or math.isinf(v):
                        stats[k] = 0.0
                        
            elif pd.api.types.is_datetime64_any_dtype(series):
                stats = {
                    "min": str(series.min()) if non_null > 0 else "NaT",
                    "max": str(series.max()) if non_null > 0 else "NaT"
                }
            else:
                # Text / Categorical
                mode_series = series.mode()
                top_val = str(mode_series.iloc[0]) if not mode_series.empty else "N/A"
                
                try:
                    val_counts = series.value_counts()
                    top_freq = int(val_counts.iloc[0]) if not val_counts.empty else 0
                except Exception:
                    top_freq = 0
                    
                stats = {
                    "top_value": top_val,
                    "top_frequency": top_freq
                }
                
            columns_info.append({
                "name": col,
                "type": dtype_str,
                "non_null_count": non_null,
                "null_count": nulls,
                "unique_count": uniques,
                "sample_values": sample_list,
                "statistics": stats
            })
            
        return {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "missing_values_count": missing_count,
            "duplicate_count": duplicate_count,
            "columns": columns_info
        }
