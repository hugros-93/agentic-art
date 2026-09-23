from pydantic import BaseModel, Field

from painting_agents.domain.painting import Painting


class PaintingOperation(BaseModel):
    agent_id: str
    operation: str
    details: dict[str, object] = Field(default_factory=dict)


class PaintingSession(BaseModel):
    id: str
    painting: Painting
    iteration: int = 0
    operations: list[PaintingOperation] = Field(default_factory=list)

    def record_operation(
        self,
        *,
        agent_id: str,
        operation: str,
        details: dict[str, object] | None = None,
    ) -> None:
        self.operations.append(
            PaintingOperation(
                agent_id=agent_id,
                operation=operation,
                details=details or {},
            )
        )

    def next_iteration(self) -> None:
        self.iteration += 1
