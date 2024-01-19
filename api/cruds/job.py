import datetime
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import desc, func, or_

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
        raise HTTPException(status_code=404, detail="Job Not Found")
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
        raise HTTPException(status_code=404, detail="Tag Not Found")
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
    status: Literal["all", "active", "inactive", "draft", "posted"] = "all",
    keyword: str = "",
    sort: Literal["review", "favorite", "recent", "id", "pv", "last_watched"] = "id",
    order: str = "desc",
    offset: int = 0,
    limit: int = 100,
    tag_name="",
    user_id: int = None,
    target: Literal["favorite", "history", "posted"] = None,
):
    stmt = db.query(models.Job)
    if status == "posted":
        stmt = stmt.filter(
            or_(models.Job.status == "active", models.Job.status == "inactive")
        )
    elif status != "all":
        stmt = stmt.filter(models.Job.status == status)
    if keyword != "":
        stmt = stmt.filter(
            or_(
                models.Job.name.contains(keyword),
                models.Job.tags.any(models.Tag.name.contains(keyword)),
            )
        )
    if user_id:
        if target == "favorite":
            stmt = stmt.join(models.JobBookmark).filter(
                models.JobBookmark.user_id == user_id
            )
        elif target == "history":
            stmt = stmt.join(models.JobWatched).filter(
                models.JobWatched.user_id == user_id
            )
        elif target == "posted":
            stmt = stmt.filter(models.Job.user_id == user_id)
        elif target == "apply":
            stmt = stmt.join(models.Application).filter(
                models.Application.user_id == user_id
            )
    if tag_name:
        stmt = stmt.filter(models.Job.tags.any(models.Tag.name == tag_name))
    if sort == "id":
        stmt = get_jobs_by_id(stmt)
    elif sort == "review":
        stmt = get_jobs_by_review(stmt)
    elif sort == "favorite":
        stmt = get_jobs_by_bookmark(stmt, target)
    elif sort == "pv":
        stmt = get_jobs_by_pv(stmt, target)
    elif sort == "last_watched":
        stmt = get_jobs_by_last_watched(stmt, target)
    else:
        stmt = get_jobs_by_recent(stmt)
    return stmt.offset(offset).limit(limit).all()


# Reviewの評価平均順にイベントを取得
def get_jobs_by_review(query):
    return (
        query.outerjoin(models.JobReview)
        .order_by(func.avg(models.JobReview.review_point).desc())
        .group_by(models.Job.id)
    )


def get_jobs_by_last_watched(query, target):
    if target == "history":
        return query.order_by(models.JobWatched.updated_at.desc())
    return query.join(models.JobWatched).order_by(desc(models.JobWatched.updated_at))


def get_jobs_by_pv(query, target):
    if target == "history":
        return query.order_by(func.count(models.JobWatched.user_id).desc()).group_by(
            models.Job.id
        )
    return (
        query.outerjoin(models.JobWatched)
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


def get_jobs_by_bookmark(query, target):
    if "favorite" == target:
        return query.order_by(func.count(models.JobBookmark.user_id).desc()).group_by(
            models.Job.id
        )
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


def toggle_bookmark_job(db: Session, job_id: int, user_id: int):
    bookmark = (
        db.query(models.JobBookmark)
        .filter(
            models.JobBookmark.user_id == user_id,
            models.JobBookmark.job_id == job_id,
        )
        .first()
    )
    if bookmark:
        db.delete(bookmark)
        db.commit()
        return False
    else:
        bookmark = models.JobBookmark(user_id=user_id, job_id=job_id)
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
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
    pv = len(job.watched_user_link)
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
