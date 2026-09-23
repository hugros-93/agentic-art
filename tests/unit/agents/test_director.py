from unittest.mock import Mock

from painting_agents.agents.contracts import PaintingPlan
from painting_agents.agents.director import DirectorAgent


def test_director_creates_painting_plan() -> None:
    expected_plan = PaintingPlan(
        title="Mountain Sunset",
        description="A peaceful sunset over a mountain village.",
        style="warm and atmospheric",
    )

    structured_model = Mock()
    structured_model.invoke.return_value = expected_plan

    model = Mock()
    model.with_structured_output.return_value = structured_model

    director = DirectorAgent(model=model)

    plan = director.create_plan("Paint a peaceful sunset over a mountain village.")

    assert plan == expected_plan

    model.with_structured_output.assert_called_once_with(
        PaintingPlan,
    )

    structured_model.invoke.assert_called_once()
