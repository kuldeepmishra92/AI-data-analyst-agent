import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.agents.llm import get_llm
from backend.database import run_query
from backend.tools.sql_tool import get_database_schema, format_sql_result_for_llm

class GeneratedQuery(BaseModel):
    title: str = Field(description="Business description of what the query calculates")
    query: str = Field(description="Valid SQLite SQL query")

class DefaultQueriesList(BaseModel):
    queries: List[GeneratedQuery] = Field(description="Exactly 5 useful default business queries")

class SQLAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.0)
        
    def generate_default_queries(self, table_name: str) -> List[Dict[str, str]]:
        """
        Scan table schema and generate 5 standard useful SQL queries
        (e.g., Top 10 rows, Group by categorical, average values, etc.).
        """
        schema = get_database_schema()
        table_schema = schema.get(table_name, [])
        schema_text = "\n".join([f"- {col['name']}: {col['type']}" for col in table_schema])
        
        prompt = f"""
You are an expert Data Analyst and SQLite DBA.
Given the schema for the table '{table_name}':
{schema_text}

Generate exactly 5 useful, valid SQLite queries that a business analyst would want to run to explore this dataset.
Include:
1. An overall metric calculation (e.g. average, sum, or counts)
2. A top-10 ranking query (e.g. top customers, top products, or highest values)
3. A grouping/aggregation query (e.g. total sales by category or region)
4. A chronological/time-based aggregation query if there is a date column, otherwise another grouping query
5. A simple status or validation check query (e.g. counting nulls, duplicates, or listing unique categories)

Ensure:
- The SQL dialect must be SQLite-compatible (no window functions if not necessary, double check syntax).
- Make sure to use exact column names as specified in the schema. Do not invent columns.
- Keep table name as '{table_name}'.

Return the output in JSON format matching this schema:
{{
  "queries": [
    {{
      "title": "Title describing query purpose",
      "query": "SELECT ... FROM {table_name} ..."
    }}
  ]
}}
"""
        try:
            structured_llm = self.llm.with_structured_output(DefaultQueriesList)
            result = structured_llm.invoke(prompt)
            return [{"title": q.title, "query": q.query} for q in result.queries]
        except Exception as e:
            print(f"Failed to generate default queries: {str(e)}")
            # Fallback queries
            return [
                {
                    "title": "Preview Dataset (First 10 Rows)",
                    "query": f"SELECT * FROM {table_name} LIMIT 10;"
                },
                {
                    "title": "Total Row Count",
                    "query": f"SELECT COUNT(*) AS total_rows FROM {table_name};"
                }
            ]

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Translate a natural language question into SQL, run it,
        and generate a textual summary of the results.
        """
        schema = get_database_schema()
        schema_summary = []
        for table_name, columns in schema.items():
            cols_text = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            schema_summary.append(f"Table '{table_name}' with columns: {cols_text}")
        schema_text = "\n".join(schema_summary)
        
        # 1. SQL Generation Phase
        sql_prompt = f"""
You are a SQL Agent. Convert the user's natural language question into a single valid SQLite query.
Available Database Schema:
{schema_text}

Question: "{question}"

Rules:
- Generate ONLY a valid SQLite query. Do not include markdown code block formatting in your thoughts, but return a clean query.
- Use only columns that exist in the schemas above.
- Make sure table names match exactly.
- If joining tables is needed, use standard SQLite join syntax.
- Ensure the query is read-only (SELECT statements only).

Return the SQL query. Do not write explanation.
"""
        # Call LLM directly to get raw SQL text
        raw_response = self.llm.invoke(sql_prompt).content
        
        # Clean any backticks if returned
        sql_query = str(raw_response).strip()
        if "```" in sql_query:
            # extract code block
            match = re.search(r"```(?:sql)?(.*?)```", sql_query, re.DOTALL)
            if match:
                sql_query = match.group(1).strip()
        # Clean any single backticks
        sql_query = sql_query.replace("`", "")
        
        # 2. Execution Phase
        try:
            execution_result = run_query(sql_query)
            formatted_results = format_sql_result_for_llm(execution_result)
            error = None
        except Exception as e:
            execution_result = {"columns": [], "rows": [], "count": 0}
            formatted_results = f"ERROR executing query: {str(e)}"
            error = str(e)
            
        # 3. Answer Generation Phase
        answer_prompt = f"""
You are a helpful Data Analyst explaining database results to a user.
The user asked: "{question}"
The SQL query generated was:
```sql
{sql_query}
```
The execution results from the database:
{formatted_results}

Based on this information, provide a clear, user-friendly, and concise summary answer to the user's question.
If there was an error in the query, explain that you encountered a database execution issue and recommend how they might rephrase the question.
"""
        answer = self.llm.invoke(answer_prompt).content
        
        return {
            "query": sql_query,
            "success": error is None,
            "error": error,
            "result_rows": execution_result["rows"],
            "result_columns": execution_result["columns"],
            "result_count": execution_result["count"],
            "answer": str(answer).strip()
        }
