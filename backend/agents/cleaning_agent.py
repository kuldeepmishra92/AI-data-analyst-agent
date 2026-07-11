import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

class CleaningAgent:
    def __init__(self):
        pass
        
    def sanitize_column_name(self, name: str) -> str:
        """Standardize column names to be lowercase and underscore-separated."""
        # Convert to string and strip
        s = str(name).strip()
        # Remove special characters
        s = re.sub(r'[^\w\s\-\.]', '', s)
        # Replace spaces, hyphens, and dots with underscores
        s = re.sub(r'[\s\-\.]+', '_', s)
        # Convert to lowercase
        s = s.lower()
        # Remove consecutive underscores
        s = re.sub(r'_+', '_', s)
        # Strip leading/trailing underscores
        s = s.strip('_')
        # If column name starts with a number, prepend with col_
        if s and s[0].isdigit():
            s = f"col_{s}"
        return s if s else "unnamed_column"

    def clean_numeric_value(self, val: Any) -> Any:
        """Programmatically scrub currency and format symbols from numeric inputs."""
        if pd.isna(val) or val is None:
            return np.nan
        if isinstance(val, (int, float, np.integer, np.floating)):
            return val
        
        s = str(val).strip()
        # Remove currency symbols and comma separators
        s = s.replace('$', '').replace(',', '').replace('€', '').replace('£', '')
        
        # Check if percentage
        is_pct = False
        if s.endswith('%'):
            is_pct = True
            s = s.rstrip('%').strip()
            
        try:
            # Try float conversion
            num = float(s)
            if is_pct:
                num = num / 100.0
            # If it's equivalent to an int, return int
            if num.is_integer():
                return int(num)
            return num
        except ValueError:
            return val

    def auto_convert_types(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Scan columns and automatically convert them to appropriate datatypes:
        - Dates: If column name contains 'date' or matches common patterns.
        - Numeric: If a column consists mostly of numeric characters or formatting.
        """
        actions = []
        df = df.copy()
        
        for col in df.columns:
            non_null_series = df[col].dropna()
            if non_null_series.empty:
                continue
                
            col_lower = col.lower()
            
            # 1. Date conversion strategy
            is_date_col = "date" in col_lower or "time" in col_lower
            if is_date_col or df[col].dtype == 'object':
                # Try parsing as dates
                try:
                    converted = pd.to_datetime(df[col], errors='coerce')
                    # If conversion succeeds for at least 70% of non-null records, apply it
                    if converted.notna().sum() >= 0.7 * len(non_null_series):
                        df[col] = converted
                        actions.append(f"Converted column '{col}' to DateTime format.")
                        continue
                except Exception:
                    pass
            
            # 2. Numeric conversion strategy
            if df[col].dtype == 'object':
                try:
                    # Apply cleaning helper
                    cleaned_series = df[col].apply(self.clean_numeric_value)
                    non_null_cleaned = cleaned_series.dropna()
                    
                    # If cleaned values are numeric, apply conversion
                    numeric_count = pd.to_numeric(non_null_cleaned, errors='coerce').notna().sum()
                    if numeric_count >= 0.8 * len(non_null_cleaned) and len(non_null_cleaned) > 0:
                        df[col] = pd.to_numeric(cleaned_series, errors='coerce')
                        actions.append(f"Converted column '{col}' to Numeric format.")
                except Exception:
                    pass
                    
        return df, actions

    def clean_sheet(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Performs the complete automated cleaning pipeline on a single worksheet DataFrame.
        """
        actions = []
        initial_rows = len(df)
        initial_cols = len(df.columns)
        
        # 1. Strip whitespaces from column headers & sanitize
        old_cols = list(df.columns)
        df.columns = [self.sanitize_column_name(col) for col in df.columns]
        # Check if column names changed
        col_changes = [f"'{old}' -> '{new}'" for old, new in zip(old_cols, df.columns) if old != new]
        if col_changes:
            actions.append(f"Standardized column headers: {', '.join(col_changes[:5])}" + ("..." if len(col_changes) > 5 else ""))

        # 2. Trim whitespace in string columns
        string_cols = df.select_dtypes(include=['object']).columns
        for col in string_cols:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            
        # 3. Handle empty rows & empty columns
        df = df.dropna(how='all')
        rows_after_empty_drop = len(df)
        empty_rows_removed = initial_rows - rows_after_empty_drop
        if empty_rows_removed > 0:
            actions.append(f"Removed {empty_rows_removed} completely empty rows.")
            
        # Remove completely empty columns
        df = df.dropna(how='all', axis=1)
        cols_after_empty_drop = len(df.columns)
        empty_cols_removed = initial_cols - cols_after_empty_drop
        if empty_cols_removed > 0:
            actions.append(f"Removed {empty_cols_removed} completely empty columns.")

        # 4. Remove duplicate rows
        rows_before_dup = len(df)
        df = df.drop_duplicates()
        duplicates_removed = rows_before_dup - len(df)
        if duplicates_removed > 0:
            actions.append(f"Removed {duplicates_removed} duplicate rows.")

        # 5. Type Conversions
        df, conv_actions = self.auto_convert_types(df)
        actions.extend(conv_actions)

        # 6. Fill missing values with sensible defaults
        missing_count = df.isna().sum().sum()
        if missing_count > 0:
            fill_summary = []
            for col in df.columns:
                nulls_in_col = df[col].isna().sum()
                if nulls_in_col > 0:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(0)
                        fill_summary.append(f"'{col}' filled with 0")
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        # For dates, don't fill with 0, fill with a default epoch or leave?
                        # Leaving dates empty is usually better, or fill with a placeholder
                        pass
                    else:
                        df[col] = df[col].fillna("Unknown")
                        fill_summary.append(f"'{col}' filled with 'Unknown'")
            if fill_summary:
                actions.append(f"Handled missing values: {', '.join(fill_summary[:5])}" + ("..." if len(fill_summary) > 5 else ""))

        summary = {
            "initial_shape": (initial_rows, initial_cols),
            "final_shape": df.shape,
            "duplicates_removed": duplicates_removed,
            "empty_rows_removed": empty_rows_removed,
            "missing_values_imputed": int(missing_count),
            "actions_taken": actions
        }
        
        return df, summary
