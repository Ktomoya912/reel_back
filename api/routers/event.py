from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.cruds.event as event_crud
import api.cruds.tag as tag_crud
import api.schemas.event as event_schema
from api.db import get_db

router = APIRouter()


async def common_parameters(
    db: AsyncSession = Depends(get_db),
    sort: str = "id",
    order: str = "asc",
    offset: int = 0,
    limit: int = 100,
):
    return {"db": db, "sort": sort, "order": order, "offset": offset, "limit": limit}


@router.get("/events/", response_model=list[event_schema.Event])
async def get_events(
    common: Annotated[dict, Depends(common_parameters)], tag: str = ""
):
    if tag:
        data = await tag_crud.get_event_from_tag(
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


@router.get("/events/search", response_model=list[event_schema.Event])
async def search_events(db: AsyncSession = Depends(get_db), keyword: str = ""):
    return await event_crud.search_events(db, keyword)
