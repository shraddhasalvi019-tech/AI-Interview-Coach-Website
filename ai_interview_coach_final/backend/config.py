import os
from dotenv import load_dotenv

_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(_ENV_PATH, override=True)

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI-Powered Intelligent Interview Coaching System")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "interview_ai_super_secret_jwt_key_academic_project_2026")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Database URLs (PostgreSQL with psycopg2 driver dialect)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/interview_ai_db")
    FALLBACK_SQLITE_URL: str = os.getenv("FALLBACK_SQLITE_URL", "sqlite:///./interview_ai.db")

    # Generative AI Provider settings
    GENAI_PROVIDER: str = os.getenv("GENAI_PROVIDER", "google")
    GENAI_API_KEY: str = os.getenv("GENAI_API_KEY", "")
    GENAI_MODEL: str = os.getenv("GENAI_MODEL", "gemini-2.5-flash")

    # Scoring Weights
    WEIGHT_TECHNICAL: float = float(os.getenv("WEIGHT_TECHNICAL", "0.30"))
    WEIGHT_CORRECTNESS: float = float(os.getenv("WEIGHT_CORRECTNESS", "0.20"))
    WEIGHT_COMPLETENESS: float = float(os.getenv("WEIGHT_COMPLETENESS", "0.15"))
    WEIGHT_RELEVANCE: float = float(os.getenv("WEIGHT_RELEVANCE", "0.15"))
    WEIGHT_COMMUNICATION: float = float(os.getenv("WEIGHT_COMMUNICATION", "0.20"))

settings = Settings()
