import uvicorn
from backend.config import HOST, PORT

if __name__ == "__main__":
    print(f"============================================================")
    print(f"🚀 Launching AI Data Analyst Agent MVP")
    print(f"🌍 Server available at: http://{HOST}:{PORT}")
    print(f"💡 Press Ctrl+C to stop the application")
    print(f"============================================================")
    
    # Run uvicorn server pointing to FastAPI app in backend/app.py
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=True)
