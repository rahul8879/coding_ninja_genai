import asyncio
from nodes.parse_reply import parse_reply


async def main():
    state = {
        "proposed_slots": [
            "2026-07-28T11:00:00",
            "2026-07-28T14:00:00",
            "2026-07-28T16:00:00",
        ],
        "candidate_reply_text": "I am available for 1st slot.",
        "clarification_attempts": 0,
    }
    result = await parse_reply(state)
    print(result)


asyncio.run(main())