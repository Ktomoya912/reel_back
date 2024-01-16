import datetime
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import func, or_

import api.cruds.tag as tag_crud
from api import models, schemas
from api.utils import get_jst_now


def create_event(
    db: Session, event_create: schemas.EventCreate, user_id: int
) -> models.Event:
    tmp = event_create.model_dump(exclude={"tags", "event_times"})
    event = models.Event(**tmp, user_id=user_id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def create_event_times(
    db: Session,
    event: models.Event,
    event_times: list[schemas.EventTimeCreate],
) -> models.EventTime:
    results = []
    for event_time in event_times:
        tmp = event_time.model_dump()
        event_time = db.query(models.EventTime).filter_by(**tmp).first()
        if event_time is None:
            event_time = models.EventTime(**tmp)
        results.append(event_time)
    event.event_times = results
    db.commit()
    db.refresh(event)
    return event


def update_event(
    db: Session, id: int, event_update: schemas.EventCreate
) -> models.Event:
    tags = event_update.tags
    event = get_event(db, id)
    tag_crud.create_event_tags(db, event, tags)
    event = create_event_times(db, event, event_update.event_times)
    tmp = event_update.model_dump(exclude={"tags", "event_times"}, exclude_unset=True)
    for key, value in tmp.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


def get_event(db: Session, id: int) -> models.Event:
    event = db.query(models.Event).filter(models.Event.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event Not Found")
    return event


def watch_event(db: Session, event_id: int, user_id: int) -> models.Event:
    event = get_event(db, event_id)
    watched_users = (
        db.query(models.EventWatched)
        .filter(
            models.EventWatched.user_id == user_id,
            models.EventWatched.event_id == event_id,
        )
        .first()
    )
    if watched_users is None:
        watched_users = models.EventWatched(user_id=user_id, event_id=event_id)
        db.add(watched_users)
    else:
        watched_users.count += 1
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, id: int) -> bool:
    event = db.query(models.Event).filter(models.Event.id == id).first()
    db.delete(event)
    db.commit()
    return True


def get_event_by_tag(db: Session, tag_name: str) -> list[models.Event]:
    tag = tag_crud.get_tag_by_name(db, tag_name)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag Not Found")
    return tag.events


# 開催時期が3日以内のイベントを取得
def get_recent_events(db: Session) -> list[models.Event]:
    now = get_jst_now()
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


def get_events(
    db: Session,
    type: Literal["all", "active", "inactive", "draft"] = "all",
    keyword: str = "",
    sort: str = "new",
    order: str = "desc",
    offset: int = 0,
    limit: int = 100,
):
    query = db.query(models.Event)
    if type != "all":
        query = query.filter(models.Event.status == type)
    if keyword != "":
        query = query.filter(
            or_(
                models.Event.name.contains(keyword),
                models.Event.description.contains(keyword),
                models.Event.tags.any(models.Tag.name.contains(keyword)),
            )
        )
    if sort == "id":
        query = get_events_by_id(query)
    elif sort == "review":
        query = get_events_by_review(query)
    elif sort == "watched":
        query = get_events_by_watched(query)
    elif sort == "favorite":
        query = get_events_by_bookmark(query)
    elif sort == "pv":
        query = get_events_by_pv(query)
    else:
        query = get_events_by_recent(query)
    return query.offset(offset).limit(limit).all()


# Reviewの評価平均順にイベントを取得
def get_events_by_review(query):
    return (
        query.outerjoin(models.EventReview)
        .order_by(func.avg(models.EventReview.review_point).desc())
        .group_by(models.Event.id)
    )


def get_events_by_pv(query):
    return (
        query.join(models.EventWatched)
        .order_by(func.sum(models.EventWatched.count).desc())
        .group_by(models.Event.id)
    )


def get_events_by_watched(query):
    return (
        query.join(models.EventWatched)
        .order_by(func.sum(models.EventWatched.count).desc())
        .group_by(models.Event.id)
    )


def get_events_by_id(query):
    return query.order_by(models.Event.id.desc())


def get_events_by_recent(query):
    now = get_jst_now()
    # 現在日時と開催日時の差が小さい順にイベントを取得、開催日時が過ぎているものは除外
    return (
        query.join(models.EventTime)
        .filter(models.EventTime.start_time >= now)
        .order_by(models.EventTime.start_time)
    )


def get_events_by_bookmark(query):
    return (
        query.outerjoin(models.EventBookmark)
        .order_by(func.count(models.EventBookmark.user_id).desc())
        .group_by(models.Event.id)
    )


def create_review(
    db: Session, event_id: int, user_id: int, review: schemas.EventReviewCreate
):
    event_review = models.EventReview(
        **review.model_dump(), user_id=user_id, event_id=event_id
    )
    db.add(event_review)
    db.commit()
    db.refresh(event_review)
    return event_review


def get_review(db: Session, event_id: int, user_id: int):
    return (
        db.query(models.EventReview)
        .filter(
            models.EventReview.user_id == user_id,
            models.EventReview.event_id == event_id,
        )
        .first()
    )


def update_review(
    db: Session, event_id: int, user_id: int, review: schemas.EventReviewCreate
):
    event_review = get_review(db, event_id, user_id)
    tmp = review.model_dump(exclude_unset=True)
    for key, value in tmp.items():
        setattr(event_review, key, value)
    db.commit()
    db.refresh(event_review)
    return event_review


def delete_review(db: Session, event_id: int, user_id: int):
    event_review = get_review(db, event_id, user_id)
    db.delete(event_review)
    db.commit()
    return True


def toggle_bookmark_event(db: Session, event_id: int, user_id: int):
    bookmark = (
        db.query(models.EventBookmark)
        .filter(
            models.EventBookmark.user_id == user_id,
            models.EventBookmark.event_id == event_id,
        )
        .first()
    )
    if bookmark:
        db.delete(bookmark)
        db.commit()
        return False
    else:
        bookmark = models.EventBookmark(user_id=user_id, event_id=event_id)
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return True


def get_event_impressions(
    db: Session,
    event_id: int,
):
    def get_age_range(
        age: int,
    ) -> Literal["under_20", "20-24", "25-29", "30-34", "35-39", "over_40"]:
        if age < 20:
            return "under_20"
        elif age < 25:
            return "20-24"
        elif age < 30:
            return "25-29"
        elif age < 35:
            return "30-34"
        elif age < 40:
            return "35-39"
        else:
            return "over_40"

    event = get_event(db, event_id)
    favorite_user_count = len(event.bookmark_users)
    pv = sum([watch.count for watch in event.watched_user_link])
    review_count = len(event.reviews)

    age = {
        "o": {
            "under_20": 0,
            "20-24": 0,
            "25-29": 0,
            "30-34": 0,
            "35-39": 0,
            "over_40": 0,
        },
        "m": {
            "under_20": 0,
            "20-24": 0,
            "25-29": 0,
            "30-34": 0,
            "35-39": 0,
            "over_40": 0,
        },
        "f": {
            "under_20": 0,
            "20-24": 0,
            "25-29": 0,
            "30-34": 0,
            "35-39": 0,
            "over_40": 0,
        },
    }

    for link in event.watched_user_link:
        user_age = get_jst_now().year - link.user.birthday.year
        age[link.user.sex][get_age_range(user_age)] += 1

    return {
        "favorite_user_count": favorite_user_count,
        "pv": pv,
        "review_count": review_count,
        "sex": age,
    }
