import sys
from pathlib import Path
from fastapi import FastAPI
from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from app.api import router as api_router
from app.utils.throttling import limiter

db_pool = None
MEDIA_ROOT = Path("media")
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
allowed_cors_origins = settings.allowed_cors_origins
allowed_hosts = settings.allowed_hosts


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
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(api_router, prefix="/api")

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.debug:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
