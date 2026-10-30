"""Application configuration using Pydantic v2 settings."""

from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with strict validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = Field(default="Secure AI Governance PoC")
    APP_VERSION: str = Field(default="0.1.0")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    # Security
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://user:password@localhost:5432/ai_governance"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, ge=1, le=50)
    DATABASE_MAX_OVERFLOW: int = Field(default=20, ge=0, le=100)

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0")

    # Vector Database
    VECTOR_DB_URL: str = Field(default="http://localhost:6333")
    VECTOR_COLLECTION_NAME: str = Field(default="ai_memory")

    # Audit
    ENABLE_AUDIT_LOG: bool = Field(default=True)
    AUDIT_LOG_PATH: str = Field(default="logs/audit.log")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=10000)

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"]
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)

    # AI Security
    MAX_PROMPT_LENGTH: int = Field(default=4000, ge=100, le=32000)
    ENABLE_PROMPT_INJECTION_DETECTION: bool = Field(default=True)
    SANITIZATION_LEVEL: Literal["none", "basic", "strict"] = Field(default="strict")

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure SECRET_KEY is strong enough."""
        if v == "your-super-secret-key-change-this-in-production":
            raise ValueError("SECRET_KEY must be changed from default value")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
