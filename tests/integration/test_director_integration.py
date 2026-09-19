from painting_agents.agents.contracts import PaintingPlan
from painting_agents.agents.director import DirectorAgent


def test_director_creates_plan_with_qwen() -> None:
    director = DirectorAgent()

    plan = director.create_plan(
        "Paint a peaceful sunset over a small mountain village."
    )

    assert isinstance(plan, PaintingPlan)
    assert plan.title
    assert plan.description
    assert plan.style