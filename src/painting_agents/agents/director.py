from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from opentelemetry import trace

from painting_agents.agents.contracts import PaintingPlan
from painting_agents.config import Settings
from painting_agents.models.chat import create_chat_model
from painting_agents.observability.llm import (
    record_llm_prompt,
    record_llm_response,
)

tracer = trace.get_tracer(__name__)


class DirectorAgent:
    def __init__(self, model: BaseChatModel | None = None) -> None:
        if model is None:
            model = create_chat_model(Settings())

        self.model = model.with_structured_output(PaintingPlan)

    def create_plan(self, request: str) -> PaintingPlan:
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

        with tracer.start_as_current_span("llm.call") as span:
            span.set_attribute("llm.agent", "director")
            span.set_attribute("llm.operation", "create_plan")

            record_llm_prompt(span, messages)

            response = self.model.invoke(messages)

            if isinstance(response, AIMessage):
                record_llm_response(span, response)

            return cast(PaintingPlan, response)