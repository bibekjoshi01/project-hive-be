"""API Routes for Public Site"""

from fastapi import APIRouter
from .auth import router as auth_router
from .website import router as website_router
from .project import router as project_router

router = APIRouter(prefix="/public")

router.include_router(auth_router)
router.include_router(website_router)
router.include_router(project_router)
