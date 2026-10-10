import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Barrier

# URL = "http://localhost:8001/chat"
URL = "http://localhost:8080/chat"
TOTAL_REQUESTS = 12



# All client threads wait here, then send requests together.
start_gate = Barrier(TOTAL_REQUESTS)


def send_request(request_id):
    payload = json.dumps({
        "question": f"Request {request_id}: What is the leave policy?"
    }).encode("utf-8")

    request = urllib.request.Request(
        URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start_gate.wait()
    started_at = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.load(response)

        return {
            "request_id": request_id,
            "client_seconds": time.perf_counter() - started_at,
            "result": result,
            "error": None,
        }

    except Exception as exc:
        return {
            "request_id": request_id,
            "client_seconds": time.perf_counter() - started_at,
            "result": None,
            "error": str(exc),
        }


def main():
    print(f"Sending {TOTAL_REQUESTS} concurrent requests to {URL}\n")
    started_at = time.perf_counter()
    successful = 0

    with ThreadPoolExecutor(max_workers=TOTAL_REQUESTS) as executor:
        futures = [
            executor.submit(send_request, request_id)
            for request_id in range(1, TOTAL_REQUESTS + 1)
        ]

        # Print each result as soon as that request completes.
        for future in as_completed(futures):
            row = future.result()

            if row["error"]:
                print(
                    f"Request {row['request_id']:02d} FAILED "
                    f"| {row['error']}"
                )
                continue

            successful += 1
            result = row["result"]

            print(
                f"Request {row['request_id']:02d} "
                f"| {result['instance']} "
                f"| Queue: {result['queue_wait_seconds']:.1f}s "
                f"| Processing: {result['processing_seconds']:.1f}s "
                f"| Client total: {row['client_seconds']:.1f}s"
            )

    elapsed = time.perf_counter() - started_at

    print("\n--- Summary ---")
    print(f"Successful: {successful}/{TOTAL_REQUESTS}")
    print(f"Wall time: {elapsed:.1f}s")
    print(f"Successful throughput: {successful / elapsed:.2f} req/sec")


if __name__ == "__main__":
    main()
