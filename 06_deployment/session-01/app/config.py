import os
from functools import lru_cache
from pathlib import Path
from dotnev import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    langsmith_tracing: bool = False
    chroma_directory: Path = Path("artifacts/chroma")
    retrieval_k: int = 3
    prompt_version: str = "v2"
    max_context_chars: int = 6000
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")