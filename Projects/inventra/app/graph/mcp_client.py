import sys
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient


_client: MultiServerMCPClient | None = None
_tools: dict[str, Any] | None = None


def get_mcp_client() -> MultiServerMCPClient:
    global _client

    if _client is None:
        python = sys.executable

        _client = MultiServerMCPClient(
            {
                "weather": {
                    "transport": "stdio",
                    "command": python,
                    "args": ["-m", "app.mcp.weather_server"],
                },
                "forecast": {
                    "transport": "stdio",
                    "command": python,
                    "args": ["-m", "app.mcp.forecast_server"],
                },
                "inventory": {
                    "transport": "stdio",
                    "command": python,
                    "args": ["-m", "app.mcp.inventory_server"],
                },
                "finance": {
                    "transport": "stdio",
                    "command": python,
                    "args": ["-m", "app.mcp.finance_server"],
                },
                "vendor": {
                    "transport": "stdio",
                    "command": python,
                    "args": ["-m", "app.mcp.vendor_server"],
                },
            },
            tool_name_prefix=True,
        )

    return _client


async def get_tools() -> dict[str, Any]:
    global _tools

    if _tools is None:
        loaded = await get_mcp_client().get_tools()
        _tools = {tool.name: tool for tool in loaded}

    return _tools
