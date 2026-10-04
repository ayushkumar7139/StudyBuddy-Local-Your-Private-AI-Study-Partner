import uvicorn
import webbrowser
import time
import os

if __name__ == "__main__":
    print("==================================================")
    print("      StudyBuddy Local: Private AI Companion     ")
    print("==================================================")
    print("Starting server at: http://localhost:8000")
    print("Press Ctrl+C to stop.")
    print("==================================================")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
