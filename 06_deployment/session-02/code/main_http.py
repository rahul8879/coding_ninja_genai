from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
app = FastAPI(title = "HTTPS for AI Engineers")

prompts = {
    1: {"name": "summarizer", "template": "Summarize: {text}"},
    2: {"name": "teacher", "template": "Teach simply: {text}"},
}


class ChatRequest(BaseModel):
    message:str


class PromptReplacement(BaseModel):
    name: str
    template: str


class PromptPatch(BaseModel):
    name: str | None = None
    template: str | None = None


@app.get("/models")
def list_models():
    """GET: retrieve information."""
    return {"models": ["tiny-sentiment-v1", "demo-chat-v1"]}

@app.post("/chat")
def chat(request: ChatRequest):
    """POST: send a chat message."""

    return {"message": f"Received message: {request.message}"}

@app.put("/prompts/{prompt_id}")
def replace_prompt(prompt_id: int, prompt: PromptPatch):
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    prompts[prompt_id] = prompt.model_dump()
    return {"message": "Prompt replaced successfully"}


@app.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int):
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    del prompts[prompt_id]
    return {"message": "Prompt deleted successfully"}
