from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import api.models.event as event_model
import api.models.job as job_model
import api.models.tag as tag_model
import api.schemas.tag as tag_schema


async def create_tag(
    db: AsyncSession, tag_create: tag_schema.TagCreate
) -> tag_model.Tag:
    tag = tag_model.Tag(**tag_create.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_tag_from_name(db: AsyncSession, tag_name: str) -> tag_model.Tag:
    sql = select(tag_model.Tag).filter(tag_model.Tag.name == tag_name)
    result: Result = await db.execute(sql)
    return result.scalar_one_or_none()


async def get_event_from_tag(
    db: AsyncSession, tag_name: str, sort: str = "id", order: str = "asc"
) -> list[event_model.Event]:
    try:
        sort_column = getattr(event_model.Event, sort)
    except AttributeError:
        sort_column = event_model.Event.id
    tag = await get_tag_from_name(db, tag_name)
    sql = (
        select(event_model.Event)
        .filter(event_model.Event.tags.any(tag))
        .order_by(sort_column if order == "asc" else sort_column.desc())
    )
    result: Result = await db.execute(sql)
    return result.scalars()


async def get_job_from_tag(
    db: AsyncSession, tag_name: str, sort: str = "id", order: str = "asc"
) -> list[job_model.Job]:
    try:
        sort_column = getattr(job_model.Job, sort)
    except AttributeError:
        sort_column = job_model.Job.id
    tag = await get_tag_from_name(db, tag_name)
    sql = (
        select(job_model.Job)
        .filter(job_model.Job.tags.any(tag))
        .order_by(sort_column if order == "asc" else sort_column.desc())
    )
    result: Result = await db.execute(sql)
    return result.scalars()


async def create_job_tags(
    db: AsyncSession, job: job_model.Job, tags: list[str]
) -> job_model.Job:
    job.tags = []
    for tag in tags:
        tag = await get_tag_from_name(db, tag)
        if tag is None:
            tag = await create_tag(db, tag_schema.TagCreate(name=tag))
        job.tags.append(tag)
    await db.commit()
    await db.refresh(job)
    return job


async def create_event_tags(
    db: AsyncSession, event: event_model.Event, tags: list[str]
) -> event_model.Event:
    event.tags = []
    for tag in tags:
        tag = await get_tag_from_name(db, tag)
        if tag is None:
            tag = await create_tag(db, tag_schema.TagCreate(name=tag))
        event.tags.append(tag)
    await db.commit()
    await db.refresh(event)
    return event
