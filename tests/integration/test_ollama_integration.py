import pytest

from painting_agents.models.ollama import create_ollama_model


@pytest.mark.integration
def test_ollama_can_generate() -> None:
    model = create_ollama_model()

    response = model.invoke(
        "Reply with exactly: painting model online"
    )

    assert response.content
    assert isinstance(response.content, str)