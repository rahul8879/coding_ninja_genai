from langfuse import Langfuse
from app.core import config


def create_observability_client():
    return Langfuse(
        public_key=config.LANGFUSE_PUBLIC_KEY,
        secret_key=config.LANGFUSE_SECRET_KEY,
        base_url=config.LANGFUSE_BASE_URL,
    )