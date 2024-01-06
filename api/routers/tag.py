from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.tag as tag_crud
from api import schemas
from api.dependencies import get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[schemas.Tag])
def get_tags(db: Session = Depends(get_db)):
    return tag_crud.get_tags(db)
