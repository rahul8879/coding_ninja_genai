from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.llm.client import create_llm


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Stage 2 Modular Monolith...")

    app.state.llm = create_llm()

    if app.state.llm is None:
        print("OPENAI_API_KEY not configured. Retrieval-only mode enabled.")
    else:
        print(f"LLM initialized: {settings.model_name}")

    yield

    print("Shutting down Stage 2 Modular Monolith...")


app = FastAPI(
    title="Employee Policy Assistant - Stage 2 Modular Monolith",
    version="2.0.0",
    description=(
        "One application and one deployment, but code is separated "
        "into clear domain modules."
    ),
    lifespan=lifespan,
)

app.include_router(router)
