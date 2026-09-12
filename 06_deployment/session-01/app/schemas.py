from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    prompt_version: Literal["v1", "v2"] | None = None
    # False benchmarks API + retrieval without paying for an LLM call.
    generate_answer: bool = True


class Source(BaseModel):
    file: str
    chunk: int | None = None


class ChatResponse(BaseModel):
    answer: str
    prompt_version: str
    model: str
    latency_ms: float
    sources: list[Source]
    request_id: str
    # mode: Literal["rag", "retrieval_only"]
