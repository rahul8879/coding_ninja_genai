from fastapi import FastAPI
from pydantic import BaseModel, Field


POLICY_DOCUMENTS = [
    {
        "id": "leave-001",
        "title": "Annual Leave Policy",
        "text": (
            "Employees are entitled to 24 working days of annual leave "
            "per calendar year. A maximum of 10 unused annual leave days "
            "may be carried forward."
        ),
    },
    {
        "id": "leave-002",
        "title": "Sick Leave Policy",
        "text": (
            "Employees are entitled to 12 working days of paid sick leave "
            "per calendar year."
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
        "title": "Parental Leave Policy",
        "text": (
            "Eligible employees may receive maternity, paternity, or "
            "adoption leave according to applicable company policy "
            "and local law."
        ),
    },
]


class RetrievalRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=2, ge=1, le=5)


class Document(BaseModel):
    id: str
    title: str
    text: str


class RetrievalResponse(BaseModel):
    question: str
    documents: list[Document]


app = FastAPI(
    title="Retrieval Service",
    version="3.0.0",
    description="Independent document retrieval microservice.",
)


@app.get("/")
def root():
    return {
        "service": "retrieval-service",
        "architecture": "microservice",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "retrieval-service",
    }


def retrieve_documents(
    question: str,
    top_k: int = 2,
) -> list[dict]:

    query_terms = {
        word.strip(".,?!:;").lower()
        for word in question.split()
        if len(word.strip(".,?!:;")) > 2
    }

    scored = []

    for document in POLICY_DOCUMENTS:
        content = (
            f"{document['title']} "
            f"{document['text']}"
        ).lower()

        score = sum(
            1
            for term in query_terms
            if term in content
        )

        scored.append((score, document))

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        document
        for score, document in scored
        if score > 0
    ][:top_k]


@app.post(
    "/retrieve",
    response_model=RetrievalResponse,
)
def retrieve(payload: RetrievalRequest):

    documents = retrieve_documents(
        payload.question,
        payload.top_k,
    )

    print(
        {
            "service": "retrieval-service",
            "question": payload.question,
            "documents_found": len(documents),
        }
    )

    return RetrievalResponse(
        question=payload.question,
        documents=[
            Document(**document)
            for document in documents
        ],
    )
