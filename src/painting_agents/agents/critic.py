from typing import Any, cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from painting_agents.agents.contracts import Critique, PaintingPlan
from painting_agents.models.ollama import create_ollama_model


class CriticAgent:
    def __init__(
        self,
        model: BaseChatModel | None = None,
    ) -> None:
        if model is None:
            model = create_ollama_model()

        self.model = model.with_structured_output(Critique)

    def critique(
        self,
        plan: PaintingPlan,
        canvas: dict[str, Any],
    ) -> Critique:
        messages = [
            SystemMessage(
                content=(
                    "You are the critic in a collaborative painting system.\n\n"
                    "Evaluate the current canvas against the provided painting plan.\n\n"
                    "Consider:\n"
                    "- whether the required subjects are represented\n"
                    "- whether the composition follows the plan\n"
                    "- whether the style is reasonably represented\n"
                    "- whether the painting is complete enough\n\n"
                    "Do not modify the canvas.\n"
                    "Be concise and specific.\n"
                    "Approve the painting only if it sufficiently satisfies the plan."
                )
            ),
            HumanMessage(
                content=(
                    "Painting plan:\n\n"
                    f"{plan.model_dump_json(indent=2)}\n\n"
                    "Current canvas:\n\n"
                    f"{canvas}"
                )
            ),
        ]

        result = self.model.invoke(messages)

        return cast(Critique, result)