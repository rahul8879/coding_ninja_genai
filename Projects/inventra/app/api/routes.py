from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
)
from app.graph.workflow import graph
# from app.observability.langsmith_observability import (
#     build_run_config,
# )


router = APIRouter(
    prefix="/api/v1",
)


@router.get("/health")
async def health() -> dict:
    """
    Lightweight application health check.

    This does not call the LLM or MCP servers.
    """

    return {
        "status": "ok",
        "service": "inventra-api",
    }


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    Main application endpoint.

    FastAPI is intentionally thin:
        request
            ↓
        LangGraph
            ↓
        response
    """

    try:
        # config = build_run_config(
        #     thread_id=request.thread_id,
        #     user_query=request.message,
        # )

        result = await graph.ainvoke(
            {
                "user_query": request.message,

                "messages": [
                    HumanMessage(
                        content=request.message
                    )
                ],
            },
            # config=config,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return ChatResponse(
        thread_id=request.thread_id,

        answer=(
            result.get("final_answer")
            or "No response generated."
        ),

        intent=result.get("intent"),

        reorder_needed=(
            result.get("reorder_needed")
        ),

        sku=result.get("sku"),

        region=result.get("region"),

        target_date=(
            result.get("target_date")
        ),
    )
