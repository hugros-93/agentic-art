from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from painting_agents.mcp.results import parse_mcp_result


class PaintingMCPClient:
    def __init__(self, server_script: Path) -> None:
        self.client = MultiServerMCPClient(
            {
                "painting": {
                    "transport": "stdio",
                    "command": "uv",
                    "args": [
                        "run",
                        "python",
                        str(server_script),
                    ],
                },
            }
        )

        self._session_context = None
        self._session = None
        self._tools: list[BaseTool] | None = None

    async def start(self) -> None:
        if self._session is not None:
            return

        self._session_context = self.client.session("painting")
        self._session = await self._session_context.__aenter__()

        self._tools = await load_mcp_tools(self._session)

    async def close(self) -> None:
        if self._session_context is not None:
            await self._session_context.__aexit__(None, None, None)

        self._session_context = None
        self._session = None
        self._tools = None

    async def get_tools(self) -> list[BaseTool]:
        await self.start()

        assert self._tools is not None
        return self._tools

    async def get_canvas(self) -> dict[str, Any]:
        tools = await self.get_tools()

        get_canvas_tool = next(tool for tool in tools if tool.name == "get_canvas")

        result = await get_canvas_tool.ainvoke({})

        return parse_mcp_result(result)
