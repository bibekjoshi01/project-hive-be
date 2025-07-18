"""API Routes for Admin Dashboard"""

from fastapi import APIRouter

from .auth import router as auth_router

router = APIRouter(prefix="/admin")
router.include_router(auth_router)
