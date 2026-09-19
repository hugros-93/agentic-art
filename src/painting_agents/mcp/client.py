from pathlib import Path

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


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

    async def get_tools(self) -> list[BaseTool]:
        return await self.client.get_tools(server_name="painting")