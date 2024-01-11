from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.job as job_crud
import api.cruds.plan as plan_crud
import api.cruds.tag as tag_crud
from api import models, schemas
from api.dependencies import (
    common_parameters,
    get_admin_user,
    get_company_user,
    get_current_active_user,
    get_db,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=schemas.JobCreateResponse)
def create_job(
    current_user: Annotated[dict, Depends(get_company_user)],
    job_create: schemas.JobCreate,
    db: Session = Depends(get_db),
):
    job = job_crud.create_job(db, job_create, current_user.id)
    job = job_crud.create_job_times(db, job, job_create.job_times)
    job = tag_crud.create_job_tags(db, job, job_create.tags)
    return job


@router.get("/", response_model=list[schemas.JobListView])
def get_jobs(
    common: Annotated[dict, Depends(common_parameters)],
    tag: str = "",
    only_active: bool = False,
):
    if tag:
        data = job_crud.get_job_by_tag(
            common["db"],
            tag,
        )
    else:
        data = job_crud.get_jobs(only_active=only_active, **common)
    return data[common["offset"] : common["offset"] + common["limit"]]  # noqa E203


@router.get("/recent/", response_model=list[schemas.JobListView])
def get_recent_jobs(db: Session = Depends(get_db)):
    return job_crud.get_recent_jobs(db)


@router.get("/{job_id}", response_model=schemas.Job)
def get_job(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    job = job_crud.watch_job(db, job_id, current_user.id)
    setattr(job, "is_favorite", job in current_user.job_bookmarks)
    return job


@router.put("/{job_id}", response_model=schemas.JobCreateResponse)
def update_job(
    job_id: int,
    job_update: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    return job_crud.update_job(db, job_id, job_update)


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    if job_crud.delete_job(db, job_id):
        return {"message": "Deleted successfully"}
    return {"message": "Failed to delete"}


@router.put("/{job_id}/activate", response_model=schemas.JobListView)
def activate_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    job = job_crud.get_job(db, job_id)
    job.status = "1"
    db.commit()
    db.refresh(job)
    return job


@router.post("/purchase-job", response_model=schemas.JobCreateResponse)
def purchase_job(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    purchase_data: schemas.JobArticleCreate,
    db: Session = Depends(get_db),
):
    purchase = plan_crud.purchase_plan(db, purchase_data.purchase, current_user)
    job = create_job(current_user, purchase_data.job, db)
    job.purchase = purchase
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/bookmark")
def bookmark_job(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return job_crud.bookmark_job(db, job_id, current_user.id)


@router.delete("/{job_id}/bookmark")
def unbookmark_job(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return job_crud.unbookmark_job(db, job_id, current_user.id)


@router.post("/{job_id}/review", response_model=schemas.JobReview)
def post_review(
    job_id: int,
    review: schemas.JobReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return job_crud.create_review(db, job_id, current_user.id, review)


@router.put("/{job_id}/review", response_model=schemas.JobReview)
def update_review(
    job_id: int,
    review: schemas.JobReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return job_crud.update_review(db, job_id, current_user.id, review)


@router.delete("/{job_id}/review")
def delete_review(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return job_crud.delete_review(db, job_id, current_user.id)
