from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.event as event_crud
import api.cruds.tag as tag_crud
import api.schemas.event as event_schema
from api.dependencies import get_company_user, get_current_active_user, get_db

router = APIRouter(prefix="/events", tags=["events"])


def common_parameters(
    db: Session = Depends(get_db),
    sort: str = "id",
    order: str = "asc",
    offset: int = 0,
    limit: int = 100,
):
    return {"db": db, "sort": sort, "order": order, "offset": offset, "limit": limit}


@router.post("/", response_model=event_schema.EventListView)
def create_event(
    current_user: Annotated[dict, Depends(get_company_user)],
    event_create: event_schema.EventCreate,
    db: Session = Depends(get_db),
):
    event = event_crud.create_event(db, event_create, current_user.id)
    event = event_crud.create_event_times(db, event, event_create.event_times)
    event = tag_crud.create_event_tags(db, event, event_create.tags)
    return event


@router.get("/", response_model=list[event_schema.EventListView])
def get_events(
    common: Annotated[dict, Depends(common_parameters)],
    tag: str = "",
    only_active: bool = False,
):
    if tag:
        data = event_crud.get_event_from_tag(
            common["db"],
            tag,
        )
    else:
        data = event_crud.get_events(
            common["db"],
            only_active=only_active,
        )
    return data[common["offset"] : common["offset"] + common["limit"]]  # noqa E203


@router.get("/{event_id}", response_model=event_schema.Event)
def get_event(
    event_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return event_crud.watch_event(db, event_id, current_user.id)


@router.put("/{event_id}", response_model=event_schema.Event)
def update_event(
    event_id: int,
    event_update: event_schema.EventCreate,
    db: Session = Depends(get_db),
):
    return event_crud.update_event(db, event_id, event_update)


@router.put("/{event_id}/activate", response_model=event_schema.Event)
def activate_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = event_crud.get_event(db, event_id)
    event.status = "1"
    db.commit()

    return event


@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    if event_crud.delete_event(db, event_id):
        return {"message": "Deleted successfully"}
    return {"message": "Failed to delete"}


@router.get("/recent/", response_model=list[event_schema.EventListView])
def get_recent_events(db: Session = Depends(get_db)):
    return event_crud.get_recent_events(db)


@router.get("/search/", response_model=list[event_schema.EventListView])
def search_events(db: Session = Depends(get_db), keyword: str = ""):
    print(keyword)
    return event_crud.search_events(db, keyword)
