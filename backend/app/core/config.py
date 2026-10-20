from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "deepseek"
    llm_model: str = "deepseek-chat"
    deepseek_api_key: str = Field(default="", repr=False)
    deepseek_base_url: str = ""
    openai_api_key: str = Field(
        default="", repr=False, validation_alias=AliasChoices("OPENAI_API_KEY", "OPEN_AI_API_KEY")
    )
    groq_api_key: str = Field(default="", repr=False)
    gemini_api_key: str = Field(default="", repr=False)
    langchain_api_key: str = Field(default="", repr=False)
    langchain_tracing_v2: bool = False
    langchain_project: str = "osj-demo"
    llm_timeout: int = 30
    llm_max_tokens: int = 600

    # Hybrid Retrieval
    HYBRID_K_DENSE: int = 20
    HYBRID_K_FINAL: int = 5
    HYBRID_ALPHA: float = 0.7
    # Explicitly opt in to a populated server index; local mode remains default.
    qdrant_path: str = "qdrant_db"
    qdrant_url: str = ""
    qdrant_api_key: str = Field(default="", repr=False)

    # CORS configuration
    cors_origins: list[str] = ["*"]

    # Waitlist, Database, and Cache
    database_url: str = Field(default="", repr=False)
    redis_url: str = "redis://localhost:6379/0"
    resend_api_key: str = Field(default="", repr=False)
    resend_from_email: str = "noreply@example.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        from typing import cast

        if isinstance(value, str):
            clean = value.strip()
            if not clean:
                return ["*"]
            if clean.startswith("[") and clean.endswith("]"):
                import json

                parsed_json: object = json.loads(clean)
                if isinstance(parsed_json, list):
                    items = cast(list[object], parsed_json)
                    return [str(item).strip() for item in items if str(item).strip()]
            return [origin.strip() for origin in clean.split(",") if origin.strip()]
        if isinstance(value, list):
            items = cast(list[object], value)
            return [str(item).strip() for item in items if str(item).strip()]
        return ["*"]

    @model_validator(mode="after")
    def validate_qdrant_mode(self) -> "Settings":
        if self.qdrant_url and self.qdrant_path != "qdrant_db":
            raise ValueError("QDRANT_URL and a custom QDRANT_PATH cannot both be set")
        return self


settings = Settings()
