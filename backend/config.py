import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(dotenv_path=BASE_DIR / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Server Config
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# Database path
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "backend/database/analyst.db")

# Directory Configs
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
REPORT_DIR = BASE_DIR / "backend" / "reports"
CHART_DIR = BASE_DIR / "backend" / "charts"
DATABASE_DIR = DATABASE_PATH.parent

# Ensure directories exist
for directory in [UPLOAD_DIR, REPORT_DIR, CHART_DIR, DATABASE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
