from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from painting_agents.agents.contracts import PaintingPlan
from painting_agents.models.ollama import create_ollama_model


class DirectorAgent:
    """Creates a structured painting plan from a user's artistic request."""

    def __init__(self, model: BaseChatModel | None = None) -> None:
        if model is None:
            model = create_ollama_model()

        self.model = model.with_structured_output(PaintingPlan)

    def create_plan(self, request: str) -> PaintingPlan:
        """Turn a natural-language request into a painting plan."""

        messages = [
            SystemMessage(
                content=(
                    "You are the director of a collaborative painting system. "
                    "Turn the user's artistic request into a concise painting plan. "
                    "Do not draw anything. Do not discuss implementation details. "
                    "Return only the requested structured painting plan."
                )
            ),
            HumanMessage(content=request),
        ]

        result = self.model.invoke(messages)

        return cast(PaintingPlan, result)
