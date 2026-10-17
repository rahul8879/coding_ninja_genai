from app.llm_client import generate_reply
import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request
from openai import APIError, APITimeoutError, RateLimitError
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from app.chat_routes import ChatRequest, ChatResponse
from app.conversation_service import (
    ConversationNotFound,
    ConversationBusy,
    create_conversation,
    get_messages,
    prepare_turn,
    complete_turn,
    fail_turn,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])
logger = logging.getLogger(__name__)


@router.post("", status_code=201)
def start_conversation():
    try:
        return create_conversation()
    except SQLAlchemyError:
        raise HTTPException(
            503, "Could not create conversation. Database unavailable."
        ) from None




@router.get("/{conversation_id}/messages")
def read_messages(conversation_id: UUID):
    try:
        return {
            "conversation_id": str(conversation_id),
            "messages": get_messages(str(conversation_id)),
        }
    except ConversationNotFound:
        raise HTTPException(404, "Conversation not found") from None
    except SQLAlchemyError:
        raise HTTPException(
            503, "Could not load conversation. Database unavailable."
        ) from None


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(conversation_id: UUID, payload: ChatRequest, request: Request):
    try:
        message_id, history = await run_in_threadpool(
            prepare_turn, str(conversation_id), payload.message
        )
    except ConversationNotFound:
        raise HTTPException(404, "Conversation not found") from None
    except ConversationBusy:
        raise HTTPException(
            409, "A message is already being processed in this conversation."
        ) from None
    except SQLAlchemyError:
        raise HTTPException(503, "Could not save your message.") from None
    try:
        reply = await generate_reply(
            client=request.app.state.llm_client,
            message=payload.message,
            history=history,
        )
        await run_in_threadpool(complete_turn, message_id, reply)
        return ChatResponse(reply=reply)
    except (APIError, ValueError, SQLAlchemyError) as exc:
        logger.error(
            "conversation_turn_failed message_id=%s type=%s request_id=%s",
            message_id,
            type(exc).__name__,
            getattr(exc, "request_id", None),
        )
        try:
            await run_in_threadpool(fail_turn, message_id)
        except SQLAlchemyError:
            logger.error("turn_status_update_failed message_id=%s", message_id)
        if isinstance(exc, APITimeoutError):
            status, detail = 504, "AI response timed out."
        elif isinstance(exc, RateLimitError):
            status, detail = 503, "AI provider limit reached."
        elif isinstance(exc, SQLAlchemyError):
            status, detail = 503, "Could not save the AI response."
        else:
            status, detail = 502, "AI request failed."
        raise HTTPException(status, detail) from None
