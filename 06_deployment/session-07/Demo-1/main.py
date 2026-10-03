import os
import time
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")



POLICY_DOCUMENTS = [
    {
        "id": "leave-001",
        "title": "Annual Leave Policy",
        "text": (
            "Employees are entitled to 24 working days of annual leave "
            "per calendar year. Unused annual leave may be carried forward "
            "up to a maximum of 10 days."
        ),
    },
    {
        "id": "leave-002",
        "title": "Sick Leave Policy",
        "text": (
            "Employees are entitled to 12 working days of paid sick leave "
            "per calendar year. Medical documentation may be requested for "
            "extended absences."
        ),
    },
    {
        "id": "benefit-001",
        "title": "Relocation Benefit",
        "text": (
            "Eligible employees relocating for an approved business need "
            "may receive reimbursement up to INR 100,000, subject to "
            "manager and HR approval."
        ),
    },
    {
        "id": "parental-001",
        "title": "Parental Leave",
        "text": (
            "Eligible employees may receive maternity, paternity, or adoption "
            "leave according to applicable company policy and local law."
        ),
    },
]

class ChatRequest(BaseModel):
    question: str
    generate_answer: bool = True

class Source(BaseModel):
    id: str
    title: str
    text: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    latency_ms: float


def retrieve_documents(question: str, top_k: int = 2):
    query_terms = {
        word.strip(".,?!").lower()
        for word in question.split()
        if len(word.strip(".,?!")) > 2
    }

    scored = []

    for document in POLICY_DOCUMENTS:
        content = f"{document['title']} {document['text']}".lower()
        score = sum(term in content for term in query_terms)
        scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)

    matches = [
        document
        for score, document in scored
        if score > 0
    ]

    return matches[:top_k]


def retrieve_documents(question: str, top_k: int = 2):
    start_time = time.perf_counter()
    query_terms = {
        word.strip(".,?!").lower()
        for word in question.split()
        if len(word.strip(".,?!")) > 2
    }

    scored = []

    for document in POLICY_DOCUMENTS:
        content = f"{document['title']} {document['text']}".lower()
        score = sum(term in content for term in query_terms)
        scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)

    matches = [
        document
        for score, document in scored
        if score > 0
    ]
    end_time = time.perf_counter()
    print(f"Document retrieval latency: {(end_time - start_time) * 1000:.2f} ms")
    return matches[:top_k]


def build_prompt(question: str, documents: list[dict]) -> str:
    if not documents:
        context = "No relevant company policy was found."
    else:
        context = "\n\n".join(
            f"[{doc['title']}]\n{doc['text']}"
            for doc in documents
        )

    return f"""
            You are an employee policy assistant.

            Rules:
            1. Answer only from the supplied context.
            2. If the context does not contain the answer, say:
            "I could not find this information in the available policy documents."
            3. Do not invent company policy.
            4. Keep the answer concise.

            CONTEXT:
            {context}

            QUESTION:
            {question}

            ANSWER:
            """.strip()


def create_llm():
    if not OPENAI_API_KEY:
        return None

    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=OPENAI_API_KEY,
    )


llm = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm

    print("Starting Policy Assistant...")
    llm = create_llm()

    if llm is None:
        print("OPENAI_API_KEY is not configured.")
        print("The API will still run in retrieval-only demo mode.")
    else:
        print(f"LLM initialized: {MODEL_NAME}")

    yield

    print("Shutting down Policy Assistant...")



app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {
        "application": "Employee Policy Assistant",
        "architecture": "monolith",
        "stage": 1,
    }



@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    start = time.perf_counter()

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # Step 1: Retrieval
    documents = retrieve_documents(question)

    # Step 2: Prompt creation
    prompt = build_prompt(question, documents)

    # Step 3: LLM generation
    if not request.generate_answer:
        answer = (
            "LLM generation disabled. "
            "Relevant policy documents were retrieved successfully."
        )

    elif llm is None:
        answer = (
            "OPENAI_API_KEY is not configured. "
            "Run with generate_answer=false to test retrieval, "
            "or configure the API key to generate an answer."
        )

    else:
        try:
            response = llm.invoke(prompt)
            answer = response.content
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"LLM provider error: {str(exc)}",
            )

    latency_ms = (time.perf_counter() - start) * 1000

    # Step 4: Logging
    print(
        {
            "question": question,
            "documents_found": len(documents),
            "latency_ms": round(latency_ms, 2),
        }
    )

    return ChatResponse(
        question=question,
        answer=answer,
        sources=[Source(**document) for document in documents],
        latency_ms=round(latency_ms, 2),
    )
