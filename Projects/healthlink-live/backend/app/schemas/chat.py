from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class ChatRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    message: str = Field(
        min_length=1,
        max_length=2000,
    )

class ChatResponse(BaseModel):
    # Shared by /chat and the conversation message endpoint.
    reply: str
    booking_proposal: dict[str, Any] | None = None
