from typing import TypedDict

from painting_agents.agents.contracts import ArtistResult, Critique, PaintingPlan


class PaintingGraphState(TypedDict, total=False):
    request: str
    request_id: str
    plan: PaintingPlan
    artist_result: ArtistResult
    critique: Critique
    iteration: int
    max_iterations: int

    # Rendering checkpoint for the current iteration.
    image_path: str
