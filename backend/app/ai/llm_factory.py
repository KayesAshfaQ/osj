"""Provider construction with explicit, bounded network policy."""

from os import getenv
from urllib.parse import urlsplit

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.core.config import Settings, settings


class LLMConfigurationError(ValueError):
    """Invalid provider configuration, before any provider request is attempted."""


MAX_RETRIES = 0
MAX_TIMEOUT_SECONDS = 30


def create_llm(config: Settings | None = None) -> BaseChatModel:
    """Construct a chat model; validation does not contact the provider."""
    selected = config if config is not None else settings
    provider = selected.llm_provider.strip().lower()
    if provider not in {"openai", "groq", "deepseek", "gemini"}:
        raise LLMConfigurationError(f"Unsupported LLM provider: {provider}")

    key = {
        "openai": selected.openai_api_key,
        "groq": selected.groq_api_key,
        "deepseek": selected.deepseek_api_key,
        "gemini": selected.gemini_api_key,
    }[provider]
    if not key or not key.strip():
        field = {
            "openai": "OPENAI_API_KEY",
            "groq": "GROQ_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "gemini": "GEMINI_API_KEY",
        }[provider]
        raise LLMConfigurationError(f"{field} is required for {provider}")
    if not 0 < selected.llm_timeout <= MAX_TIMEOUT_SECONDS:
        raise LLMConfigurationError(f"LLM_TIMEOUT must be between 1 and {MAX_TIMEOUT_SECONDS} seconds")

    endpoint = selected.deepseek_base_url or "https://api.deepseek.com"
    if provider == "deepseek":
        try:
            parsed = urlsplit(endpoint)
            valid_endpoint = (
                parsed.scheme == "https"
                and bool(parsed.hostname)
                and not parsed.username
                and not parsed.password
                and not parsed.query
                and not parsed.fragment
            )
        except ValueError:
            valid_endpoint = False
        if not valid_endpoint:
            raise LLMConfigurationError(
                "DEEPSEEK_BASE_URL must be an HTTPS endpoint without credentials, query, or fragment"
            )

    if provider == "gemini":
        model = selected.llm_model.strip()
        if not model.startswith("gemini-"):
            raise LLMConfigurationError("LLM_MODEL must explicitly select a Gemini model (gemini-...)")
        # The Google SDK can re-read backend flags even when the LangChain model
        # receives vertexai=False. Reject conflicting flags before constructing it.
        if any(
            getenv(name, "").strip().lower() in {"true", "1", "yes"}
            for name in ("GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_GENAI_USE_ENTERPRISE")
        ):
            raise LLMConfigurationError(
                "Gemini requires the Developer API; unset GOOGLE_GENAI_USE_VERTEXAI and GOOGLE_GENAI_USE_ENTERPRISE"
            )
        return ChatGoogleGenerativeAI(
            model=model,
            api_key=SecretStr(key),
            vertexai=False,
            max_retries=MAX_RETRIES,
            timeout=selected.llm_timeout,
            max_tokens=selected.llm_max_tokens,
        )
    if provider == "groq":
        return ChatGroq(
            model=selected.llm_model,
            api_key=SecretStr(key),
            streaming=True,
            max_retries=MAX_RETRIES,
            timeout=selected.llm_timeout,
            max_tokens=selected.llm_max_tokens,
        )
    if provider == "deepseek":
        return ChatOpenAI(
            model=selected.llm_model if "deepseek" in selected.llm_model.lower() else "deepseek-chat",
            api_key=SecretStr(key),
            streaming=True,
            max_retries=MAX_RETRIES,
            timeout=selected.llm_timeout,
            base_url=endpoint,
            # ChatOpenAI renames its token field to OpenAI's newer spelling;
            # DeepSeek's compatible endpoint requires max_tokens in the body.
            extra_body={"max_tokens": selected.llm_max_tokens},
        )
    return ChatOpenAI(
        model="gpt-4o-mini" if selected.llm_model == "openai/gpt-oss-120b" else selected.llm_model,
        api_key=SecretStr(key),
        streaming=True,
        max_retries=MAX_RETRIES,
        timeout=selected.llm_timeout,
        max_completion_tokens=selected.llm_max_tokens,
    )
