import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from openai import APIError, APITimeoutError, RateLimitError
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from app.observability.tracing import run_agent_with_trace

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service import (
    ConversationNotFound,
    ConversationBusy,
    create_conversation,
    get_messages,
    prepare_turn,
    complete_turn,
    fail_turn,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)

logger = logging.getLogger(__name__)


@router.post("", status_code=201)
def start_conversation():
    try:
        return create_conversation()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Could not create conversation. Database unavailable.",
        ) from None


@router.get("/{conversation_id}/messages")
def read_messages(conversation_id: UUID):
    try:
        return {
            "conversation_id": str(conversation_id),
            "messages": get_messages(str(conversation_id)),
        }

    except ConversationNotFound:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        ) from None

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Could not load conversation. Database unavailable.",
        ) from None


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatResponse,
)
async def send_message(
    conversation_id: UUID,
    payload: ChatRequest,
    request: Request,
):
    # Save the user turn and load existing conversation history.
    try:
        message_id, history = await run_in_threadpool(
            prepare_turn,
            str(conversation_id),
            payload.message,
        )

    except ConversationNotFound:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        ) from None

    except ConversationBusy:
        raise HTTPException(
            status_code=409,
            detail=(
                "A message is already being processed "
                "in this conversation."
            ),
        ) from None

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Could not save your message.",
        ) from None

    try:
        messages = history + [
            {
                "role": "user",
                "content": payload.message,
            }
        ]

        # Start each turn with no booking proposal.
        # prepare_booking can populate this field in the graph.
        # result = await request.app.state.agent.ainvoke(
        #     {
        #         "messages": messages,
        #         "tool_calls": [],
        #         "model_calls": 0,
        #         "reply": "",
        #         "booking_proposal": None,
        #     },
        #     config={"recursion_limit": 12},
        # )

        result = await run_agent_with_trace(
            langfuse=request.app.state.langfuse,
            agent=request.app.state.agent,
            conversation_id=str(conversation_id),
            messages=messages,
        )

        reply = result["reply"]
        booking_proposal = result.get("booking_proposal")

        # Construct the response before marking the turn complete.
        response = ChatResponse(
            reply=reply,
            booking_proposal=booking_proposal,
        )

        await run_in_threadpool(
            complete_turn,
            message_id,
            reply,
        )

        logger.info(
            "conversation_response "
            "conversation_id=%s "
            "booking_proposal_present=%s",
            str(conversation_id),
            booking_proposal is not None,
        )

        # Return both the text and the structured card data.
        return response

    except (APIError, ValueError, SQLAlchemyError) as exc:
        logger.error(
            "conversation_turn_failed "
            "message_id=%s type=%s request_id=%s",
            message_id,
            type(exc).__name__,
            getattr(exc, "request_id", None),
        )

        try:
            await run_in_threadpool(
                fail_turn,
                message_id,
            )

        except SQLAlchemyError:
            logger.error(
                "turn_status_update_failed message_id=%s",
                message_id,
            )

        if isinstance(exc, APITimeoutError):
            status = 504
            detail = "AI response timed out."

        elif isinstance(exc, RateLimitError):
            status = 503
            detail = "AI provider limit reached."

        elif isinstance(exc, SQLAlchemyError):
            status = 503
            detail = "Could not save the AI response."

        else:
            status = 502
            detail = "AI request failed."

        raise HTTPException(
            status_code=status,
            detail=detail,
        ) from None