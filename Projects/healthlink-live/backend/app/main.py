# Step 1: write your FastAPI application here, following the instructions.
from fastapi import FastAPI,HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine
from app.doctor_routes import router as doctor_router
from app.llm_client import create_llm_client
from app.chat_routes import router as chat_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm_client = create_llm_client()
    try:
        yield
    finally:
        await app.state.llm_client.close()

app = FastAPI(title="HealthLink API", version="1.0.0", lifespan=lifespan)
app.include_router(doctor_router)
app.include_router(chat_router)

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


