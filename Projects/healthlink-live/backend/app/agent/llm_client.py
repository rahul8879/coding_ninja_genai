import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI


from app.core.config import PROJECT_ROOT
from app.core import config
MODEL = config.OPENAI_MODEL


# later on we will read this prompt from hub/prompt hub/langfuse/shared drive
SYSTEM_PROMPT = """
You are HealthLink, a healthcare navigation assistant.
Help the user describe their concern and prepare to find appropriate care.
Use simple language and respond in the user's language.
For an unclear health concern, ask one or two relevant follow-up questions.
Do not provide a definitive diagnosis or prescribe medications.
For apparent urgent danger, advise immediate local emergency help.
Doctor search and booking are not connected to this direct-call function.
Do not invent doctor names, availability, or booking confirmations.
Keep replies concise.
"""

def create_llm_client() -> AsyncOpenAI:
    api_key = config.OPENAI_API_KEY.strip()
    if not api_key or api_key == "your_actual_api_key":
        raise RuntimeError("Set a valid OPENAI_API_KEY in your .env file")
    base_url = config.OPENAI_BASE_URL.strip()
    if not base_url.startswith(("https://", "http://")):
        raise RuntimeError("OPENAI_BASE_URL must start with https:// or http://")
    return AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=config.LLM_TIMEOUT_SECONDS, max_retries=config.LLM_MAX_RETRIES)

async def generate_reply(
    client: AsyncOpenAI, message: str, history: list[dict[str, str]] | None = None
) -> str:
    # Used in the direct-call and conversation-memory lessons, before LangGraph.
    input_messages = list(history or [])
    input_messages.append({"role": "user", "content": message})
    response = await client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=input_messages,
        max_output_tokens=400,
        store=False,
    )
    reply = response.output_text.strip()
    if response.status != "completed" or not reply:
        raise ValueError("Model did not return a complete text response")
    return reply

