from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from app.config import settings


db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Ensure relative SQLite path always resolves to backend/app.db
if db_url in ("sqlite:///./app.db", "sqlite:///app.db", "sqlite:///./backend/app.db"):
    backend_dir = Path(__file__).resolve().parent.parent
    db_path = (backend_dir / "app.db").resolve().as_posix()
    db_url = f"sqlite:///{db_path}"

if db_url.startswith("sqlite"):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        db_url
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()