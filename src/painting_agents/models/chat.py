from langchain_core.language_models import BaseChatModel
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

from painting_agents.config import Settings


def create_chat_model(settings: Settings) -> BaseChatModel:
    """Create a chat model from application settings."""

    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=settings.ollama_temperature,
        )

    if settings.llm_provider == "mistral":
        if settings.mistral_api_key is None:
            raise ValueError(
                "MISTRAL_API_KEY must be configured when using Mistral."
            )

        return ChatMistralAI(
            model_name=settings.mistral_model,
            api_key=settings.mistral_api_key,
            temperature=settings.mistral_temperature,
            max_retries=settings.mistral_max_retries,
        )

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )