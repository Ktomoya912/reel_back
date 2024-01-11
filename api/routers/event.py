from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.event as event_crud
import api.cruds.plan as plan_crud
import api.cruds.tag as tag_crud
from api import models, schemas
from api.dependencies import (
    common_parameters,
    get_admin_user,
    get_company_user,
    get_current_active_user,
    get_db,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=schemas.EventCreateResponse)
def create_event(
    current_user: Annotated[dict, Depends(get_company_user)],
    event_create: schemas.EventCreate,
    db: Session = Depends(get_db),
):
    event = event_crud.create_event(db, event_create, current_user.id)
    event = event_crud.create_event_times(db, event, event_create.event_times)
    event = tag_crud.create_event_tags(db, event, event_create.tags)
    return event


@router.post("/purchase-event", response_model=schemas.EventCreateResponse)
def purchase_event(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    purchase_data: schemas.EventArticleCreate,
    db: Session = Depends(get_db),
):
    purchase = plan_crud.purchase_plan(db, purchase_data.purchase, current_user)
    event = create_event(current_user, purchase_data.event, db)
    event.purchase = purchase
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=list[schemas.EventListView])
def get_events(
    common: Annotated[dict, Depends(common_parameters)],
    tag: str = "",
    only_active: bool = False,
):
    if tag:
        data = event_crud.get_event_by_tag(
            common["db"],
            tag,
        )
    else:
        data = event_crud.get_events(only_active=only_active, **common)
    return data[common["offset"] : common["offset"] + common["limit"]]  # noqa E203


@router.get("/{event_id}", response_model=schemas.Event)
def get_event(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    event = event_crud.watch_event(db, event_id, current_user.id)
    setattr(event, "is_favorite", event in current_user.event_bookmarks)
    return event


@router.put("/{event_id}", response_model=schemas.EventCreateResponse)
def update_event(
    event_id: int,
    event_update: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    return event_crud.update_event(db, event_id, event_update)


@router.put("/{event_id}/activate", response_model=schemas.EventListView)
def activate_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    event = event_crud.get_event(db, event_id)
    event.status = "1"
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    if event_crud.delete_event(db, event_id):
        return {"message": "Deleted successfully"}
    return {"message": "Failed to delete"}


@router.get("/recent/", response_model=list[schemas.EventListView])
def get_recent_events(db: Session = Depends(get_db)):
    return event_crud.get_recent_events(db)


@router.post("/{event_id}/bookmark")
def bookmark_event(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return event_crud.bookmark_event(db, event_id, current_user.id)


@router.delete("/{event_id}/bookmark")
def unbookmark_event(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return event_crud.unbookmark_event(db, event_id, current_user.id)


@router.post("/{event_id}/review", response_model=schemas.EventReview)
def post_review(
    event_id: int,
    review: schemas.EventReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return event_crud.create_review(db, event_id, current_user.id, review)


@router.put("/{event_id}/review", response_model=schemas.EventReview)
def update_review(
    event_id: int,
    review: schemas.EventReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return event_crud.update_review(db, event_id, current_user.id, review)


@router.delete("/{event_id}/review")
def delete_review(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return event_crud.delete_review(db, event_id, current_user.id)
