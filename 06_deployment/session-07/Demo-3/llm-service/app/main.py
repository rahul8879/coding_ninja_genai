import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "gpt-4.1-mini",
)


class Document(BaseModel):
    id: str
    title: str
    text: str


class GenerateRequest(BaseModel):
    question: str
    documents: list[Document]


class GenerateResponse(BaseModel):
    answer: str
    model: str


llm = None


def create_llm():
    if not OPENAI_API_KEY:
        return None

    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=OPENAI_API_KEY,
    )


def build_prompt(
    question: str,
    documents: list[Document],
) -> str:

    if documents:
        context = "\n\n".join(
            f"TITLE: {doc.title}\nCONTENT: {doc.text}"
            for doc in documents
        )
    else:
        context = (
            "No relevant policy document was retrieved."
        )

    return f"""
You are an Employee Policy Assistant.

Rules:
1. Answer only from the supplied context.
2. Do not invent company policy.
3. If the answer is unavailable, say exactly:
   "I could not find this information in the available policy documents."
4. Keep the answer concise.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm

    print("Starting LLM Service...")
    llm = create_llm()

    if llm is None:
        print(
            "OPENAI_API_KEY not configured. "
            "Fallback demo response mode enabled."
        )
    else:
        print(f"LLM initialized: {MODEL_NAME}")

    yield

    print("Shutting down LLM Service...")


app = FastAPI(
    title="LLM Service",
    version="3.0.0",
    description="Independent LLM generation microservice.",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "service": "llm-service",
        "architecture": "microservice",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "llm-service",
        "llm_enabled": llm is not None,
        "model": MODEL_NAME,
    }


@app.post(
    "/generate",
    response_model=GenerateResponse,
)
def generate(payload: GenerateRequest):

    prompt = build_prompt(
        payload.question,
        payload.documents,
    )

    if llm is None:
        # Useful for architecture demos without API spend.
        if payload.documents:
            answer = (
                "LLM is not configured. "
                "Relevant policy context was received successfully "
                "by the LLM microservice."
            )
        else:
            answer = (
                "I could not find this information in the "
                "available policy documents."
            )

        return GenerateResponse(
            answer=answer,
            model="demo-no-llm",
        )

    try:
        response = llm.invoke(prompt)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error: {exc}",
        )

    print(
        {
            "service": "llm-service",
            "question": payload.question,
            "documents_received": len(
                payload.documents
            ),
            "model": MODEL_NAME,
        }
    )

    return GenerateResponse(
        answer=response.content,
        model=MODEL_NAME,
    )
