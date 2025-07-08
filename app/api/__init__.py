from fastapi import APIRouter
from .public import router as public_router
from .admin import router as admin_router

router = APIRouter()
router.include_router(public_router, tags=['Public APIs'])
router.include_router(admin_router, tags=['Admin APIs'])
