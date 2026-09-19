from langchain_ollama import ChatOllama

from painting_agents.config import settings


def create_ollama_model() -> ChatOllama:
    """Create the configured local Ollama chat model."""

    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.ollama_temperature,
    )