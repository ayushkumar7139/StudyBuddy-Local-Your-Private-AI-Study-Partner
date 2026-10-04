from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, BASE_DIR
from app.database import init_db
from app.routers import notes, study, quizzes, flashcards, summaries

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="StudyBuddy Local: Private AI Study Companion"
)

# Enable CORS for local cross-origin development if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(notes.router)
app.include_router(study.router)
app.include_router(quizzes.router)
app.include_router(flashcards.router)
app.include_router(summaries.router)

# Mount static frontend assets
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.on_event("startup")
def startup_event():
    init_db()
    print(f"=== {settings.PROJECT_NAME} v{settings.VERSION} initialized ===")
    print("Database ready. Web interface accessible at http://localhost:8000")
