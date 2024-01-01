import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import or_

import api.cruds.tag as tag_crud
import api.models.event as event_model
import api.models.user as user_model
import api.schemas.event as event_schema


def create_event(
    db: Session, event_create: event_schema.EventCreate, user_id: int
) -> event_model.Event:
    tmp = event_create.model_dump(exclude={"tags", "event_times"})
    event = event_model.Event(**tmp, user_id=user_id)
    db.add(event)
    db.commit()
    return event


def create_event_times(
    db: Session,
    event: event_model.Event,
    event_times: list[event_schema.EventTimeCreate],
) -> event_model.EventTime:
    for event_time in event_times:
        tmp = event_time.model_dump()
        event_time = event_model.EventTime(**tmp)
        event.event_times.append(event_time)
    db.commit()

    return event


def update_event(
    db: Session, id: int, event_update: event_schema.EventCreate
) -> event_model.Event:
    tags = event_update.tags
    sql = select(event_model.Event).filter(event_model.Event.id == id)
    result: Result = db.execute(sql)
    event = result.scalar_one()
    tag_crud.create_event_tags(db, event_update, tags)
    tmp = event_update.model_dump(exclude={"tags"})
    for key, value in tmp.items():
        setattr(event, key, value)
    db.commit()

    return event


def get_event(db: Session, id: int) -> event_model.Event:
    event = db.query(event_model.Event).filter(event_model.Event.id == id).first()
    return event


def watch_event(db: Session, id: int, user_id: int) -> event_model.Event:
    event = get_event(db, id)
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    watched_users = (
        db.query(event_model.EventWatched)
        .filter(
            event_model.EventWatched.user_id == user.id,
            event_model.EventWatched.event_id == event.id,
        )
        .first()
    )
    if watched_users is None:
        watched_users = event_model.EventWatched(user_id=user.id, event_id=event.id)
        db.add(watched_users)
    else:
        watched_users.count += 1
    db.commit()
    return event


def delete_event(db: Session, id: int) -> bool:
    event = db.query(event_model.Event).filter(event_model.Event.id == id).first()
    db.delete(event)
    db.commit()
    return True


def get_event_from_tag(db: Session, tag_name: str) -> list[event_model.Event]:
    tag = tag_crud.get_tag_from_name(db, tag_name)
    return tag.events


# 開催時期が3日以内のイベントを取得
def get_recent_events(db: Session) -> list[event_model.Event]:
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(days=3)
    events = (
        db.query(event_model.Event)
        .join(event_model.EventTime)
        .filter(
            event_model.EventTime.start_time >= now,
            event_model.EventTime.start_time <= start_time,
            event_model.Event.status == "1",
        )
        .all()
    )
    return events


def search_events(
    db: Session,
    keyword: str = "",
) -> list[event_model.Event]:
    events = (
        db.query(event_model.Event)
        .filter(
            or_(
                event_model.Event.name.contains(keyword),
                event_model.Event.description.contains(keyword),
            )
        )
        .filter(event_model.Event.status == "1")
        .all()
    )
    return events


def get_events(db: Session, only_active: bool = True) -> list[event_model.Event]:
    if only_active:
        return db.query(event_model.Event).filter(event_model.Event.status == "1").all()
    return db.query(event_model.Event).all()
