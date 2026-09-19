import asyncio
import time
import httpx

BASE_URL = "http://127.0.0.1:8000"
REQUESTS = 10
WAIT_SECONDS = 3
async def hit(client, endpoint, request_id):
    started = time.perf_counter()
    response = await client.get(
        endpoint,
        params={"request_id": request_id, "seconds": WAIT_SECONDS},
    )
    response.raise_for_status()
    return request_id, time.perf_counter() - started

async def run(endpoint):
    print("\n" + "=" * 70)
    print(f"{endpoint}: {REQUESTS} concurrent requests x {WAIT_SECONDS}s")
    print("=" * 70)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60) as client:
        started = time.perf_counter()
        results = await asyncio.gather(
            *[hit(client, endpoint, i) for i in range(1, REQUESTS + 1)]
        )
        wall = time.perf_counter() - started
    for request_id, elapsed in results:
        print(f"Request {request_id}: {elapsed:.2f}s")
    print(f"TOTAL WALL TIME: {wall:.2f}s")


async def main():
    await run("/bad")
    await run("/good")

if __name__ == "__main__":
    asyncio.run(main())