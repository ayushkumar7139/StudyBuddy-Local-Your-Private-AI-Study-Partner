import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "studybuddy.db"

# Ensure required data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "StudyBuddy Local"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    
    # Local LLM default endpoints
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LM_STUDIO_BASE_URL: str = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    
    # Default model preferences
    DEFAULT_OLLAMA_MODEL: str = os.getenv("DEFAULT_OLLAMA_MODEL", "llama3")
    
    # RAG Settings
    CHUNK_SIZE: int = 400  # Words per chunk
    CHUNK_OVERLAP: int = 80 # Words overlap
    MAX_RETRIEVED_CHUNKS: int = 5

settings = Settings()
