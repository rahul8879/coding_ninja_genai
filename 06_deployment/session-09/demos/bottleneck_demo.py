import asyncio
import time

TOTAL_REQUESTS = 10

# Change this between runs: 1, 2, then 10.
APP_LIMIT = 10
# Our simulated LLM service can process only 2 calls at once.
LLM_LIMIT = 10
LLM_DELAY = 5


async def handle_request(
    request_id,
    app_slots,
    llm_slots,
    start_time,
):
    # First gate: application processing slots.
    async with app_slots:
        print(
            f"{request_id:02d}: Entered application; "
            "waiting for an LLM slot"
        )

        # Second gate: simulated LLM processing slots.
        async with llm_slots:
            print(f"{request_id:02d}: LLM processing started")

            await asyncio.sleep(LLM_DELAY)

            elapsed = time.perf_counter() - start_time
            print(f"{request_id:02d}: Completed at {elapsed:.1f}s")


async def main():
    app_slots = asyncio.Semaphore(APP_LIMIT)
    llm_slots = asyncio.Semaphore(LLM_LIMIT)

    start_time = time.perf_counter()

    await asyncio.gather(
        *(
            handle_request(
                request_id,
                app_slots,
                llm_slots,
                start_time,
            )
            for request_id in range(1, TOTAL_REQUESTS + 1)
        )
    )

    elapsed = time.perf_counter() - start_time

    print(f"\nApp limit: {APP_LIMIT}")
    print(f"LLM limit: {LLM_LIMIT}")
    print(f"Total time: {elapsed:.1f}s")
    print(f"Throughput: {TOTAL_REQUESTS / elapsed:.2f} req/sec")


if __name__ == "__main__":
    asyncio.run(main())