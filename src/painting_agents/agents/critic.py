from typing import Any, cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from opentelemetry import trace

from painting_agents.agents.contracts import Critique, PaintingPlan
from painting_agents.config import Settings
from painting_agents.models.chat import create_chat_model
from painting_agents.observability.llm import (
    record_llm_prompt,
    record_llm_response,
)

tracer = trace.get_tracer(__name__)


class CriticAgent:
    def __init__(self, model: BaseChatModel | None = None) -> None:
        if model is None:
            model = create_chat_model(Settings())

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

        with tracer.start_as_current_span("llm.call") as span:
            span.set_attribute("llm.agent", "critic")
            span.set_attribute("llm.operation", "critique")

            record_llm_prompt(span, messages)

            response = self.model.invoke(messages)

            if isinstance(response, AIMessage):
                record_llm_response(span, response)

            return cast(Critique, response)
