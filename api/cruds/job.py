import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import or_
from api.modules.common import get_jst_now
import api.cruds.tag as tag_crud

from api import models, schemas


def create_job(db: Session, job_create: schemas.JobCreate, user_id: int) -> models.Job:
    tmp = job_create.model_dump(exclude={"tags", "job_times"})
    job = models.Job(**tmp, user_id=user_id)
    db.add(job)
    db.commit()
    return job


def create_job_times(
    db: Session,
    job: models.Job,
    job_times: list[schemas.JobTimeCreate],
) -> models.JobTime:
    for job_time in job_times:
        tmp = job_time.model_dump()
        job_time = models.JobTime(**tmp)
        job.job_times.append(job_time)
    db.commit()

    return job


def update_job(db: Session, id: int, job_update: schemas.JobCreate) -> models.Job:
    tags = job_update.tags
    sql = select(models.Job).filter(models.Job.id == id)
    result: Result = db.execute(sql)
    job = result.scalar_one()
    tag_crud.create_job_tags(db, job_update, tags)
    tmp = job_update.model_dump(exclude={"tags"})
    for key, value in tmp.items():
        setattr(job, key, value)
    db.commit()

    return job


def get_job(db: Session, id: int) -> models.Job:
    job = db.query(models.Job).filter(models.Job.id == id).first()
    return job


def watch_job(db: Session, id: int, user_id: int) -> models.Job:
    job = get_job(db, id)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    watched_users = (
        db.query(models.JobWatched)
        .filter(
            models.JobWatched.user_id == user.id,
            models.JobWatched.job_id == job.id,
        )
        .first()
    )
    if watched_users is None:
        watched_users = models.JobWatched(user_id=user.id, job_id=job.id)
        db.add(watched_users)
    else:
        watched_users.count += 1
    db.commit()
    return job


def delete_job(db: Session, id: int) -> bool:
    job = db.query(models.Job).filter(models.Job.id == id).first()
    db.delete(job)
    db.commit()
    return True


def get_job_by_tag(db: Session, tag_name: str) -> list[models.Job]:
    tag = tag_crud.get_tag_by_name(db, tag_name)
    return tag.jobs


# 開催時期が3日以内のアルバイトを取得
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


def search_jobs(
    db: Session,
    keyword: str = "",
) -> list[models.Job]:
    jobs = (
        db.query(models.Job)
        .filter(
            or_(
                models.Job.name.contains(keyword),
                models.Job.description.contains(keyword),
            )
        )
        .filter(models.Job.status == "1")
        .all()
    )
    return jobs


def get_jobs(
    db: Session, only_active: bool = True, limit: int = 10, offset: int = 0
) -> list[models.Job]:
    result = db.query(models.Job)
    if only_active:
        result = result.filter(models.Job.status == "1")
    return result.limit(limit).offset(offset).all()
