from typing import Literal

from sqlalchemy.orm.session import Session

import api.models.message as message_model
import api.schemas.message as message_schema


def create_message(
    db: Session, message_create: message_schema.MessageCreate
) -> message_model.Message:
    message = message_model.Message(**message_create.model_dump(exclude={"user_list"}))
    db.add(message)
    db.commit()
    return message


def send_message(
    db: Session, user_list: list[int], message_id: int
) -> list[message_model.MessageBox]:
    message_box_list = []
    for user_id in user_list:
        message_box = message_model.MessageBox(user_id=user_id, message_id=message_id)
        db.add(message_box)
        message_box_list.append(message_box)
    db.commit()
    return message_box_list


def get_messages(
    db: Session, user_id: int, type: Literal["J", "E"]
) -> list[message_model.Message]:
    messages = (
        db.query(message_model.Message)
        .join(message_model.MessageBox)
        .filter(message_model.MessageBox.user_id == user_id)
        .filter(message_model.Message.type == type)
        .all()
    )
    return messages


def get_message(db: Session, message_id: int) -> message_model.Message:
    message = db.query(message_model.Message).filter(
        message_model.Message.id == message_id
    )
    return message


def read_message(
    db: Session, message_id: int, user_id: int
) -> message_model.MessageBox:
    message_box = (
        db.query(message_model.MessageBox)
        .filter(message_model.MessageBox.message_id == message_id)
        .filter(message_model.MessageBox.user_id == user_id)
        .first()
    )
    message_box.is_read = True
    db.commit()
    return message_box
