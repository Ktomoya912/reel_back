from typing import Literal

from sqlalchemy.orm.session import Session


from api import models, schemas


def create_message(
    db: Session, message_create: schemas.MessageCreate
) -> models.Message:
    message = models.Message(**message_create.model_dump(exclude={"user_list"}))
    db.add(message)
    db.commit()
    return message


def send_message(
    db: Session, user_list: list[int], message_id: int
) -> list[models.MessageBox]:
    message_box_list = []
    for user_id in user_list:
        message_box = models.MessageBox(user_id=user_id, message_id=message_id)
        db.add(message_box)
        message_box_list.append(message_box)
    db.commit()
    return message_box_list


def get_messages(
    db: Session, user_id: int, type: Literal["J", "E"]
) -> list[models.Message]:
    messages = (
        db.query(models.Message)
        .join(models.MessageBox)
        .filter(models.MessageBox.user_id == user_id)
        .filter(models.Message.type == type)
        .all()
    )
    return messages


def get_message(db: Session, message_id: int) -> models.Message:
    message = db.query(models.Message).filter(models.Message.id == message_id)
    return message


def read_message(db: Session, message_id: int, user_id: int) -> models.MessageBox:
    message_box = (
        db.query(models.MessageBox)
        .filter(models.MessageBox.message_id == message_id)
        .filter(models.MessageBox.user_id == user_id)
        .first()
    )
    message_box.is_read = True
    db.commit()
    return message_box
