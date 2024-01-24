import os
from pathlib import Path

import boto3
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..dependencies import get_company_user
from ..utils import get_jst_now
from . import auth, event, job, notice, plan, tag, user

router = APIRouter(prefix=os.getenv("PREFIX", "/api/v1"))

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
    print(file_name)
    need_env = [
        "AWS_S3_BUCKET",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_DEFAULT_REGION",
        "AWS_SESSION_TOKEN",
    ]
    bucket = os.getenv(need_env[0])
    for env in need_env:
        if os.getenv(env) is None:
            raise HTTPException(status_code=500, detail=f"{env} is not set")
    s3 = boto3.client("s3")
    try:
        s3.head_bucket(Bucket=bucket)
        print("Bucket Exists!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    s3.upload_fileobj(file.file, bucket, file_name, ExtraArgs={"ACL": "public-read"})
    print("Upload Success!")
    return {"url": f"https://{bucket}.s3.amazonaws.com/{file_name}"}
