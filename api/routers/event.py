from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.cruds.event as event_crud
import api.cruds.tag as tag_crud
import api.schemas.event as event_schema
from api.db import get_db
from api.dependencies import get_current_active_user

router = APIRouter(prefix="/events", tags=["events"])


async def common_parameters(
    db: AsyncSession = Depends(get_db),
    sort: str = "id",
    order: str = "asc",
    offset: int = 0,
    limit: int = 100,
):
    return {"db": db, "sort": sort, "order": order, "offset": offset, "limit": limit}


@router.post("/")
async def create_event(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    event_create: event_schema.EventCreate,
    db: AsyncSession = Depends(get_db),
):
    event = await event_crud.create_event(db, event_create)
    event = await event_crud.create_event_times(db, event, event_create.event_times)
    # event = await tag_crud.create_event_tags(db, event, event_create.tags)
    return {"message": "Created successfully"}


@router.get("/", response_model=list[event_schema.Event])
async def get_events(
    common: Annotated[dict, Depends(common_parameters)], tag: str = ""
):
    if tag:
        data = await event_crud.get_event_from_tag(
            common["db"],
            tag,
            common["sort"],
            common["order"],
        )
    data = await event_crud.get_events(
        common["db"],
        common["sort"],
        common["order"],
    )
    return data[common["offset"] : common["offset"] + common["limit"]]  # noqa E203


@router.get("/{event_id}", response_model=event_schema.Event)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    return await event_crud.get_event(db, event_id)


@router.put("/{event_id}", response_model=event_schema.Event)
async def update_event(
    event_id: int,
    event_update: event_schema.EventCreate,
    db: AsyncSession = Depends(get_db),
):
    return await event_crud.update_event(db, event_id, event_update)


@router.put("/{event_id}/activate", response_model=event_schema.Event)
async def activate_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    event = await event_crud.get_event(db, event_id)
    event.status = "1"
    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}")
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db)):
    if await event_crud.delete_event(db, event_id):
        return {"message": "Deleted successfully"}
    return {"message": "Failed to delete"}


@router.get("/recent", response_model=list[event_schema.Event])
async def get_recent_events(db: AsyncSession = Depends(get_db)):
    return await event_crud.get_recent_events(db)


@router.get("/search", response_model=list[event_schema.Event])
async def search_events(db: AsyncSession = Depends(get_db), keyword: str = ""):
    return await event_crud.search_events(db, keyword)
