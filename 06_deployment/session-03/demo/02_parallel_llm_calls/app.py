import asyncio
import os

import time
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from langchain_openai import ChatOpenAI

app = FastAPI(title="Parallel LLM Calls")
llm = ChatOpenAI(model= "gpt-5.4-mini")


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


async def ask_llm(label: str, prompt: str) -> dict:
    started = time.perf_counter()
    print(f"START {label}", flush=True)
    response = await llm.ainvoke(prompt)
    print(f"END   {label}", flush=True)
    return {
        "label": label,
        "answer": message_text(response),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }

@app.get("/sequential")
async def sequential():
    started = time.perf_counter()
    first = await ask_llm("first", "In one short sentence, explain what FastAPI is.")
    second = await ask_llm("second", "In one short sentence, explain what async programming is.")
    return {
        "mode": "sequential",
        "results": [first, second],
        "total_seconds": round(time.perf_counter() - started, 3)
    }

@app.get("/parallel")
async def parallel():
    started = time.perf_counter()
    first, second = await asyncio.gather(
        ask_llm("first", "In one short sentence, explain what FastAPI is."),
        ask_llm("second", "In one short sentence, explain what async programming is."),
    )
    return {
        "mode": "parallel",
        "results": [first, second],
        "total_seconds": round(time.perf_counter() - started, 3)
    }