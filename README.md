# AI Data Analyst Agent MVP

![AI Data Analyst Agent Dashboard](image/Screenshot%202026-07-12%20012534.png)

A production-quality, local MVP of an **AI Data Analyst Agent** built with FastAPI, LangGraph, SQLite, and Vanilla JS.

This application allows users to upload Excel (.xlsx) files and automatically clean the data, generate profiling statistics, draw Plotly charts, formulate SQL query templates, extract AI-powered insights, suggest Power BI layouts, and construct a downloadable Markdown analysis report.

---

## Technical Architecture

- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLite
- **AI Agentic Flow**: LangGraph, LangChain, ChatGoogleGenerativeAI (Gemini 2.5 Flash)
- **Data Engineering**: Pandas, NumPy, OpenPyXL
- **Visualizations**: Plotly, Kaleido
- **Frontend**: Vanilla HTML5, CSS3 (white-and-blue professional theme), JavaScript (ES6 relative Fetch API)

---

## Folder Structure

```
ai-data-analyst/
├── backend/
│   ├── agents/
│   │   ├── llm.py
│   │   ├── upload_agent.py
│   │   ├── cleaning_agent.py
│   │   ├── profiling_agent.py
│   │   ├── sql_agent.py
│   │   ├── visualization_agent.py
│   │   ├── insight_agent.py
│   │   ├── dashboard_agent.py
│   │   └── report_agent.py
│   ├── database/
│   │   └── analyst.db (automatically created)
│   ├── tools/
│   │   ├── excel_tool.py
│   │   ├── chart_tool.py
│   │   ├── sql_tool.py
│   │   └── report_tool.py
│   ├── uploads/ (automatically created)
│   ├── reports/ (automatically created)
│   ├── charts/ (automatically created)
│   ├── app.py
│   ├── config.py
│   └── database.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt
├── README.md
└── .env
```

---

## Setup and Installation

### 1. Prerequisites
Ensure you have **Python 3.10** or higher installed on your system.

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and insert your Gemini API Key:
```bash
cp .env.example .env
```
Open `.env` and fill in:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Create Virtual Environment & Install Requirements
Create a python virtual environment and activate it:

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running the Application

Start the local application using:
```bash
python app.py
```
This triggers the programmatically run Uvicorn server.
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## AI Agent Workflow

1. **Upload Agent**: Accepts multiple Excel uploads, saves them, validates file structure, and exposes sheet metadata and top-10 row preview arrays.
2. **Cleaning Agent**: Programmatically deduplicates records, standardizes headers, handles null values (fills or tags "Unknown"), and auto-converts datatypes (strings representing dates or currencies).
3. **Data Profiling Agent**: Calculates shape sizes, missing values rate, categorical distributions, mode, and numeric quartiles.
4. **Visualization Agent**: AI scans columns to select best parameters, then executes Plotly drawing routines saving exactly 4 charts (Bar, Line, Pie, Histogram) as PNG files.
5. **SQL Agent**: Automatically builds 5 default query examples. Translates user natural language questions to read-only SQLite syntax, runs queries, and details outcomes.
6. **Insight Agent**: Extracts key data performance metrics, outlines observations, details caveats, and gives actionable tips.
7. **Dashboard Agent**: Recommends Power BI KPIs, charts assignments, slicers, and colors logic.
8. **Report Agent**: Synthesizes all summaries and details into a downloadable Markdown (.md) document.
