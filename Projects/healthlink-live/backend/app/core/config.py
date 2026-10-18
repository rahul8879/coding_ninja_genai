"""Environment settings. Secrets stay in .env or deployment environment."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Override is useful for isolated verification; normally inferred from this file.
PROJECT_ROOT = Path(os.environ.get(
    "HEALTHLINK_PROJECT_ROOT", str(Path(__file__).resolve().parents[3])
)).resolve()
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_TIMEOUT_SECONDS = 20.0
LLM_MAX_RETRIES = 1

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL", "https://jp.cloud.langfuse.com").strip()


