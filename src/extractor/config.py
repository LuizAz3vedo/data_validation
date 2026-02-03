"""Configurações centralizadas com Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    llm_provider: Literal["ollama", "openai", "anthropic"] = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 120

    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str = Field(default="", repr=False)
    anthropic_model: str = "claude-3-haiku-20240307"

    llm_model: str = "llama3.1:8b"

    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")  # type: ignore[assignment]
    cache_ttl_seconds: int = 3600
    cache_enabled: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    max_retries: int = 3
    retry_delay_seconds: float = 2.0

    @property
    def active_model(self) -> str:
        """Retorna o modelo ativo baseado no provider."""
        if self.llm_provider == "ollama":
            return self.ollama_model
        elif self.llm_provider == "openai":
            return self.openai_model
        else:
            return self.anthropic_model

    @property
    def llm_api_key(self) -> str:
        """Retorna a API key do provider configurado."""
        if self.llm_provider == "openai":
            return self.openai_api_key
        elif self.llm_provider == "anthropic":
            return self.anthropic_api_key
        return "ollama"


@lru_cache
def get_settings() -> Settings:
    """Singleton das configurações."""
    return Settings()
