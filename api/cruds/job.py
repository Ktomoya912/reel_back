import datetime
from typing import Literal

from sqlalchemy.orm.session import Session
from sqlalchemy.sql import func, or_
from fastapi import HTTPException
import api.cruds.tag as tag_crud
from api import models, schemas
from api.utils import get_jst_now


def create_job(db: Session, job_create: schemas.JobCreate, user_id: int) -> models.Job:
    tmp = job_create.model_dump(exclude={"tags", "job_times"})
    job = models.Job(**tmp, user_id=user_id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_job_times(
    db: Session,
    job: models.Job,
    job_times: list[schemas.JobTimeCreate],
) -> models.JobTime:
    results = []
    for job_time in job_times:
        tmp = job_time.model_dump()
        job_time = db.query(models.JobTime).filter_by(**tmp).first()
        if job_time is None:
            job_time = models.JobTime(**tmp)
        results.append(job_time)
    job.job_times = results
    db.commit()
    db.refresh(job)
    return job


def update_job(db: Session, id: int, job_update: schemas.JobCreate) -> models.Job:
    tags = job_update.tags
    job = get_job(db, id)
    tag_crud.create_job_tags(db, job, tags)
    job = create_job_times(db, job, job_update.job_times)
    tmp = job_update.model_dump(exclude={"tags", "job_times"}, exclude_unset=True)
    for key, value in tmp.items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, id: int) -> models.Job:
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return job


def watch_job(db: Session, job_id: int, user_id: int) -> models.Job:
    job = get_job(db, job_id)
    watched_users = (
        db.query(models.JobWatched)
        .filter(
            models.JobWatched.user_id == user_id,
            models.JobWatched.job_id == job_id,
        )
        .first()
    )
    if watched_users is None:
        watched_users = models.JobWatched(user_id=user_id, job_id=job_id)
        db.add(watched_users)
    else:
        watched_users.count += 1
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, id: int) -> bool:
    job = db.query(models.Job).filter(models.Job.id == id).first()
    db.delete(job)
    db.commit()
    return True


def apply_job(db: Session, job_id: int, user: models.User) -> models.Application:
    apply_model = (
        db.query(models.Application)
        .filter(
            models.Application.user_id == user.id,
            models.Application.job_id == job_id,
        )
        .first()
    )
    if apply_model:
        raise HTTPException(status_code=400, detail="Already applied")
    apply_model = models.Application(user_id=user.id, job_id=job_id)
    db.add(apply_model)
    db.commit()
    db.refresh(apply_model)
    return apply_model


def approve_application(db: Session, job_id: int, user_id: int) -> models.Application:
    application = (
        db.query(models.Application)
        .filter(
            models.Application.user_id == user_id,
            models.Application.job_id == job_id,
        )
        .first()
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.status == "a":
        raise HTTPException(status_code=400, detail="Already approved")
    application.status = "a"
    db.commit()
    db.refresh(application)
    return application


def reject_application(db: Session, job_id: int, user_id: int) -> models.Application:
    application = (
        db.query(models.Application)
        .filter(
            models.Application.user_id == user_id,
            models.Application.job_id == job_id,
        )
        .first()
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.status == "r":
        raise HTTPException(status_code=400, detail="Already rejected")
    application.status = "r"
    db.commit()
    db.refresh(application)
    return application


def get_applications(db: Session, job_id: int) -> list[models.Application]:
    return (
        db.query(models.Application).filter(models.Application.job_id == job_id).all()
    )


def get_job_by_tag(db: Session, tag_name: str) -> list[models.Job]:
    tag = tag_crud.get_tag_by_name(db, tag_name)
    if tag is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return tag.jobs


# 開催時期が3日以内のイベントを取得
def get_recent_jobs(db: Session) -> list[models.Job]:
    now = get_jst_now()
    start_time = now + datetime.timedelta(days=3)
    jobs = (
        db.query(models.Job)
        .join(models.JobTime)
        .filter(
            models.JobTime.start_time >= now,
            models.JobTime.start_time <= start_time,
            models.Job.status == "1",
        )
        .all()
    )
    return jobs


def get_jobs(
    db: Session,
    type: Literal["all", "active", "inactive", "draft"] = "all",
    keyword: str = "",
    sort: str = "new",
    order: str = "desc",
    offset: int = 0,
    limit: int = 100,
):
    query = db.query(models.Job)
    if type != "all":
        query = query.filter(models.Job.status == type)

    if keyword != "":
        query = query.filter(
            or_(
                models.Job.name.contains(keyword),
                models.Job.description.contains(keyword),
                models.Job.tags.any(models.Tag.name.contains(keyword)),
            )
        )
    if sort == "id":
        query = get_jobs_by_id(query)
    elif sort == "review":
        query = get_jobs_by_review(query)
    elif sort == "watched":
        query = get_jobs_by_watched(query)
    elif sort == "favorite":
        query = get_jobs_by_bookmark(query)
    elif sort == "pv":
        query = get_jobs_by_pv(query)
    else:
        query = get_jobs_by_recent(query)
    return query.offset(offset).limit(limit).all()


# Reviewの評価平均順にイベントを取得
def get_jobs_by_review(query):
    return (
        query.outerjoin(models.JobReview)
        .order_by(func.avg(models.JobReview.review_point).desc())
        .group_by(models.Job.id)
    )


def get_jobs_by_pv(query):
    return (
        query.join(models.JobWatched)
        .order_by(func.sum(models.JobWatched.count).desc())
        .group_by(models.Job.id)
    )


def get_jobs_by_watched(query):
    return (
        query.join(models.JobWatched)
        .order_by(func.sum(models.JobWatched.count).desc())
        .group_by(models.Job.id)
    )


def get_jobs_by_id(query):
    return query.order_by(models.Job.id.desc())


def get_jobs_by_recent(query):
    now = get_jst_now()
    # 現在日時と開催日時の差が小さい順にイベントを取得、開催日時が過ぎているものは除外
    return (
        query.join(models.JobTime)
        .filter(models.JobTime.start_time >= now)
        .order_by(models.JobTime.start_time)
    )


def get_jobs_by_bookmark(query):
    return (
        query.outerjoin(models.JobBookmark)
        .order_by(func.count(models.JobBookmark.user_id).desc())
        .group_by(models.Job.id)
    )


def create_review(
    db: Session, job_id: int, user_id: int, review: schemas.JobReviewCreate
):
    job_review = models.JobReview(**review.model_dump(), user_id=user_id, job_id=job_id)
    db.add(job_review)
    db.commit()
    db.refresh(job_review)
    return job_review


def get_review(db: Session, job_id: int, user_id: int):
    return (
        db.query(models.JobReview)
        .filter(
            models.JobReview.user_id == user_id,
            models.JobReview.job_id == job_id,
        )
        .first()
    )


def update_review(
    db: Session, job_id: int, user_id: int, review: schemas.JobReviewCreate
):
    job_review = get_review(db, job_id, user_id)
    tmp = review.model_dump(exclude_unset=True)
    for key, value in tmp.items():
        setattr(job_review, key, value)
    db.commit()
    db.refresh(job_review)
    return job_review


def delete_review(db: Session, job_id: int, user_id: int):
    job_review = get_review(db, job_id, user_id)
    db.delete(job_review)
    db.commit()
    return True


def bookmark_job(db: Session, job_id: int, user_id: int):
    if (
        db.query(models.JobBookmark)
        .filter(
            models.JobBookmark.user_id == user_id,
            models.JobBookmark.job_id == job_id,
        )
        .first()
    ):
        return False
    job_bookmark = models.JobBookmark(user_id=user_id, job_id=job_id)
    db.add(job_bookmark)
    db.commit()
    db.refresh(job_bookmark)
    return True


def unbookmark_job(db: Session, job_id: int, user_id: int):
    bookmark = (
        db.query(models.JobBookmark)
        .filter(
            models.JobBookmark.user_id == user_id,
            models.JobBookmark.job_id == job_id,
        )
        .first()
    )
    if not bookmark:
        return False
    db.delete(bookmark)
    db.commit()
    return True


def get_job_impressions(
    db: Session,
    job_id: int,
):
    def get_age_range(
        age: int,
    ) -> Literal["under_20", "20-24", "25-29", "30-34", "35-39", "over_40"]:
        if age < 20:
            return "under_20"
        elif age < 25:
            return "20-24"
        elif age < 30:
            return "25-29"
        elif age < 35:
            return "30-34"
        elif age < 40:
            return "35-39"
        else:
            return "over_40"

    job = get_job(db, job_id)
    favorite_user_count = len(job.bookmark_users)
    pv = sum([watch.count for watch in job.watched_user_link])
    review_count = len(job.reviews)

    age = {
        "o": {
            "under_20": 0,
            "20-24": 0,
            "25-29": 0,
            "30-34": 0,
            "35-39": 0,
            "over_40": 0,
        },
        "m": {
            "under_20": 0,
            "20-24": 0,
            "25-29": 0,
            "30-34": 0,
            "35-39": 0,
            "over_40": 0,
        },
        "f": {
            "under_20": 0,
            "20-24": 0,
            "25-29": 0,
            "30-34": 0,
            "35-39": 0,
            "over_40": 0,
        },
    }

    for link in job.watched_user_link:
        user_age = get_jst_now().year - link.user.birthday.year
        age[link.user.sex][get_age_range(user_age)] += 1

    return {
        "favorite_user_count": favorite_user_count,
        "pv": pv,
        "review_count": review_count,
        "sex": age,
    }
