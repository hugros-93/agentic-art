from painting_agents.agents.contracts import PaintingPlan
from painting_agents.config import Settings
from painting_agents.models.chat import create_chat_model


def test_qwen_can_create_painting_plan() -> None:
    model = create_chat_model(Settings())

    structured_model = model.with_structured_output(
        PaintingPlan,
    )

    plan = structured_model.invoke(
        """
        Create a painting plan for a peaceful sunset over a small
        mountain village. Keep the plan concise.
        """
    )

    assert isinstance(plan, PaintingPlan)
    assert plan.title
    assert plan.description
    assert plan.style
