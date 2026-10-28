import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import Base, get_db

TEST_DB_FILE = "./test_interview_ai.db"
engine = create_engine(f"sqlite:///{TEST_DB_FILE}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_gemini(monkeypatch):
    """Stubs the Gemini network call so tests run offline and deterministically."""
    import json
    from backend.services.ai_service import ai_service

    def fake_call(prompt: str) -> str:
        if '"overall_summary"' in prompt:
            return json.dumps({"overall_summary": "Good", "strengths": [], "weaknesses": [], "technical_gaps": [],
                               "communication_issues": [], "recommended_topics": [], "practice_areas": [],
                               "tips": [], "sample_answer_improvements": []})
        if '"strong_skills"' in prompt:
            return json.dumps({"target_role": "x", "expected_skills": ["a"], "strong_skills": ["a"],
                               "skills_to_improve": [], "recommended_learning_areas": []})
        if '"correctness"' in prompt:
            return json.dumps({"correctness": 8, "relevance": 8, "completeness": 7, "technical_understanding": 8,
                               "communication": 8, "overall_score": 8, "strengths": ["a"], "improvements": ["b"],
                               "feedback_text": "ok", "needs_follow_up": False, "follow_up_question": None})
        import random
        return json.dumps({"question": f"Mock question {random.random()}", "category": "Technical",
                           "targeted_skill": "Java", "difficulty": "Medium"})

    monkeypatch.setattr(ai_service, "_call_llm", fake_call)
