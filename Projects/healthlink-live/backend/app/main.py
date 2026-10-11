# Step 1: write your FastAPI application here, following the instructions.
from fastapi import FastAPI,HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine
from app.doctor_routes import router as doctor_router

app = FastAPI(title="HealthLink API", version="1.0.0")
app.include_router(doctor_router)
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


