import asyncio
from mcp_tools import get_client, tools_session

async def main():
    client = get_client("ats")
    for server_name in ["ats", "calendar", "email"]:
        async with tools_session(client, server_name) as tools:
            for tool in tools:
                # Use each tool here
                print(f"  - {tool.name}")

asyncio.run(main())