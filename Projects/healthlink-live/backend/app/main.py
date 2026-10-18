import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import engine
from app.routes.doctor_routes import router as doctor_router
from app.routes.conversation_routes import router as conversation_router
from app.agent.llm_client import create_llm_client
from app.agent.graph import build_agent
from app.routes.appointment_routes import router as appointment_router
from starlette.concurrency import run_in_threadpool
from app.observability.client import create_observability_client
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm_client = create_llm_client()
    langfuse = None
    try:
        langfuse = create_observability_client()
        app.state.langfuse = langfuse
        app.state.agent = build_agent(app.state.llm_client)
        yield
    finally:
        try:
            await app.state.llm_client.close()
        finally:
            if langfuse is not None:
                await run_in_threadpool(langfuse.shutdown)
                

app = FastAPI(title="HealthLink API", lifespan=lifespan)
app.include_router(doctor_router)
app.include_router(conversation_router)
app.include_router(appointment_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "healthlink-api"}


@app.get("/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable") from None
    return {"status": "ready", "database": "connected"}
