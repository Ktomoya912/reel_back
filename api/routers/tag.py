from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.tag as tag_crud
import api.schemas.tag as tag_schema
from api.db import get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[tag_schema.Tag])
def get_tags(db: Session = Depends(get_db)):
    return tag_crud.get_tags(db)
