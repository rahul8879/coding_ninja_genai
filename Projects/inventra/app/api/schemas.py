from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User question for Inventra."
    )

    thread_id: str = Field(
        ...,
        min_length=1,
        description="Conversation/session identifier."
    )


class ChatResponse(BaseModel):
    thread_id: str
    answer: str

    intent: Optional[str] = None
    reorder_needed: Optional[bool] = None

    sku: Optional[str] = None
    region: Optional[str] = None
    target_date: Optional[str] = None
