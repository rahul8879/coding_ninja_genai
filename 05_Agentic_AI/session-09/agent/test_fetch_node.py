import asyncio
from nodes.fetch_candidates import fetch_candidates_and_panel


async def main():
    initial_state = {"job_id": "REQ-101"}
    result = await fetch_candidates_and_panel(initial_state)
    print(result)


asyncio.run(main())