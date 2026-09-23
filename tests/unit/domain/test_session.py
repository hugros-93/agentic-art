from painting_agents.domain.factory import create_painting_session
from painting_agents.mcp.tools.canvas import CanvasTools


def test_create_painting_session() -> None:
    session = create_painting_session(
        title="Sunset",
        width=800,
        height=600,
    )

    assert session.id
    assert session.painting.id
    assert session.painting.title == "Sunset"
    assert session.painting.canvas.width == 800
    assert session.painting.canvas.height == 600
    assert session.iteration == 0
    assert session.operations == []


def test_record_operation() -> None:
    session = create_painting_session(title="Sunset")

    session.record_operation(
        agent_id="artist-1",
        operation="add_circle",
        details={
            "shape_id": "sun",
        },
    )

    assert len(session.operations) == 1
    assert session.operations[0].agent_id == "artist-1"
    assert session.operations[0].operation == "add_circle"
    assert session.operations[0].details["shape_id"] == "sun"


def test_next_iteration() -> None:
    session = create_painting_session(title="Sunset")

    session.next_iteration()
    session.next_iteration()

    assert session.iteration == 2


def test_canvas_tools_operate_on_session() -> None:
    session = create_painting_session(title="Test Painting")
    tools = CanvasTools(session)

    result = tools.add_circle(
        shape_id="sun",
        x=500,
        y=150,
        radius=75,
        fill="#FFD700",
    )

    assert result["success"] is True
    assert len(session.painting.canvas.shapes) == 1
    assert session.painting.canvas.shapes[0].id == "sun"

    assert len(session.operations) == 1
    assert session.operations[0].operation == "add_circle"


def test_session_records_operations() -> None:
    session = create_painting_session(
        title="Test painting",
    )

    session.record_operation(
        agent_id="artist",
        operation="add_circle",
        details={"shape_id": "sun"},
    )

    assert len(session.operations) == 1

    operation = session.operations[0]

    assert operation.agent_id == "artist"
    assert operation.operation == "add_circle"
    assert operation.details["shape_id"] == "sun"


def test_session_iteration() -> None:
    session = create_painting_session(
        title="Test painting",
    )

    assert session.iteration == 0

    session.next_iteration()

    assert session.iteration == 1
