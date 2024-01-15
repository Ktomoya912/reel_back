from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from ..dependencies import get_company_user, get_config
from ..utils import get_jst_now
from . import auth, event, job, notice, plan, tag, user

router = APIRouter(prefix=get_config().PREFIX)

router.include_router(auth.router)
router.include_router(event.router)
router.include_router(job.router)
router.include_router(notice.router)
router.include_router(plan.router)
router.include_router(tag.router)
router.include_router(user.router)


@router.post("/upload-image")
def upload_image(file: UploadFile = File(...), current_user=Depends(get_company_user)):
    file_ext = Path(file.filename).suffix
    file_name = f"{current_user.id}_{get_jst_now().strftime('%Y%m%d%H%M%S')}{file_ext}"
    return {"filename": file_name}
