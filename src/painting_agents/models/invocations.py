import httpx

from painting_agents.exceptions import (
    LLMProviderError,
    LLMRateLimitError,
)


def translate_llm_exception(exc: Exception) -> Exception:
    """Translate provider-specific exceptions into application exceptions."""

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code

        if status_code == 429:
            return LLMRateLimitError(
                "LLM provider rate limit exceeded after retries."
            )

        if status_code >= 500:
            return LLMProviderError(
                f"LLM provider returned HTTP {status_code}."
            )

        return LLMProviderError(
            f"LLM provider request failed with HTTP {status_code}."
        )

    return exc