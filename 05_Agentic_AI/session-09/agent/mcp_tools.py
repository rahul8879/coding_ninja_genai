import json
from contextlib import asynccontextmanager
from config import MCP_SERVERS
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

def get_client():
    return MultiServerMCPClient(MCP_SERVERS)


@asynccontextmanager
async def tools_session(client: MultiServerMCPClient, server_name: str):
    async with client.session(server_name) as session:
        tools = await load_mcp_tools(session)
        yield tools


# will explore the reasoning behind below functions ??
def _parse_text_block(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text
    

def parse_tool_result(result):
    if isinstance(result, list):
        return [_parse_text_block(block["text"]) for block in result]
    if isinstance(result, dict) and "text" in result:
        return _parse_text_block(result["text"])
    return result


