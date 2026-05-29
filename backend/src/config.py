"""Configuration management using Pydantic Settings"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://toxzone:toxzone_pass@localhost:5432/toxzone",
        description="PostgreSQL database URL"
    )
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "toxzone"
    database_user: str = "toxzone"
    database_password: str = "toxzone_pass"

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    debug: bool = True

    # Security
    secret_key: str = Field(
        default="change_this_in_production_random_string_min_32_chars",
        min_length=32
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        json_encoders = {
            # Add any custom JSON encoders here
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()