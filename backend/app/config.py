import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Technopie AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    SECRET_KEY: str = "technopie-ai-super-secret-key-change-in-production-2026-secure"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/technopie.db"
    
    # AI Providers
    DEFAULT_AI_PROVIDER: str = "gemini" # gemini | openai | anthropic | mock
    DEFAULT_FAST_MODEL: str = "gemini-2.5-flash"
    DEFAULT_REASONING_MODEL: str = "gemini-2.5-pro"
    ALLOW_MOCK_FALLBACK: bool = False
    AI_REQUEST_TIMEOUT_SECONDS: float = 30.0
    AI_MAX_RETRIES: int = 3
    AI_RETRY_BACKOFF_FACTOR: float = 1.5
    
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Integrations
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/integrations/google/callback"
    TOKEN_ENCRYPTION_KEY: str = "secret-aes-token-encryption-key-32bytes!!"

    # Paths
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DOCS_DIR: Path = BASE_DIR / "generated_docs"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DOCS_DIR.mkdir(parents=True, exist_ok=True)
