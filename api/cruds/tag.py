from sqlalchemy.orm.session import Session

import api.models.event as event_model
import api.models.tag as tag_model
import api.schemas.tag as tag_schema


def create_tag(db: Session, tag: tag_schema.TagCreate) -> tag_model.Tag:
    if tag is None:
        return None
    tmp = tag.model_dump()
    tag = tag_model.Tag(**tmp)
    db.add(tag)
    db.commit()

    return tag


def get_tag_from_name(db: Session, tag_name: str) -> tag_model.Tag:
    tag = db.query(tag_model.Tag).filter(tag_model.Tag.name == tag_name).first()
    return tag


def get_tags(db: Session) -> list[tag_model.Tag]:
    return db.query(tag_model.Tag).all()


def create_event_tags(
    db: Session, event: event_model.Event, tags: list[tag_schema.TagCreate]
) -> event_model.Event:
    event.tags = []
    for tag in tags:
        tag_model = get_tag_from_name(db, tag.name)
        if tag_model is None:
            tag_model = create_tag(db, tag)
        try:
            event.tags.append(tag_model)
            db.flush()
        except Exception:
            db.rollback()
    db.commit()

    return event
