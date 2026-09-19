from langgraph.graph import END, START, StateGraph

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.critic import CriticAgent
from painting_agents.agents.director import DirectorAgent
from painting_agents.graph.nodes import PaintingGraphNodes
from painting_agents.graph.state import PaintingGraphState
from painting_agents.mcp.client import PaintingMCPClient


def build_painting_graph(
    *,
    mcp_client: PaintingMCPClient,
    director: DirectorAgent,
    artist: ArtistAgent,
    critic: CriticAgent,
):
    nodes = PaintingGraphNodes(
        mcp_client=mcp_client,
        director=director,
        artist=artist,
        critic=critic,
    )

    graph = StateGraph(PaintingGraphState)

    graph.add_node("director", nodes.director_node)
    graph.add_node("artist", nodes.artist_node)
    graph.add_node("critic", nodes.critic_node)

    graph.add_edge(START, "director")
    graph.add_edge("director", "artist")
    graph.add_edge("artist", "critic")

    def critic_router(state: PaintingGraphState) -> str:
        critique = state.get("critique")
        if critique is None:
            raise ValueError("Critique is required before routing.")
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 3)

        if critique.approved:
            return "end"

        if iteration >= max_iterations:
            return "end"

        return "artist"

    graph.add_conditional_edges(
        "critic",
        critic_router,
        {
            "artist": "artist",
            "end": END,
        },
    )

    return graph.compile()