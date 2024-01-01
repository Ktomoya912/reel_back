from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.message as message_crud
import api.schemas.message as message_schema
import api.schemas.user as user_schema
from api.db import get_db

from ..dependencies import get_current_user

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_user),
) -> list[list[message_schema.Message]]:
    job_messages = message_crud.get_messages(db, current_user.id, "J")
    event_messages = message_crud.get_messages(db, current_user.id, "E")
    return [
        event_messages,
        job_messages,
    ]


@router.post("/", response_model=message_schema.Message)
def create_notification(
    message_create: message_schema.MessageCreate,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_user),
):
    message = message_crud.create_message(db, message_create)
    message_crud.send_message(db, message_create.user_list, message.id)

    return message


@router.post("/{message_id}/read")
def read_notification(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_user),
) -> message_schema.Message:
    message_crud.read_message(db, message_id, current_user.id)
    message = message_crud.get_message(db, message_id)
    return message
