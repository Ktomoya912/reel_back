import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import or_

import api.models.event as event_model
import api.schemas.event as event_schema


async def create_event(
    db: AsyncSession, event_create: event_schema.EventCreate
) -> event_model.Event:
    tmp = event_create.model_dump()
    event = event_model.Event(**tmp)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_event(db: AsyncSession, id: int) -> event_model.Event:
    sql = select(event_model.Event).filter(event_model.Event.id == id)
    result: Result = await db.execute(sql)
    return result.scalar_one()


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
    return result.scalars()


async def search_events(
    db: AsyncSession,
    keyword: str = "",
) -> list[event_model.Event]:
    sql = select(event_model.Event).filter(
        or_(
            event_model.Event.title.like(f"%{keyword}%"),
            event_model.Event.description.like(f"%{keyword}%"),
        ),
    )
    result: Result = await db.execute(sql)
    return result.scalars()


async def get_events(
    db: AsyncSession, sort: str = "id", order: str = "asc"
) -> list[event_model.Event]:
    try:
        sort_column = getattr(event_model.Event, sort)
    except AttributeError:
        sort_column = event_model.Event.id
    sql = select(event_model.Event).order_by(
        sort_column if order == "asc" else sort_column.desc()
    )
    result: Result = await db.execute(sql)
    return result.scalars()
