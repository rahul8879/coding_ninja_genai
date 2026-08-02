import asyncio
from nodes.wait_for_reply import check_for_reply


async def main():
    state = {
        "candidate": {"name": "Saher Rizvi", "email": "saherrizvi1502@gmail.com"},
    }
    result = await check_for_reply(state)
    print(result)


asyncio.run(main())