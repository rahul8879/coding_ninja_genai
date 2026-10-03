from langchain_openai import ChatOpenAI

from app.core.config import settings


def create_llm():
    if not settings.openai_api_key:
        return None

    return ChatOpenAI(
        model=settings.model_name,
        temperature=0,
        api_key=settings.openai_api_key,
    )
