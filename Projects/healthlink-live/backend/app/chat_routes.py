import logging
from fastapi import APIRouter, HTTPException, Request
from openai import APIError, APITimeoutError, RateLimitError
from pydantic import BaseModel, ConfigDict, Field
from app.llm_client import generate_reply

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request):
    try:
        reply = await generate_reply(request.app.state.llm_client, payload.message)
        return ChatResponse(reply=reply)
    except APITimeoutError:
        raise HTTPException(504, "AI response timed out. Please try again.") from None
    except RateLimitError:
        raise HTTPException(
            503, "AI provider limit reached. Please try again later."
        ) from None
    except APIError as exc:
        logger.error(
            "llm_error type=%s status=%s request_id=%s cause=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
            getattr(exc, "request_id", None),
            type(exc.__cause__).__name__ if exc.__cause__ else None,
        )
        raise HTTPException(502, "AI provider request failed.") from None
    except ValueError:
        raise HTTPException(502, "AI did not return a complete response.") from None

