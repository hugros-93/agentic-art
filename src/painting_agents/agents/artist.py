from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from painting_agents.agents.contracts import ArtistResult, PaintingPlan
from painting_agents.config import Settings
from painting_agents.models.chat import create_chat_model
from painting_agents.observability.agent_middleware import (
    OpenTelemetryAgentMiddleware,
)


class ArtistAgent:
    def __init__(
        self,
        tools: list[BaseTool],
        model: BaseChatModel | None = None,
    ) -> None:
        if model is None:
            model = create_chat_model(Settings())

        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt="""
You are an artist in a collaborative painting system.

Your job is to execute the provided painting plan on the canvas.

Tool usage rules:
- Inspect the tools available to you and use them to accomplish the plan.
- Treat the provided tool definitions and schemas as authoritative.
- Never invent a tool, argument, or capability.
- Use the appropriate available tool whenever an actual canvas modification
or inspection is required.
- You may make multiple tool calls.
- After receiving a tool result, evaluate whether additional tool calls are
required to complete the painting.
- Inspect the current canvas when necessary before modifying it.
- Do not claim that an operation was performed unless you actually called
the corresponding tool successfully.
- Preserve existing work unless modification or removal is necessary.
- When the painting is complete, stop calling tools and provide a short summary.
- When a tool requires a color, use a valid 6-digit hexadecimal. CSS color in the form #RRGGBB.
            """,
            middleware=[
                OpenTelemetryAgentMiddleware(),
            ],
        )

    async def paint(
        self,
        plan: PaintingPlan,
        critique: str | None = None,
    ) -> ArtistResult:
        content = f"Execute this painting plan:\n\n{plan.model_dump_json(indent=2)}"

        if critique is not None:
            content += (
                "\n\nPrevious critic feedback:\n\n"
                f"{critique}\n\n"
                "Address the critic's feedback while preserving the "
                "parts of the painting that already satisfy the plan."
            )

        result = await self.agent.ainvoke({"messages": [{"role": "user", "content": content}]})

        return self._build_result(result)

    @staticmethod
    def _build_result(result: dict[str, Any]) -> ArtistResult:
        # Temporary result extraction.
        # PaintingSession will eventually become the source of truth.
        messages = result.get("messages", [])
        created_shape_ids: list[str] = []

        for message in messages:
            if getattr(message, "type", None) != "tool":
                continue

            content = getattr(message, "content", None)

            if not isinstance(content, list):
                continue

            for block in content:
                if not isinstance(block, dict):
                    continue

                text = block.get("text")
                if not isinstance(text, str):
                    continue

                import json

                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    continue

                if not isinstance(parsed, dict):
                    continue

                shape = parsed.get("shape")
                if isinstance(shape, dict):
                    shape_id = shape.get("id")
                    if isinstance(shape_id, str):
                        created_shape_ids.append(shape_id)

        return ArtistResult(
            summary="Artist completed the requested canvas operations.",
            shapes_created=created_shape_ids,
        )
