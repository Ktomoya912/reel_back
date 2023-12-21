import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import or_

import api.models.job as job_model
import api.schemas.job as job_schema


async def create_job(
    db: AsyncSession, job_create: job_schema.JobCreate
) -> job_model.Job:
    tmp = job_create.model_dump()
    job = job_model.Job(**tmp)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job(db: AsyncSession, id: int) -> job_model.Job:
    sql = select(job_model.Job).filter(job_model.Job.id == id)
    result: Result = await db.execute(sql)
    return result.scalar_one()


# 開催時期が7日以内のイベントを取得
async def get_recent_jobs(db: AsyncSession) -> list[job_model.Job]:
    sql = select(job_model.Job).filter(
        job_model.Job.status == "1",
        job_model.Job.job_times.any(
            job_model.JobTime.start_time
            > datetime.datetime.now() - datetime.timedelta(days=7)
        ),
    )
    result: Result = await db.execute(sql)
    return result.scalars()


async def search_jobs(
    db: AsyncSession,
    keyword: str = "",
) -> list[job_model.Job]:
    sql = select(job_model.Job).filter(
        or_(
            job_model.Job.title.like(f"%{keyword}%"),
            job_model.Job.description.like(f"%{keyword}%"),
        ),
    )
    result: Result = await db.execute(sql)
    return result.scalars()


async def get_jobs(
    db: AsyncSession, sort: str = "id", order: str = "asc"
) -> list[job_model.Job]:
    try:
        sort_column = getattr(job_model.Job, sort)
    except AttributeError:
        sort_column = job_model.Job.id
    sql = select(job_model.Job).order_by(
        sort_column if order == "asc" else sort_column.desc()
    )
    result: Result = await db.execute(sql)
    return result.scalars()
