"""Unit tests for AI LLM factory, provider configuration, and timeout bounds."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.ai import llm_factory
from app.ai.llm_factory import LLMConfigurationError, create_llm
from app.core.config import Settings, settings

pytestmark = pytest.mark.unit


def make_config(**overrides: Any) -> Settings:
    values: dict[str, Any] = dict(
        _env_file=None,
        llm_provider="openai",
        llm_model="gpt-4o",
        OPENAI_API_KEY="openai-test",
        groq_api_key="groq-test",
        deepseek_api_key="deepseek-test",
        redis_url="redis://localhost:6379/0",
        llm_timeout=8,
    )
    if "openai_api_key" in overrides:
        overrides["OPENAI_API_KEY"] = overrides.pop("openai_api_key")
    values.update(overrides)
    return Settings.model_validate(values)


@pytest.mark.parametrize(
    ("provider", "key_field", "constructor"),
    [
        ("openai", "openai_api_key", "ChatOpenAI"),
        ("groq", "groq_api_key", "ChatGroq"),
        ("deepseek", "deepseek_api_key", "ChatOpenAI"),
    ],
)
def test_llm_missing_key_fails_before_constructor(
    monkeypatch: pytest.MonkeyPatch, provider: str, key_field: str, constructor: str
) -> None:
    model = Mock()
    monkeypatch.setattr(llm_factory, constructor, model)
    with pytest.raises(LLMConfigurationError, match=f"{key_field.upper()} is required"):
        create_llm(make_config(llm_provider=provider, **{key_field: "  "}))
    model.assert_not_called()


def test_openai_uses_canonical_key_and_bounded_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    model = Mock(return_value=object())
    monkeypatch.setattr(llm_factory, "ChatOpenAI", model)
    result = create_llm(make_config(llm_timeout=8))
    assert result is model.return_value
    kwargs = model.call_args.kwargs
    assert kwargs["api_key"].get_secret_value() == "openai-test"
    assert kwargs["timeout"] == 8
    assert kwargs["max_retries"] == 0
    assert kwargs["streaming"] is True


def test_deepseek_passes_base_url_without_key_leak(monkeypatch: pytest.MonkeyPatch) -> None:
    model = Mock()
    monkeypatch.setattr(llm_factory, "ChatOpenAI", model)
    create_llm(make_config(llm_provider="deepseek", llm_model="gpt-4o", deepseek_base_url="https://example.invalid"))
    assert model.call_args.kwargs["model"] == "deepseek-chat"
    assert model.call_args.kwargs["base_url"] == "https://example.invalid"


def test_deepseek_default_endpoint_is_not_openai() -> None:
    config = Settings(_env_file=None, deepseek_api_key="synthetic", deepseek_base_url="")  # type: ignore[call-arg]
    model = create_llm(config)
    assert str(getattr(model, "openai_api_base", None)).startswith("https://api.deepseek.com")


@pytest.mark.parametrize("url", ["http://api.deepseek.com", "https://user:secret@api.deepseek.com", "not-a-url"])
def test_invalid_provider_endpoint_fails_locally(url: str) -> None:
    with pytest.raises(LLMConfigurationError):
        create_llm(Settings(_env_file=None, deepseek_api_key="synthetic", deepseek_base_url=url))  # type: ignore[call-arg]


def test_groq_constructor_uses_bounded_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    model = Mock()
    monkeypatch.setattr(llm_factory, "ChatGroq", model)
    create_llm(make_config(llm_provider="groq"))
    assert model.call_args.kwargs["timeout"] == 8
    assert model.call_args.kwargs["max_retries"] == 0
    assert model.call_args.kwargs["max_tokens"] == 600


def test_groq_constructor_accepts_custom_max_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    model = Mock()
    monkeypatch.setattr(llm_factory, "ChatGroq", model)
    create_llm(make_config(llm_provider="groq", llm_max_tokens=800))
    assert model.call_args.kwargs["max_tokens"] == 800


@pytest.mark.parametrize("timeout", [0, -1, 31])
def test_invalid_timeout_fails_before_constructor(monkeypatch: pytest.MonkeyPatch, timeout: int) -> None:
    model = Mock()
    monkeypatch.setattr(llm_factory, "ChatOpenAI", model)
    with pytest.raises(LLMConfigurationError, match="LLM_TIMEOUT"):
        create_llm(make_config(llm_timeout=timeout))
    model.assert_not_called()


def test_unsupported_provider_has_typed_error() -> None:
    with pytest.raises(LLMConfigurationError, match="Unsupported LLM provider: custom"):
        create_llm(make_config(llm_provider="custom"))


def test_legacy_factory_missing_key_is_typed_and_does_not_call_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "")
    constructor = Mock()
    monkeypatch.setattr(llm_factory, "ChatOpenAI", constructor)
    with pytest.raises(LLMConfigurationError, match="OPENAI_API_KEY is required"):
        create_llm()
    constructor.assert_not_called()


def test_create_llm_deepseek(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "deepseek")
    monkeypatch.setattr(settings, "llm_model", "deepseek-chat")
    monkeypatch.setattr(settings, "deepseek_api_key", "test-key")
    monkeypatch.setattr(settings, "deepseek_base_url", "https://api.deepseek.com")

    llm = create_llm()
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "deepseek-chat"
    assert llm.openai_api_base == "https://api.deepseek.com"


def test_create_llm_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "llm_model", "gpt-4o")
    monkeypatch.setattr(settings, "openai_api_key", "test-key")

    llm = create_llm()
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "gpt-4o"


def test_create_llm_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "groq")
    monkeypatch.setattr(settings, "llm_model", "llama3-8b-8192")
    monkeypatch.setattr(settings, "groq_api_key", "test-key")

    llm = create_llm()
    assert isinstance(llm, ChatGroq)
    assert llm.model_name == "llama3-8b-8192"


@pytest.mark.parametrize("provider", ["gemini", " GEMINI "])
def test_gemini_uses_explicit_native_configuration(monkeypatch: pytest.MonkeyPatch, provider: str) -> None:
    constructor = Mock()
    monkeypatch.setattr(llm_factory, "ChatGoogleGenerativeAI", constructor, raising=False)
    create_llm(make_config(llm_provider=provider, llm_model="gemini-3.8-flash", gemini_api_key="gemini-test"))
    kwargs = constructor.call_args.kwargs
    assert kwargs["model"] == "gemini-3.8-flash"
    assert kwargs["api_key"].get_secret_value() == "gemini-test"
    assert kwargs["vertexai"] is False
    assert kwargs["timeout"] == 8
    assert kwargs["max_retries"] == 0
    assert kwargs["max_tokens"] == 600


@pytest.mark.parametrize("model", ["", "  ", "deepseek-chat", "gpt-4o"])
def test_gemini_rejects_missing_or_foreign_model(monkeypatch: pytest.MonkeyPatch, model: str) -> None:
    constructor = Mock()
    monkeypatch.setattr(llm_factory, "ChatGoogleGenerativeAI", constructor, raising=False)
    with pytest.raises(LLMConfigurationError, match="LLM_MODEL"):
        create_llm(make_config(llm_provider="gemini", llm_model=model, gemini_api_key="synthetic"))
    constructor.assert_not_called()


def test_gemini_requires_its_own_key(monkeypatch: pytest.MonkeyPatch) -> None:
    constructor = Mock()
    monkeypatch.setattr(llm_factory, "ChatGoogleGenerativeAI", constructor, raising=False)
    with pytest.raises(LLMConfigurationError, match="GEMINI_API_KEY is required"):
        create_llm(make_config(llm_provider="gemini", llm_model="gemini-3.8-flash", gemini_api_key=" "))
    constructor.assert_not_called()


@pytest.mark.parametrize("timeout", [0, -1, 31])
def test_gemini_rejects_invalid_timeout(timeout: int) -> None:
    with pytest.raises(LLMConfigurationError, match="LLM_TIMEOUT"):
        create_llm(
            make_config(llm_provider="gemini", llm_model="gemini-3.8-flash", gemini_api_key="test", llm_timeout=timeout)
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [200, 429, 503])
async def test_native_gemini_http_boundary(monkeypatch: pytest.MonkeyPatch, status: int) -> None:
    import json

    import httpx
    from langchain_core.messages import HumanMessage
    from langchain_google_genai import ChatGoogleGenerativeAI

    from app.ai.llm_responses import invoke_llm, response_text
    from app.core.exceptions import LLMProviderError

    calls: list[httpx.Request] = []

    async def send(client: httpx.AsyncClient, request: httpx.Request, **kwargs: object) -> httpx.Response:
        calls.append(request)
        body = json.loads(request.content)
        assert body["generationConfig"]["maxOutputTokens"] == 2048
        assert request.extensions["timeout"]["read"] == 8
        assert request.url.host == "generativelanguage.googleapis.com"
        assert request.headers["x-goog-api-key"] == "synthetic-gemini"
        if status != 200:
            return httpx.Response(status, request=request, json={"error": {"code": status, "message": "private"}})
        return httpx.Response(
            200,
            request=request,
            json={
                "candidates": [
                    {
                        "content": {"role": "model", "parts": [{"text": "visible answer"}]},
                        "finishReason": "STOP",
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "send", send)
    monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
    monkeypatch.delenv("GOOGLE_GENAI_USE_ENTERPRISE", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "wrong-key")
    model = create_llm(
        make_config(
            llm_provider="gemini",
            llm_model="gemini-3.8-flash",
            gemini_api_key="synthetic-gemini",
            llm_max_tokens=2048,
        )
    )
    assert isinstance(model, ChatGoogleGenerativeAI)
    try:
        if status == 200:
            assert response_text(await invoke_llm(model, [HumanMessage(content="sanitized query")])) == "visible answer"
        else:
            with pytest.raises(LLMProviderError) as captured:
                await invoke_llm(model, [HumanMessage(content="sanitized query")])
            assert captured.value.status_code == status
        assert len(calls) == 1
    finally:
        await model.aclose()


@pytest.mark.parametrize("variable", ["GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_GENAI_USE_ENTERPRISE"])
def test_gemini_rejects_sdk_backend_override(monkeypatch: pytest.MonkeyPatch, variable: str) -> None:
    monkeypatch.setenv(variable, "true")
    with pytest.raises(LLMConfigurationError, match="Developer API"):
        create_llm(make_config(llm_provider="gemini", llm_model="gemini-3.8-flash", gemini_api_key="synthetic"))


@pytest.mark.parametrize("provider", ["openai", "deepseek"])
def test_openai_compatible_constructor_applies_output_cap(monkeypatch: pytest.MonkeyPatch, provider: str) -> None:
    constructor = Mock()
    monkeypatch.setattr(llm_factory, "ChatOpenAI", constructor)
    create_llm(make_config(llm_provider=provider, llm_max_tokens=725))
    kwargs = constructor.call_args.kwargs
    if provider == "deepseek":
        assert kwargs["extra_body"]["max_tokens"] == 725
    else:
        assert kwargs["max_completion_tokens"] == 725


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["openai", "deepseek"])
async def test_openai_compatible_http_payload_applies_output_cap(
    monkeypatch: pytest.MonkeyPatch, provider: str
) -> None:
    import json

    import httpx
    from langchain_core.messages import HumanMessage

    calls: list[httpx.Request] = []

    async def send(client: httpx.AsyncClient, request: httpx.Request, **kwargs: object) -> httpx.Response:
        calls.append(request)
        payload = json.loads(request.content)
        token_field = "max_tokens" if provider == "deepseek" else "max_completion_tokens"
        assert payload[token_field] == 725
        other_field = "max_completion_tokens" if provider == "deepseek" else "max_tokens"
        assert other_field not in payload
        assert request.extensions["timeout"]["read"] == 8
        return httpx.Response(
            200,
            request=request,
            headers={"content-type": "text/event-stream"},
            content=(
                'data: {"id":"synthetic","object":"chat.completion.chunk","model":"synthetic",'
                '"choices":[{"index":0,"delta":{"role":"assistant","content":"visible answer"},'
                '"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n'
            ),
        )

    monkeypatch.setattr(httpx.AsyncClient, "send", send)
    model = create_llm(make_config(llm_provider=provider, llm_max_tokens=725))
    response = await model.ainvoke([HumanMessage(content="synthetic query")])
    assert response.content == "visible answer"
    assert len(calls) == 1
