from fastapi import FastAPI
import asyncio

app = FastAPI(title="My FastAPI App")

@app.get("/order")
async def order():
    await asyncio.sleep(3) 
    return {"order_id": 12345, "status": "confirmed"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
