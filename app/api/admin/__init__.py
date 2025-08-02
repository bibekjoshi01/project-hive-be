"""API Routes for Admin Dashboard"""

from fastapi import APIRouter

from .auth import router as auth_router
from .project import router as project_router
from .website import router as website_router

router = APIRouter(prefix="/admin")
router.include_router(auth_router)
router.include_router(website_router)
router.include_router(project_router)
