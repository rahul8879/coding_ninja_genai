from fastapi import FastAPI

from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Inventra API",
    version="1.0.0",
    description=(
        "FastAPI interface for the Inventra "
        "LangGraph multi-agent system."
    ),
)

app.add_middleware(
    CORSMiddleware,

    # React dev server
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

app.include_router(
    router
)


@app.get("/")
async def root() -> dict:
    return {
        "name": "Inventra API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
