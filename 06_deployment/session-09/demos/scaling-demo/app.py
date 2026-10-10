import asyncio
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

INSTANCE_NAME = os.getenv("INSTANCE_NAME", "app-1")

# Maximum simultaneous processing operations per app process.
PROCESSING_LIMIT = 2

# Simulated LLM response time.
PROCESSING_SECONDS = 5

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.processing_slots = asyncio.Semaphore(PROCESSING_LIMIT)
    yield

app = FastAPI(
    title="Policy Assistant Scaling Demo",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "instance": INSTANCE_NAME,
    }


class ChatInput(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@app.post("/chat")
async def chat(body: ChatInput, request: Request):
    # Timing begins when this endpoint starts handling the request.
    arrived_at = time.perf_counter()

    # Wait here if both processing slots are occupied.
    async with request.app.state.processing_slots:
        started_at = time.perf_counter()
        queue_wait = started_at - arrived_at

        print(
            f"[{INSTANCE_NAME}] START "
            f"| queue_wait={queue_wait:.2f}s",
            flush=True,
        )

        # Simulate waiting for an external LLM.
        # No real LLM call or policy retrieval happens in this demo.
        await asyncio.sleep(PROCESSING_SECONDS)

        finished_at = time.perf_counter()

    processing_time = finished_at - started_at
    total_time = finished_at - arrived_at

    print(
        f"[{INSTANCE_NAME}] END "
        f"| total={total_time:.2f}s",
        flush=True,
    )

    return {
        "instance": INSTANCE_NAME,
        "question": body.question,
        "answer": "Simulated policy answer for the scaling demo.",
        "queue_wait_seconds": round(queue_wait, 2),
        "processing_seconds": round(processing_time, 2),
        "handler_total_seconds": round(total_time, 2),
    }