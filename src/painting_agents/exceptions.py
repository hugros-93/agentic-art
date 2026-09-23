class PaintingApplicationError(Exception):
    """Base exception for expected application failures."""


class LLMRateLimitError(PaintingApplicationError):
    """The LLM provider rate limit was exceeded."""


class LLMProviderError(PaintingApplicationError):
    """The LLM provider returned an unrecoverable error."""