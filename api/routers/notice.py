from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.message as message_crud
from api import models, schemas

from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/notices", tags=["通知"])


@router.get("/", response_model=list[list[schemas.Message]], summary="通知取得")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    既読でない通知を取得する。

    - index 0: イベント通知
    - index 1: 求人通知
    """
    job_messages = message_crud.get_messages(db, current_user.id, "J")
    event_messages = message_crud.get_messages(db, current_user.id, "E")
    return [
        event_messages,
        job_messages,
    ]


@router.post("/", response_model=schemas.Message, summary="通知作成")
def create_notification(
    message_create: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    必要データを受け取り、通知を作成する。
    レスポンスとして、作成された通知の情報を返す。
    """
    message = message_crud.create_message(db, message_create)
    message_crud.send_message(db, message_create.user_list, message.id)

    return message


@router.post("/{message_id}/read", response_model=schemas.Message, summary="通知既読")
def read_notification(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    通知IDを受け取り、通知を既読にする。
    レスポンスとして、既読にした通知の情報を返す。"""
    message_crud.read_message(db, message_id, current_user.id)
    message = message_crud.get_message(db, message_id)
    return message
