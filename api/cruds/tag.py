from sqlalchemy.orm.session import Session

from api import models, schemas


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    if tag is None:
        return None
    tmp = tag.model_dump()
    tag = models.Tag(**tmp)
    db.add(tag)
    db.commit()

    return tag


def get_tag_from_name(db: Session, tag_name: str) -> models.Tag:
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    return tag


def get_tags(db: Session) -> list[models.Tag]:
    return db.query(models.Tag).all()


def create_event_tags(
    db: Session, event: models.Event, tags: list[schemas.TagCreate]
) -> models.Event:
    event.tags = []
    for tag in tags:
        models = get_tag_from_name(db, tag.name)
        if models is None:
            models = create_tag(db, tag)
        try:
            event.tags.append(models)
            db.flush()
        except Exception:
            db.rollback()
    db.commit()

    return event
