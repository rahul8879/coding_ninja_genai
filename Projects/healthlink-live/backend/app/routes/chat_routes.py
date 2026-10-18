import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from openai import APIError, APITimeoutError, RateLimitError
from pydantic import BaseModel, ConfigDict, Field

from app.agent.llm_client import generate_reply


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

logger = logging.getLogger(__name__)


from app.schemas.chat import ChatRequest, ChatResponse





@router.post(
    "",
    response_model=ChatResponse,
    summary="Send a standalone message",
    description=(
        "Direct LLM response without saved conversation history "
        "or booking tools. For the care-navigation and booking "
        "workflow, use POST /conversations/{conversation_id}/messages."
    ),
)
async def chat(
    payload: ChatRequest,
    request: Request,
):
    try:
        reply = await generate_reply(
            request.app.state.llm_client,
            payload.message,
        )

        # This endpoint does not execute booking tools.
        return ChatResponse(
            reply=reply,
            booking_proposal=None,
        )

    except APITimeoutError:
        logger.warning("direct_chat_failed reason=timeout")

        raise HTTPException(
            status_code=504,
            detail="AI response timed out. Please try again.",
        ) from None

    except RateLimitError:
        logger.warning("direct_chat_failed reason=rate_limit")

        raise HTTPException(
            status_code=503,
            detail="AI provider limit reached. Please try again later.",
        ) from None

    except APIError as exc:
        logger.error(
            "direct_chat_failed "
            "type=%s status=%s request_id=%s cause=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
            getattr(exc, "request_id", None),
            (
                type(exc.__cause__).__name__
                if exc.__cause__
                else None
            ),
        )

        raise HTTPException(
            status_code=502,
            detail="AI provider request failed.",
        ) from None

    except ValueError:
        logger.warning(
            "direct_chat_failed reason=invalid_model_response"
        )

        raise HTTPException(
            status_code=502,
            detail="AI did not return a complete response.",
        ) from None