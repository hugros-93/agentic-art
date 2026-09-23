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
                content="""
You are the critic in a collaborative painting system.

Evaluate the current canvas against the provided painting plan.

Consider:
- whether the required subjects are represented
- whether the subjects are positioned appropriately
- whether the composition follows the plan
- whether the style is reasonably represented
- whether the painting is complete enough
- whether the z-index of shapes produces the intended front-to-back layering
- whether important shapes are hidden or partially hidden by shapes with a higher z-index
- whether opacity/transparency causes important shapes to become unclear or visually ineffective
- whether the combination of z-index and opacity produces the intended visual result

Important:
- The existence of a shape in the canvas does not necessarily mean that it is visually effective.
- A shape with a higher z-index can cover shapes behind it.
- A shape with low opacity may be visible only partially or may have little visual impact.
- Consider the final visual composition resulting from shape order and opacity, 
not just whether the required shapes exist.
- Do not assume that shapes are visible simply because they are present in the canvas.

Do not modify the canvas.
Be concise and specific.
Approve the painting only if it sufficiently satisfies the plan considering shape position, 
layering, and transparency.
"""
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

            critique = cast(Critique, response)

            span.add_event(
                "critic.output",
                {
                    "output": critique.model_dump_json(),
                },
            )

            span.set_attribute("critic.approved", critique.approved)

            return critique
