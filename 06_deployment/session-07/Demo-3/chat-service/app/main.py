import os
import time

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


RETRIEVAL_SERVICE_URL = os.getenv(
    "RETRIEVAL_SERVICE_URL",
    "http://retrieval-service:8001",
)

LLM_SERVICE_URL = os.getenv(
    "LLM_SERVICE_URL",
    "http://llm-service:8002",
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class Source(BaseModel):
    id: str
    title: str
    text: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    latency_ms: float


app = FastAPI(
    title="Chat Service",
    version="3.0.0",
    description="Orchestrates Retrieval Service and LLM Service.",
)


@app.get("/")
def root():
    return {
        "service": "chat-service",
        "architecture": "microservices",
        "stage": 3,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "chat-service",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    started = time.perf_counter()

    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    async with httpx.AsyncClient(timeout=30.0) as client:
        # ----------------------------------------------------
        # 1. CALL RETRIEVAL MICROSERVICE
        # ----------------------------------------------------
        try:
            retrieval_response = await client.post(
                f"{RETRIEVAL_SERVICE_URL}/retrieve",
                json={
                    "question": question,
                    "top_k": 2,
                },
            )
            retrieval_response.raise_for_status()

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Retrieval service unavailable: {exc}",
            )

        retrieval_payload = retrieval_response.json()
        documents = retrieval_payload["documents"]

        # ----------------------------------------------------
        # 2. CALL LLM MICROSERVICE
        # ----------------------------------------------------
        try:
            llm_response = await client.post(
                f"{LLM_SERVICE_URL}/generate",
                json={
                    "question": question,
                    "documents": documents,
                },
            )
            llm_response.raise_for_status()

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"LLM service unavailable: {exc}",
            )

        answer = llm_response.json()["answer"]

    latency_ms = (time.perf_counter() - started) * 1000

    print(
        {
            "service": "chat-service",
            "question": question,
            "documents_found": len(documents),
            "latency_ms": round(latency_ms, 2),
        }
    )

    return ChatResponse(
        question=question,
        answer=answer,
        sources=[Source(**doc) for doc in documents],
        latency_ms=round(latency_ms, 2),
    )
