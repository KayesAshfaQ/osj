"""Unit tests for application settings validation and credential masking."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings

pytestmark = pytest.mark.unit


def test_openai_key_accepts_canonical_and_legacy_environment_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPEN_AI_API_KEY", raising=False)
    canonical = Settings.model_validate({"OPENAI_API_KEY": "canonical"})
    legacy = Settings.model_validate({"OPEN_AI_API_KEY": "legacy"})
    assert canonical.openai_api_key == "canonical"
    assert legacy.openai_api_key == "legacy"
    assert "canonical" not in repr(canonical)


def test_qdrant_settings_default_to_local_and_reject_ambiguous_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    local = Settings.model_validate({"QDRANT_PATH": "qdrant_db"})
    assert local.qdrant_path == "qdrant_db"
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_PATH", "other_index")
    with pytest.raises(ValidationError, match="QDRANT_URL"):
        Settings()


def test_database_url_is_not_exposed_in_settings_repr() -> None:
    config = Settings.model_validate({"DATABASE_URL": "postgresql+asyncpg://user:password@localhost/db"})
    assert "password" not in repr(config)


def test_gemini_key_loads_from_environment_and_is_masked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-gemini-credential")
    config = Settings(_env_file=None)  # type: ignore[call-arg]
    assert config.gemini_api_key == "synthetic-gemini-credential"
    assert "synthetic-gemini-credential" not in repr(config)
    assert config.llm_provider == "deepseek"


def test_qdrant_api_key_is_masked_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QDRANT_API_KEY", "secret-qdrant-key")
    config = Settings(_env_file=None)  # type: ignore[call-arg]
    assert config.qdrant_api_key == "secret-qdrant-key"
    assert "secret-qdrant-key" not in repr(config)


def test_cors_origins_defaults_and_accepts_list_or_csv() -> None:
    default_config = Settings(_env_file=None)  # type: ignore[call-arg]
    assert default_config.cors_origins == ["*"]

    custom_config = Settings(cors_origins=["https://osj-example.web.app", "https://example.com"], _env_file=None)  # type: ignore[call-arg]
    assert custom_config.cors_origins == ["https://osj-example.web.app", "https://example.com"]
