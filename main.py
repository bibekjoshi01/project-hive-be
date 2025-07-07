from fastapi import FastAPI
from app.database import db_pool
from app.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health", tags=["Site"])
async def health_check():
    return {"status": "ok"}


@app.add_event_handler("shutdown")
def shutdown_event():
    if db_pool:
        db_pool.closeall()