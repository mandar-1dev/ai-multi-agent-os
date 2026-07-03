"""
Central configuration for the AI Multi-Agent Operating System.
All values are overridable via environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Multi-Agent Operating System"
    ENV: str = "development"
    DEBUG: bool = True

    # --- Database ---
    # Defaults to local SQLite so the project runs with zero external services.
    # Set DATABASE_URL to a Postgres DSN for production, e.g.:
    # postgresql+psycopg2://user:password@localhost:5432/agentos
    DATABASE_URL: str = "sqlite:///./agentos.db"

    # --- Redis (task queue / pub-sub / cache) ---
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = True

    # --- Vector store (ChromaDB) ---
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION: str = "agentos_memory"

    # --- LLM Provider (Google Gemini) ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # --- Auth ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # --- Orchestrator ---
    MAX_PARALLEL_AGENTS: int = 4
    MAX_TASK_RETRIES: int = 2
    AGENT_TIMEOUT_SECONDS: int = 60

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
