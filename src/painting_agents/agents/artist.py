from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from painting_agents.agents.contracts import ArtistResult, PaintingPlan
from painting_agents.models.ollama import create_ollama_model
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
            model = create_ollama_model()

        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=(
                "You are an artist in a collaborative painting system.\n\n"
                "Your job is to turn the provided painting plan into "
                "concrete drawing operations on the canvas.\n\n"
                "Rules:\n"
                "1. Use the available drawing tools to create the painting.\n"
                "2. Prefer simple geometric compositions.\n"
                "3. Every shape must have a unique, descriptive ID.\n"
                "4. Do not claim that you created something unless you "
                "actually called the corresponding tool.\n"
                "5. Do not remove existing shapes unless explicitly necessary.\n"
                "6. Work directly on the canvas; do not merely describe\n"
                "7. Every visible shape must have an explicit color.\n"
                "8. Always provide a fill color for circles and rectangles.\n"
                "9. Use CSS hex colors such as #FFCC00, #3366CC, #228B22.\n"
                "10. Use contrasting colors for important subjects.\n"
                "11. Never leave a fill color unspecified.\n"
                "12. For lines, always provide an explicit stroke color.\n"
                "what could be drawn. "
            ),
            middleware=[
                    OpenTelemetryAgentMiddleware(),
                ]
        )

    async def paint(
        self,
        plan: PaintingPlan,
        critique: str | None = None,
    ) -> ArtistResult:
        content = (
            "Execute this painting plan:\n\n"
            f"{plan.model_dump_json(indent=2)}"
        )

        if critique is not None:
            content += (
                "\n\nPrevious critic feedback:\n\n"
                f"{critique}\n\n"
                "Address the critic's feedback while preserving the "
                "parts of the painting that already satisfy the plan."
            )

        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": content}]}
)

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