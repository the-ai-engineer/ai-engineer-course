"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/rag_chatbot"

    # OpenAI
    openai_api_key: str = ""

    # Models
    embedding_model: str = "text-embedding-3-small"
    generation_model: str = "gpt-4o-mini"

    # Embedding dimensions
    embedding_dimensions: int = 1536

    # CORS origins (comma-separated list)
    cors_origins: str = "http://localhost:4567"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
