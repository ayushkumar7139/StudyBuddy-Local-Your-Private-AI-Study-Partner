import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, get_db
from app.parsers.note_parser import NoteParser
from app.rag.retriever import LocalRAGRetriever
from app.llm.provider import LocalLLMProvider
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def reset_test_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS notes")
    cursor.execute("DROP TABLE IF EXISTS note_chunks")
    cursor.execute("DROP TABLE IF EXISTS quizzes")
    cursor.execute("DROP TABLE IF EXISTS quiz_attempts")
    cursor.execute("DROP TABLE IF EXISTS flashcard_decks")
    cursor.execute("DROP TABLE IF EXISTS summaries")
    conn.commit()
    conn.close()
    init_db()

def test_database_initialization():
    print("Testing database initialization...")
    reset_test_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    conn.close()
    
    assert "notes" in tables
    assert "note_chunks" in tables
    assert "quizzes" in tables
    assert "flashcard_decks" in tables
    assert "summaries" in tables
    print("[OK] Database initialized with all required tables.")

def test_note_chunker():
    print("Testing note chunker...")
    sample_text = "Machine learning is a field of study devoted to understanding and building methods that learn. Supervised learning algorithms build a mathematical model of a set of data that contains both the inputs and the desired outputs."
    chunks = NoteParser.chunk_text(sample_text, "ml_notes.txt", chunk_size=15, overlap=5)
    assert len(chunks) > 0
    assert "source_label" in chunks[0]
    assert "ml_notes.txt" in chunks[0]["source_label"]
    print("[OK] Note chunking working correctly.")

def test_note_upload_and_rag_search(tmp_path):
    print("Testing note upload & RAG search...")
    note_file = tmp_path / "test_notes.txt"
    note_file.write_text("Artificial Intelligence and Deep Learning are transforming healthcare and robotics. Neural networks extract hierarchical features from raw data.", encoding="utf-8")
    
    with open(note_file, "rb") as f:
        response = client.post("/api/notes/upload", files={"file": ("test_notes.txt", f, "text/plain")})
    
    assert response.status_code == 200
    data = response.json()
    assert "test_notes" in data["filename"]
    assert data["chunk_count"] > 0
    note_id = data["id"]

    # Test RAG retrieval
    results = LocalRAGRetriever.search("Neural networks healthcare", note_ids=[note_id], top_k=2)
    assert len(results) > 0
    print("[OK] Note upload and hybrid RAG context retrieval working.")

def test_study_chat_endpoint():
    print("Testing study chat API...")
    response = client.post("/api/study/chat", json={
        "query": "Explain deep learning in simple terms",
        "explanation_level": "beginner",
        "is_hint_mode": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    print("[OK] Study chat endpoint returning clean response.")

def test_quiz_generation_and_submit():
    print("Testing quiz generation & submission API...")
    gen_res = client.post("/api/quizzes/generate", json={
        "title": "Unit Test Quiz",
        "num_questions": 2,
        "topic_query": "Artificial Intelligence"
    })
    assert gen_res.status_code == 200
    quiz_data = gen_res.json()
    assert quiz_data["id"] is not None
    assert len(quiz_data["questions"]) > 0

    q1_id = str(quiz_data["questions"][0]["id"])
    correct = quiz_data["questions"][0].get("correct_answer", "")

    sub_res = client.post("/api/quizzes/submit", json={
        "quiz_id": quiz_data["id"],
        "answers": {q1_id: correct}
    })
    assert sub_res.status_code == 200
    report = sub_res.json()
    assert "score_percentage" in report
    print("[OK] Practice Quiz generation and grading working.")

def test_flashcards_generation():
    print("Testing flashcard deck generation...")
    res = client.post("/api/flashcards/generate", json={
        "title": "Unit Test Flashcards",
        "num_cards": 3
    })
    assert res.status_code == 200
    deck = res.json()
    assert deck["id"] is not None
    assert len(deck["cards"]) > 0
    print("[OK] Flashcards generation working.")

def test_summary_generation():
    print("Testing revision summary generation...")
    res = client.post("/api/summaries/generate", json={
        "title": "Unit Test Summary",
        "topic": "Neural Networks"
    })
    assert res.status_code == 200
    summary = res.json()
    assert "content" in summary
    print("[OK] Revision summary generation working.")

if __name__ == "__main__":
    import tempfile
    tmp_dir = Path(tempfile.mkdtemp())
    print("=== Running StudyBuddy Local Test Suite ===")
    test_database_initialization()
    test_note_chunker()
    test_note_upload_and_rag_search(tmp_dir)
    test_study_chat_endpoint()
    test_quiz_generation_and_submit()
    test_flashcards_generation()
    test_summary_generation()
    print("ALL TESTS PASSED SUCCESSFULLY!")
