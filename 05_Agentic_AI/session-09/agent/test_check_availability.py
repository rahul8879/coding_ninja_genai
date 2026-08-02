import asyncio
from nodes.check_availability import check_panel_availability


async def main():
    # Using the output from the previous node's test as input here —
    # this simulates how LangGraph will chain the two nodes together.
    state = {
        "job_id": "REQ-101",
        "panel": [
            {"name": "Vihaan Tiwari", "email": "vihaantiwari224@gmail.com", "role": "Senior Engineer"},
            {"name": "Dipanjali Shukla", "email": "dipanjalishukla10@gmail.com", "role": "Tech Lead"},
        ],
    }
    result = await check_panel_availability(state)
    print(result)


asyncio.run(main())