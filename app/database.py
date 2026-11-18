"""Database configuration and session management.

Supports zero-config local SQLite (sqlite:///./app.db) by default so that
the project runs out-of-the-box on any machine without requiring a running
PostgreSQL service, while fully supporting PostgreSQL if DATABASE_URL is configured.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent

# Database URL configuration: use settings or fallback to local SQLite
db_url = getattr(settings, "database_url", None) or f"sqlite:///{BASE_DIR / 'app.db'}"

# Connect args (check_same_thread=False is required for SQLite with multi-threading)
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding a clean database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables defined in models if they don't exist yet."""
    import app.models  # ensure models are registered with Base.metadata
    Base.metadata.create_all(bind=engine)
