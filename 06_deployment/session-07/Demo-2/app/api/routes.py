import time

from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import ChatRequest, ChatResponse, Source
from app.retrieval.service import retrieve_documents
from app.prompts.builder import build_prompt
from app.llm.service import generate_answer
from app.observability.logger import log_request

router = APIRouter()


@router.get("/")
def root():
    return {
        "application": "Employee Policy Assistant",
        "architecture": "modular-monolith",
        "stage": 2,
    }


@router.get("/health")
def health(request: Request):
    return {
        "status": "healthy",
        "architecture": "modular-monolith",
        "llm_enabled": request.app.state.llm is not None,
    }


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request):
    start = time.perf_counter()

    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # Module 1: Retrieval
    documents = retrieve_documents(question)

    # Module 2: Prompt construction
    prompt = build_prompt(question, documents)

    # Module 3: LLM generation
    answer = generate_answer(
        llm=request.app.state.llm,
        prompt=prompt,
        generate=payload.generate_answer,
    )

    latency_ms = (time.perf_counter() - start) * 1000

    # Module 4: Observability
    log_request(
        question=question,
        documents_found=len(documents),
        latency_ms=latency_ms,
    )

    return ChatResponse(
        question=question,
        answer=answer,
        sources=[Source(**document) for document in documents],
        latency_ms=round(latency_ms, 2),
    )
