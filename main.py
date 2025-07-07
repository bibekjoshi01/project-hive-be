from fastapi import FastAPI
from app.database import db_pool
from app.config import settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if db_pool:
        db_pool.closeall()


app = FastAPI(lifespan=lifespan, title=settings.app_name, version=settings.app_version)


@app.get("/health", tags=["Site"])
async def health_check():
    return {"status": "ok"}
