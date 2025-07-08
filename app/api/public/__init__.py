"""API Routes for Public Site"""

from fastapi import APIRouter
from .auth import router as auth_router

router = APIRouter(prefix="/public")
router.include_router(auth_router)
