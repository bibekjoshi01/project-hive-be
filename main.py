from fastapi import FastAPI
from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor
from app.config import settings
from contextlib import asynccontextmanager
import sys
from app.api import router as api_router

db_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    try:
        db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.database_url,
            cursor_factory=RealDictCursor,
        )
        conn = db_pool.getconn()
        db_pool.putconn(conn)
    except OperationalError as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        sys.exit(1)  

    yield

    if db_pool:
        db_pool.closeall()


app = FastAPI(lifespan=lifespan, title=settings.app_name, version=settings.app_version)
app.include_router(api_router, prefix="/api")

@app.get("/health", tags=["Site"])
async def health_check():
    return {"status": "ok"}
