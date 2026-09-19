import asyncio
import time

from fastapi import FastAPI, Query

app = FastAPI(title="Bad Async Blocking Example")

def log(message: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}",flush=True)


@app.get("/bad")
async def bad(
    request_id : int = Query(default=1, description="Request ID"),
    seconds: float = Query(default=3.0, description="Seconds to wait")
):
    started = time.perf_counter()
    log(f"Request {request_id} started, waiting for {seconds} seconds...")
    log(f"BAD #{request_id} START")
    time.sleep(seconds)  # This is a blocking call or block the event loop
    log(f"BAD #{request_id} END"
    )
    return {
        "request_id": request_id,
        "style": "async def + time.sleep()",
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }

@app.get("/good")
async def good(
    request_id: int = Query(default=1),
    seconds: float = Query(default=3.0, ge=0, le=10),
):
    started = time.perf_counter()
    log(f"GOOD #{request_id} START")
    await asyncio.sleep(seconds)
    log(f"GOOD #{request_id} END")
    return {
        "request_id": request_id,
        "style": "async def + await asyncio.sleep()",
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }

