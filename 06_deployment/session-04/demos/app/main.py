from fastapi import FastAPI
from pydantic import BaseModel

from app.chatbot import ask_chatbot

app = FastAPI(
    title=" Rahul AI Assistant",
    description="Docker + FastAPI + OpenAI teaching demo",
    version="1.0"
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "AppliedSkill Rahul AI Assistant",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    answer = ask_chatbot(request.question)

    return {
        "question": request.question,
        "answer": answer
    }