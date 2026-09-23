from typing import Any

from painting_agents.agents.contracts import Critique, PaintingPlan
from painting_agents.agents.critic import CriticAgent


class FakeCriticModel:
    def with_structured_output(self, schema: Any) -> "FakeCriticModel":
        return self

    def invoke(self, messages: Any) -> Critique:
        return Critique(
            approved=True,
            assessment="The painting satisfies the requested plan.",
        )


def test_critic_returns_structured_critique() -> None:
    critic = CriticAgent(model=FakeCriticModel())  # type: ignore[arg-type]

    plan = PaintingPlan(
        title="Simple sunset",
        description="A simple sunset over the ground.",
        style="minimal geometric",
    )

    canvas = {
        "width": 1024,
        "height": 768,
        "shapes": [
            {
                "id": "sun",
                "type": "circle",
            },
            {
                "id": "ground",
                "type": "line",
            },
        ],
    }

    result = critic.critique(plan, canvas)

    assert result.approved is True
    assert result.assessment
