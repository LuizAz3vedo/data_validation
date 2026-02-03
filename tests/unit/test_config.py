"""Testes unitários para config.py."""


from extractor.config import Settings, get_settings


class TestSettings:
    """Testes para a classe Settings."""

    def test_default_provider_is_ollama(self) -> None:
        """Provider padrão deve ser ollama."""
        settings = Settings()
        assert settings.llm_provider == "ollama"

    def test_active_model_ollama(self) -> None:
        """active_model retorna modelo ollama quando provider é ollama."""
        settings = Settings(
            llm_provider="ollama",
            ollama_model="llama3.1:8b",
        )
        assert settings.active_model == "llama3.1:8b"

    def test_active_model_openai(self) -> None:
        """active_model retorna modelo openai quando provider é openai."""
        settings = Settings(
            llm_provider="openai",
            openai_model="gpt-4o-mini",
        )
        assert settings.active_model == "gpt-4o-mini"

    def test_active_model_anthropic(self) -> None:
        """active_model retorna modelo anthropic quando provider é anthropic."""
        settings = Settings(
            llm_provider="anthropic",
            anthropic_model="claude-3-haiku-20240307",
        )
        assert settings.active_model == "claude-3-haiku-20240307"

    def test_llm_api_key_ollama(self) -> None:
        """Ollama não precisa de API key."""
        settings = Settings(llm_provider="ollama")
        assert settings.llm_api_key == "ollama"

    def test_llm_api_key_openai(self) -> None:
        """OpenAI retorna a key configurada."""
        settings = Settings(
            llm_provider="openai",
            openai_api_key="sk-test-key",
        )
        assert settings.llm_api_key == "sk-test-key"

    def test_llm_api_key_anthropic(self) -> None:
        """Anthropic retorna a key configurada."""
        settings = Settings(
            llm_provider="anthropic",
            anthropic_api_key="sk-ant-test-key",
        )
        assert settings.llm_api_key == "sk-ant-test-key"

    def test_cache_enabled_default(self) -> None:
        """Cache deve estar habilitado por padrão."""
        settings = Settings()
        assert settings.cache_enabled is True

    def test_default_redis_url(self) -> None:
        """URL do Redis deve ter valor padrão."""
        settings = Settings()
        assert "localhost" in str(settings.redis_url)
        assert "6379" in str(settings.redis_url)

    def test_default_retry_settings(self) -> None:
        """Configurações de retry devem ter valores padrão."""
        settings = Settings()
        assert settings.max_retries == 3
        assert settings.retry_delay_seconds == 2.0

    def test_ollama_timeout_default(self) -> None:
        """Timeout do Ollama deve ser 120s por padrão."""
        settings = Settings()
        assert settings.ollama_timeout == 120


class TestGetSettings:
    """Testes para função get_settings."""

    def test_returns_settings_instance(self) -> None:
        """Deve retornar instância de Settings."""
        # Limpa cache
        get_settings.cache_clear()
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_returns_cached_instance(self) -> None:
        """Deve retornar mesma instância (cached)."""
        get_settings.cache_clear()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
