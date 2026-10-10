import asyncio
import time

TOTAL_REQUESTS = 50
CONCURRENCY_LIMIT = 10 # you can change it --> and note your observations
PROCESSING_SECONDS = 5


# Completed requests: 50
# Total duration: 125.0s
# Average throughput: 0.40 req/sec

async def handle_request(request_id,semaphore, start_time):
    arrived_at = time.perf_counter()

    print(f"Request {request_id} arrived at {arrived_at - start_time:.2f} seconds")

    # here only 2 request will go inside your code blocl ---> 8 request will wait.
    async with semaphore:
        processing_started = time.perf_counter()
        queue_wait = processing_started - arrived_at

        print(f"Request {request_id} processing started at {processing_started - start_time:.2f} seconds after waiting for {queue_wait:.2f} seconds in the queue")
        await asyncio.sleep(PROCESSING_SECONDS)  # Simulate processing time
        completed_at = time.perf_counter()
        latency = completed_at - arrived_at

        print(f"Request {request_id} completed at {completed_at - start_time:.2f} seconds with latency {latency:.2f} seconds")
        print(
            f"Request {request_id:02d} FINISHED "
            f"at {completed_at - start_time:.1f}s "
            f"| Total latency: {latency:.1f}s"
        )



async def main():
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    start_time = time.perf_counter()

    # schedule all 10 request together
    await asyncio.gather(
        *[handle_request(i, semaphore, start_time) for i in range(1, TOTAL_REQUESTS + 1)]
    )

    elapsed = time.perf_counter() - start_time
    print("\n--- Results ---")
    print(f"Completed requests: {TOTAL_REQUESTS}")
    print(f"Total duration: {elapsed:.1f}s")
    print(f"Average throughput: {TOTAL_REQUESTS / elapsed:.2f} req/sec")

if __name__ == "__main__":
    asyncio.run(main())

