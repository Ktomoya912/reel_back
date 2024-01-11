from sqlalchemy.orm.session import Session

from api import models, schemas


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    if tag is None:
        return None
    tmp = tag.model_dump()
    tag = models.Tag(**tmp)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def get_tag_by_name(db: Session, tag_name: str) -> models.Tag:
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    return tag


def get_tags(db: Session) -> list[models.Tag]:
    return db.query(models.Tag).all()


def create_event_tags(
    db: Session, event: models.Event, tags: list[schemas.TagCreate]
) -> models.Event:
    event.tags = []
    for tag in tags:
        models = get_tag_by_name(db, tag.name)
        if models is None:
            models = create_tag(db, tag)
        try:
            event.tags.append(models)
            db.flush()
        except Exception:
            db.rollback()
    db.commit()
    db.refresh(event)
    return event


def create_job_tags(
    db: Session, job: models.Job, tags: list[schemas.TagCreate]
) -> models.Job:
    job.tags = []
    for tag in tags:
        models = get_tag_by_name(db, tag.name)
        if models is None:
            models = create_tag(db, tag)
        try:
            job.tags.append(models)
            db.flush()
        except Exception:
            db.rollback()
    db.commit()
    db.refresh(job)
    return job
