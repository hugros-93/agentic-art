import pytest

from painting_agents.config import Settings
from painting_agents.models.chat import create_chat_model


@pytest.mark.integration
def test_ollama_can_generate() -> None:
    model = create_chat_model(Settings())

    response = model.invoke(
        "Reply with exactly: painting model online"
    )

    assert response.content
    assert isinstance(response.content, str)