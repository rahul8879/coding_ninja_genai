from typing import List

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    generate_answer: bool = True


class Source(BaseModel):
    id: str
    title: str
    text: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    latency_ms: float
