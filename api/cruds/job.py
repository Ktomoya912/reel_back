import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import or_

import api.cruds.tag as tag_crud
import api.models.job as job_model
import api.models.user as user_model
import api.schemas.job as job_schema


def create_job(
    db: Session, job_create: job_schema.JobCreate, user_id: int
) -> job_model.Job:
    tmp = job_create.model_dump(exclude={"tags", "job_times"})
    job = job_model.Job(**tmp, user_id=user_id)
    db.add(job)
    db.commit()
    return job


def create_job_times(
    db: Session,
    job: job_model.Job,
    job_times: list[job_schema.JobTimeCreate],
) -> job_model.JobTime:
    for job_time in job_times:
        tmp = job_time.model_dump()
        job_time = job_model.JobTime(**tmp)
        job.job_times.append(job_time)
    db.commit()

    return job


def update_job(db: Session, id: int, job_update: job_schema.JobCreate) -> job_model.Job:
    tags = job_update.tags
    sql = select(job_model.Job).filter(job_model.Job.id == id)
    result: Result = db.execute(sql)
    job = result.scalar_one()
    tag_crud.create_job_tags(db, job_update, tags)
    tmp = job_update.model_dump(exclude={"tags"})
    for key, value in tmp.items():
        setattr(job, key, value)
    db.commit()

    return job


def get_job(db: Session, id: int) -> job_model.Job:
    job = db.query(job_model.Job).filter(job_model.Job.id == id).first()
    return job


def watch_job(db: Session, id: int, user_id: int) -> job_model.Job:
    job = get_job(db, id)
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    watched_users = (
        db.query(job_model.JobWatched)
        .filter(
            job_model.JobWatched.user_id == user.id,
            job_model.JobWatched.job_id == job.id,
        )
        .first()
    )
    if watched_users is None:
        watched_users = job_model.JobWatched(user_id=user.id, job_id=job.id)
        db.add(watched_users)
    else:
        watched_users.count += 1
    db.commit()
    return job


def delete_job(db: Session, id: int) -> bool:
    job = db.query(job_model.Job).filter(job_model.Job.id == id).first()
    db.delete(job)
    db.commit()
    return True


def get_job_from_tag(db: Session, tag_name: str) -> list[job_model.Job]:
    tag = tag_crud.get_tag_from_name(db, tag_name)
    return tag.jobs


# 開催時期が3日以内のアルバイトを取得
def get_recent_jobs(db: Session) -> list[job_model.Job]:
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(days=3)
    jobs = (
        db.query(job_model.Job)
        .join(job_model.JobTime)
        .filter(
            job_model.JobTime.start_time >= now,
            job_model.JobTime.start_time <= start_time,
            job_model.Job.status == "1",
        )
        .all()
    )
    return jobs


def search_jobs(
    db: Session,
    keyword: str = "",
) -> list[job_model.Job]:
    jobs = (
        db.query(job_model.Job)
        .filter(
            or_(
                job_model.Job.name.contains(keyword),
                job_model.Job.description.contains(keyword),
            )
        )
        .filter(job_model.Job.status == "1")
        .all()
    )
    return jobs


def get_jobs(
    db: Session, only_active: bool = True, limit: int = 10, offset: int = 0
) -> list[job_model.Job]:
    result = db.query(job_model.Job)
    if only_active:
        result = result.filter(job_model.Job.status == "1")
    return result.limit(limit).offset(offset).all()
