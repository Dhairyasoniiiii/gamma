"""
Minimal server test to isolate the shutdown issue
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] Starting minimal server...")
    yield
    print("[SHUTDOWN] Shutting down minimal server...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
