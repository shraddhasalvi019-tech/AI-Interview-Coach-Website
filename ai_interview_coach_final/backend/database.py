import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

logger = logging.getLogger("interview_ai.database")

Base = declarative_base()

def get_engine():
    """
    Creates SQLAlchemy Engine with PostgreSQL as primary target.
    If PostgreSQL is unavailable on localhost, smoothly falls back to SQLite
    to ensure uninterrupted application functionality.
    """
    primary_url = settings.DATABASE_URL
    try:
        engine = create_engine(primary_url, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            logger.info("Successfully connected to primary PostgreSQL database.")
            print("[DATABASE] Connected to PostgreSQL database successfully.")
        return engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to SQLite database...")
        print(f"[DATABASE WARNING] PostgreSQL connection failed: {e}")
        print("[DATABASE] Falling back to SQLite database (interview_ai.db)...")
        fallback_url = settings.FALLBACK_SQLITE_URL
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False} if "sqlite" in fallback_url else {}
        )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes all database tables defined by SQLAlchemy models."""
    from backend import models  # Ensures all ORM models are registered
    Base.metadata.create_all(bind=engine)
    print("[DATABASE] All tables created/verified successfully.")
