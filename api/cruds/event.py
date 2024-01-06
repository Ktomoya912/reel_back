import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import or_
from sqlalchemy.orm import selectinload

import api.cruds.tag as tag_crud
import api.models.event as event_model
import api.schemas.event as event_schema


async def create_event(
    db: AsyncSession, event_create: event_schema.EventCreate
) -> event_model.Event:
    tmp = event_create.model_dump(exclude={"tags", "event_times"})
    event = event_model.Event(**tmp)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def create_event_times(
    db: AsyncSession,
    event: event_model.Event,
    event_times: list[event_schema.EventTimeCreate],
) -> event_model.EventTime:
    for event_time in event_times:
        tmp = event_time.model_dump()
        tmp["event_id"] = event.id
        event_time = event_model.EventTime(**tmp)
        db.add(event_time)
        await db.commit()
        await db.refresh(event_time)
    return event


async def update_event(
    db: AsyncSession, id: int, event_update: event_schema.EventCreate
) -> event_model.Event:
    tags = event_update.tags
    sql = select(event_model.Event).filter(event_model.Event.id == id)
    result: Result = await db.execute(sql)
    event = result.scalar_one()
    await tag_crud.create_event_tags(db, event_update, tags)
    tmp = event_update.model_dump(exclude={"tags"})
    for key, value in tmp.items():
        setattr(event, key, value)
    await db.commit()
    await db.refresh(event)
    return event


async def get_event(db: AsyncSession, id: int) -> event_model.Event:
    sql = (
        select(event_model.Event)
        .options(
            selectinload(event_model.Event.event_times),
            selectinload(event_model.Event.tags),
            selectinload(event_model.Event.reviews),
        )
        .filter(event_model.Event.id == id)
    )

    result: Result = await db.execute(sql)
    return result.scalar_one()


async def delete_event(db: AsyncSession, id: int) -> bool:
    sql = select(event_model.Event).filter(event_model.Event.id == id)
    result: Result = await db.execute(sql)
    event = result.scalar_one()
    db.delete(event)
    await db.commit()
    return True


async def get_event_from_tag(
    db: AsyncSession, tag_name: str, sort: str = "id", order: str = "asc"
) -> list[event_model.Event]:
    try:
        sort_column = getattr(event_model.Event, sort)
    except AttributeError:
        sort_column = event_model.Event.id
    tag = await tag_crud.get_tag_from_name(db, tag_name)
    sql = (
        select(event_model.Event)
        .join(event_model.Event.tags)
        .filter(event_model.Event.status == "1", event_model.Tag.id == tag.id)
        .order_by(sort_column if order == "asc" else sort_column.desc())
        .options(
            selectinload(event_model.Event.event_times),
            selectinload(event_model.Event.tags),
            selectinload(event_model.Event.reviews),
        )
    )
    result: Result = await db.execute(sql)
    return result.scalars().all()


# 開催時期が3日以内のイベントを取得
async def get_recent_events(db: AsyncSession) -> list[event_model.Event]:
    sql = select(event_model.Event).filter(
        event_model.Event.status == "1",
        event_model.Event.event_times.any(
            event_model.EventTime.start_time
            > datetime.datetime.now() - datetime.timedelta(days=3)
        ),
    )
    result: Result = await db.execute(sql)
    return result.scalars().all()


async def search_events(
    db: AsyncSession,
    keyword: str = "",
    sort: str = "id",
    order: str = "asc",
) -> list[event_model.Event]:
    try:
        sort_column = getattr(event_model.Event, sort)
    except AttributeError:
        sort_column = event_model.Event.id
    sql = (
        select(event_model.Event)
        .options(
            selectinload(event_model.Event.event_times),
            selectinload(event_model.Event.tags),
            selectinload(event_model.Event.reviews),
        )
        .filter(
            or_(
                event_model.Event.title.like(f"%{keyword}%"),
                event_model.Event.description.like(f"%{keyword}%"),
            ),
        )
        .order_by(sort_column if order == "asc" else sort_column.desc())
    )
    result: Result = await db.execute(sql)
    return result.scalars().all()


async def get_events(
    db: AsyncSession, sort: str = "id", order: str = "asc"
) -> list[event_model.Event]:
    try:
        sort_column = getattr(event_model.Event, sort)
    except AttributeError:
        sort_column = event_model.Event.id
    sql = (
        select(event_model.Event)
        .order_by(sort_column if order == "asc" else sort_column.desc())
        .options(
            selectinload(event_model.Event.event_times),
            selectinload(event_model.Event.tags),
            selectinload(event_model.Event.reviews),
        )
    )
    result: Result = await db.execute(sql)
    return result.scalars().all()
