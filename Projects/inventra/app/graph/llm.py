import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )
