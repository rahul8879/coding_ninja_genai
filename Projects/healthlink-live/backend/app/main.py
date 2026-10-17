# Step 1: write your FastAPI application here, following the instructions.
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine
from app.doctor_routes import router as doctor_router
from app.conversation_routes import router as conversation_router
from app.llm_client import create_llm_client
from app.agent import build_agent

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm_client = create_llm_client()
    try:
        app.state.agent = build_agent(app.state.llm_client)
        yield
    finally:
        await app.state.llm_client.close()

app = FastAPI(title="HealthLink API", version="1.0.0", lifespan=lifespan)
app.include_router(doctor_router)
app.include_router(conversation_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "healthlink-api"}

@app.get("/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable") from None
    return {"status": "ready", "database": "connected"}


