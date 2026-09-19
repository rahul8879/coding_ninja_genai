import asyncio
import time
import httpx

URL = "http://127.0.0.1:8000/stream"

async def main():
    started = time.perf_counter()
    first_chunk = True

    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("GET", URL) as response:
            response.raise_for_status()

            async for chunk in response.aiter_text():
                if not chunk:
                    continue

                if first_chunk:
                    print(f"\nTTFT: {time.perf_counter() - started:.3f}s\n")
                    first_chunk = False

                print(chunk, end="", flush=True)

    print(f"\n\nTOTAL: {time.perf_counter() - started:.3f}s")

if __name__ == "__main__":
    asyncio.run(main())
