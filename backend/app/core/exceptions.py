"""Shared core exceptions for the future feature slices."""


class ConfigurationError(ValueError):
    """Raised when application settings cannot support a requested operation."""


class ExternalServiceError(RuntimeError):
    """Raised when an upstream dependency fails within its request boundary."""


class LLMProviderError(ExternalServiceError):
    """Sanitized inference failure with an optional upstream HTTP status."""

    def __init__(self, *, status_code: int | None = None) -> None:
        super().__init__("Chat provider unavailable")
        self.status_code = status_code
