import asyncio
from nodes.propose_slots import propose_slots_via_email


async def main():
    state = {
        "candidate": {"name": "Tushar", "email": "saherrizvi1502@gmail.com"},
        "panel_provided_slots": [
            "2026-07-28T11:00:00",
            "2026-07-28T14:00:00",
            "2026-07-28T16:00:00",
        ],
    }
    result = await propose_slots_via_email(state)
    print(result)


asyncio.run(main())