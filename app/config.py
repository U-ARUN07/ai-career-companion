"""Configuration settings for the RAG-based Internship Matching System."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General App Settings
    app_name: str = "IntelliIntern AI - Unified Internship Platform"
    app_version: str = "2.0.0"
    app_env: str = "development"
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = 8000

    # Auth & Database Settings
    database_url: str = Field(
        default=f"sqlite:///{BASE_DIR / 'app.db'}",
        description="Database connection string (SQLite default, PostgreSQL supported)",
    )
    secret_key: str = Field(
        default="infosys-vip-springboard-secret-key-2025-token-auth-dev",
        description="Secret key for signing JWT tokens",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    vector_store_dir: Path = BASE_DIR / "vector_store"
    reports_dir: Path = BASE_DIR / "reports"
    uploads_dir: Path = BASE_DIR / "uploads" / "resumes"

    internships_file: Path = BASE_DIR / "data" / "internships.json"
    test_candidates_file: Path = BASE_DIR / "data" / "test_candidates.json"
    faiss_index_file: Path = BASE_DIR / "vector_store" / "faiss_index.bin"
    metadata_file: Path = BASE_DIR / "vector_store" / "internships_metadata.json"

    # Embedding Model Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    normalize_embeddings: bool = True

    # Matching Limits
    default_top_k: int = 5
    max_top_k: int = 50

    # Optional LLM Explanation Settings
    gemini_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    explanation_provider: str = Field(
        default="rule_based",
        description="Options: 'rule_based', 'mock', 'gemini', 'openai'",
    )


settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
settings.reports_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
