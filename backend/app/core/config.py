from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict
import os

class Settings(BaseSettings):
    APP_NAME: str = "AstraRoute AI"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database: SQLite by default for zero-config portable run; Supabase PostgreSQL if provided
    DATABASE_URL: str = "sqlite:///./astraroute.db"

    # API Keys (optional; simulator activates seamlessly if missing)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Global FinOps Policy Defaults
    DEFAULT_MAX_BUDGET_PER_REQUEST: float = 0.05  # $0.05
    DEFAULT_MIN_QUALITY_THRESHOLD: float = 0.70   # 70%
    DEFAULT_MAX_LATENCY_MS: int = 4000            # 4.0s
    DEFAULT_MAX_RETRIES: int = 2

    # Routing Weights Defaults
    DEFAULT_WEIGHT_COST: float = 0.40
    DEFAULT_WEIGHT_QUALITY: float = 0.35
    DEFAULT_WEIGHT_LATENCY: float = 0.15
    DEFAULT_WEIGHT_RELIABILITY: float = 0.10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_provider_status(self) -> Dict[str, bool]:
        return {
            "openai": bool(self.OPENAI_API_KEY and len(self.OPENAI_API_KEY) > 5),
            "anthropic": bool(self.ANTHROPIC_API_KEY and len(self.ANTHROPIC_API_KEY) > 5),
            "gemini": bool(self.GEMINI_API_KEY and len(self.GEMINI_API_KEY) > 5),
            "groq": bool(self.GROQ_API_KEY and len(self.GROQ_API_KEY) > 5),
        }

    def has_any_live_provider(self) -> bool:
        return any(self.get_provider_status().values())

settings = Settings()

