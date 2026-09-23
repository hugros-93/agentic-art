from pathlib import Path
from typing import Any

import pytest

from painting_agents.agents.contracts import (
    ArtistResult,
    Critique,
    PaintingPlan,
)
from painting_agents.graph.workflow import build_painting_graph


class FakeDirector:
    def create_plan(self, request: str) -> PaintingPlan:
        return PaintingPlan(
            title="Test painting",
            description=request,
            style="minimal geometric"
        )


class FakeArtist:
    async def paint(self, plan: PaintingPlan, critique: Critique) -> ArtistResult:
        return ArtistResult(
            summary="Created test painting.",
            shapes_created=["sun", "ground"],
        )


class FakeCritic:
    def __init__(self, approvals: list[bool]) -> None:
        self.approvals = approvals
        self.calls = 0

    def critique(
        self,
        plan: PaintingPlan,
        canvas: dict[str, Any],
    ) -> Critique:
        approved = self.approvals[min(self.calls, len(self.approvals) - 1)]
        self.calls += 1

        return Critique(
            approved=approved,
            assessment="Test assessment.",
            issues=[] if approved else ["Test issue."],
            recommendations=[] if approved else ["Test recommendation."],
        )


class FakeMCPClient:
    async def get_canvas(self) -> dict[str, Any]:
        return {
            "width": 1024,
            "height": 768,
            "shapes": [],
        }


@pytest.mark.asyncio
async def test_graph_ends_when_critic_approves(tmp_path: Path) -> None:
    graph = build_painting_graph(
        mcp_client=FakeMCPClient(),  # type: ignore[arg-type]
        director=FakeDirector(),  # type: ignore[arg-type]
        artist=FakeArtist(),  # type: ignore[arg-type]
        critic=FakeCritic([True]),  # type: ignore[arg-type]
        output_dir=tmp_path,  # type: ignore[arg-type]
    )

    result = await graph.ainvoke(
        {
            "request": "Create a simple sunset.",
            "max_iterations": 3,
        }
    )

    assert result["plan"].title == "Test painting"
    assert result["artist_result"].shapes_created == ["sun", "ground"]
    assert result["critique"].approved is True
    assert result["iteration"] == 1


@pytest.mark.asyncio
async def test_graph_loops_when_critic_rejects(tmp_path: Path) -> None:
    critic = FakeCritic([False, True])

    graph = build_painting_graph(
        mcp_client=FakeMCPClient(),  # type: ignore[arg-type]
        director=FakeDirector(),  # type: ignore[arg-type]
        artist=FakeArtist(),  # type: ignore[arg-type]
        critic=critic,  # type: ignore[arg-type]
        output_dir=tmp_path,  # type: ignore[arg-type]
    )

    result = await graph.ainvoke(
        {
            "request": "Create a simple sunset.",
            "max_iterations": 3,
        }
    )

    assert result["critique"].approved is True
    assert result["iteration"] == 2
    assert critic.calls == 2


@pytest.mark.asyncio
async def test_graph_stops_at_max_iterations(tmp_path: Path) -> None:
    critic = FakeCritic([False])

    graph = build_painting_graph(
        mcp_client=FakeMCPClient(),  # type: ignore[arg-type]
        director=FakeDirector(),  # type: ignore[arg-type]
        artist=FakeArtist(),  # type: ignore[arg-type]
        critic=critic,  # type: ignore[arg-type]
        output_dir=tmp_path,  # type: ignore[arg-type]
    )

    result = await graph.ainvoke(
        {
            "request": "Create a simple sunset.",
            "max_iterations": 2,
        }
    )

    assert result["critique"].approved is False
    assert result["iteration"] == 2
    assert critic.calls == 2