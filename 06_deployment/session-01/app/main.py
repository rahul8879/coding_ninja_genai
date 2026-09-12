from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- The CORS import
from uuid import uuid4
from time import perf_counter

from contextlib import asynccontextmanager
from config import get_settings
from rag import PolicyRAG
from schemas import ChatRequest, ChatResponse, Source
from fastapi import FastAPI, HTTPException, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup builds/loads embeddings once instead of on every request.
    app.state.rag = PolicyRAG(get_settings())
    yield



app = FastAPI(title="My FastAPI App", 
              description="This is a sample FastAPI application.",
                version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health")
def health() -> dict[str, str]:
    """Infrastructure health; it cannot tell us whether answers are correct."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    settings = get_settings()
    prompt_version = payload.prompt_version or settings.prompt_version
    request_id = str(uuid4())
    started = perf_counter()

    try:
        if payload.generate_answer:
            answer, documents = request.app.state.rag.answer(payload.question, prompt_version)
        else:
            documents = request.app.state.rag.retrieve(payload.question)
            answer = "Retrieval completed; LLM generation was disabled for this load-test request."
    except Exception as exc:
        # Avoid leaking API keys, prompts, or provider details to clients.
        raise HTTPException(status_code=502, detail=f"AI pipeline failed; request_id={request_id}") from exc

    sources = [
        Source(file=str(doc.metadata.get("source", "unknown")), chunk=doc.metadata.get("chunk"))
        for doc in documents
    ]
    return ChatResponse(
        answer=answer,
        prompt_version=prompt_version,
        model=settings.openai_model,
        latency_ms=round((perf_counter() - started) * 1000, 2),
        sources=sources,
        request_id=request_id,
        mode=mode,
    )

