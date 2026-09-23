import pytest
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from pydantic import SecretStr

from painting_agents.config import Settings
from painting_agents.models.chat import create_chat_model


def test_create_ollama_model():
    settings = Settings(
        llm_provider="ollama",
        ollama_model="ministral-3:3b",
        ollama_base_url="http://localhost:11434",
        ollama_temperature=0.2,
    )

    model = create_chat_model(settings)

    assert isinstance(model, ChatOllama)
    assert model.model == "ministral-3:3b"
    assert model.base_url == "http://localhost:11434"
    assert model.temperature == 0.2


def test_create_mistral_model():
    settings = Settings(
        llm_provider="mistral",
        mistral_model="mistral-large-latest",
        mistral_api_key=SecretStr("test-key"),
        mistral_temperature=0.2,
    )

    model = create_chat_model(settings)

    assert isinstance(model, ChatMistralAI)
    assert model.model == "mistral-large-latest"
    assert model.temperature == 0.2


def test_mistral_requires_api_key():
    settings = Settings(
        llm_provider="mistral",
        mistral_api_key=None,
    )

    with pytest.raises(
        ValueError,
        match="MISTRAL_API_KEY must be configured when using Mistral",
    ):
        create_chat_model(settings)


def test_unknown_provider():
    settings = Settings(
        llm_provider="unknown",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported LLM provider",
    ):
        create_chat_model(settings)