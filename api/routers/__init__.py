from . import auth, user, event, tag, notice, plan
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(user.router)
router.include_router(event.router)
router.include_router(tag.router)
router.include_router(notice.router)
router.include_router(plan.router)
