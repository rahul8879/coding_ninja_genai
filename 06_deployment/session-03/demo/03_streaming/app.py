import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

app = FastAPI(title="05 - Streaming with LangChain + OpenAI")
llm = ChatOpenAI(model=MODEL, temperature=0, streaming=True)


def message_text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "".join(parts)
    return str(content)


PROMPT = """
Explain why async programming is useful for an AI API.
Use about 100 words, simple language, and short sentences.
"""

@app.get("/non-stream")
async def non_stream():
    response = await llm.ainvoke(PROMPT)
    return {
        "answer": message_text(response),
        "note": "The client receives the full answer after generation finishes.",
    }

async def token_stream():
    async for chunk in llm.astream(PROMPT):
        text = message_text(chunk)
        if text:
            yield text

@app.get("/stream")
async def stream():
    return StreamingResponse(
        token_stream(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
