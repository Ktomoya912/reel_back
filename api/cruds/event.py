import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import or_

import api.cruds.tag as tag_crud
from api import models, schemas


def create_event(
    db: Session, event_create: schemas.EventCreate, user_id: int
) -> models.Event:
    tmp = event_create.model_dump(exclude={"tags", "event_times"})
    event = models.Event(**tmp, user_id=user_id)
    db.add(event)
    db.commit()
    return event


def create_event_times(
    db: Session,
    event: models.Event,
    event_times: list[schemas.EventTimeCreate],
) -> models.EventTime:
    for event_time in event_times:
        tmp = event_time.model_dump()
        event_time = models.EventTime(**tmp)
        event.event_times.append(event_time)
    db.commit()

    return event


def update_event(
    db: Session, id: int, event_update: schemas.EventCreate
) -> models.Event:
    tags = event_update.tags
    sql = select(models.Event).filter(models.Event.id == id)
    result: Result = db.execute(sql)
    event = result.scalar_one()
    tag_crud.create_event_tags(db, event_update, tags)
    tmp = event_update.model_dump(exclude={"tags"})
    for key, value in tmp.items():
        setattr(event, key, value)
    db.commit()

    return event


def get_event(db: Session, id: int) -> models.Event:
    event = db.query(models.Event).filter(models.Event.id == id).first()
    return event


def watch_event(db: Session, id: int, user_id: int) -> models.Event:
    event = get_event(db, id)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    watched_users = (
        db.query(models.EventWatched)
        .filter(
            models.EventWatched.user_id == user.id,
            models.EventWatched.event_id == event.id,
        )
        .first()
    )
    if watched_users is None:
        watched_users = models.EventWatched(user_id=user.id, event_id=event.id)
        db.add(watched_users)
    else:
        watched_users.count += 1
    db.commit()
    return event


def delete_event(db: Session, id: int) -> bool:
    event = db.query(models.Event).filter(models.Event.id == id).first()
    db.delete(event)
    db.commit()
    return True


def get_event_from_tag(db: Session, tag_name: str) -> list[models.Event]:
    tag = tag_crud.get_tag_from_name(db, tag_name)
    return tag.events


# 開催時期が3日以内のイベントを取得
def get_recent_events(db: Session) -> list[models.Event]:
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(days=3)
    events = (
        db.query(models.Event)
        .join(models.EventTime)
        .filter(
            models.EventTime.start_time >= now,
            models.EventTime.start_time <= start_time,
            models.Event.status == "1",
        )
        .all()
    )
    return events


def search_events(
    db: Session,
    keyword: str = "",
) -> list[models.Event]:
    events = (
        db.query(models.Event)
        .filter(
            or_(
                models.Event.name.contains(keyword),
                models.Event.description.contains(keyword),
            )
        )
        .filter(models.Event.status == "1")
        .all()
    )
    return events


def get_events(db: Session, only_active: bool = True) -> list[models.Event]:
    if only_active:
        return db.query(models.Event).filter(models.Event.status == "1").all()
    return db.query(models.Event).all()
