from sqlalchemy.orm.session import Session

import api.models.event as event_model
import api.models.job as job_model
import api.models.tag as tag_model
import api.schemas.tag as tag_schema


def create_tag(db: Session, tag_create: tag_schema.TagCreate) -> tag_model.Tag:
    tag = get_tag_from_name(db, tag_create.name)
    if tag is not None:
        return tag
    tag = tag_model.Tag(**tag_create.model_dump())
    db.add(tag)
    db.commit()

    return tag


def get_tag_from_name(db: Session, tag_name: str) -> tag_model.Tag:
    tag = db.query(tag_model.Tag).filter(tag_model.Tag.name == tag_name).first()
    return tag


def create_job_tags(db: Session, job: job_model.Job, tags: list[str]) -> job_model.Job:
    job.tags = []
    for tag in tags:
        tag = get_tag_from_name(db, tag)
        if tag is None:
            tag = create_tag(db, tag_schema.TagCreate(name=tag))
        job.tags.append(tag)
    db.commit()

    return job


def create_event_tags(
    db: Session, event: event_model.Event, tags: list[str]
) -> event_model.Event:
    event.tags = []
    for tag in tags:
        tag = get_tag_from_name(db, tag)
        if tag is None:
            tag = create_tag(db, tag_schema.TagCreate(name=tag))
        event.tags.append(tag)
    db.commit()

    return event
