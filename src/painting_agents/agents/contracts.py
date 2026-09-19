from pydantic import BaseModel, Field


class PaintingPlan(BaseModel):
    """Structured plan produced by the Director."""

    title: str = Field(
        description="A short title for the painting.",
    )
    description: str = Field(
        description="A concise description of the intended painting.",
    )
    style: str = Field(
        description="The visual style of the painting.",
    )

class ArtistResult(BaseModel):
    """Result reported by an Artist after working on the canvas."""

    summary: str = Field(
        description="A concise description of the work completed.",
    )

    shapes_created: list[str] = Field(
        default_factory=list,
        description="IDs of shapes created by the artist.",
    )