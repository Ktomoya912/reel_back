from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.tag as tag_crud
from api import schemas
from api.dependencies import get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[schemas.Tag])
def get_tags(db: Session = Depends(get_db)):
    return tag_crud.get_tags(db)


@router.post("/", response_model=schemas.TagCreate)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    tag = tag_crud.get_tag_by_name(db, tag.name)
    if tag is None:
        tag = tag_crud.create_tag(db, tag)
    return tag
