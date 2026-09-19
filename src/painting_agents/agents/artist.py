from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from painting_agents.agents.contracts import ArtistResult, PaintingPlan
from painting_agents.models.ollama import create_ollama_model


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
                "6. Work directly on the canvas; do not merely describe "
                "what could be drawn.\n"
            ),
        )

    async def paint(self, plan: PaintingPlan) -> ArtistResult:
        result = await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Execute this painting plan:\n\n"
                            f"{plan.model_dump_json(indent=2)}"
                        ),
                    }
                ]
            }
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