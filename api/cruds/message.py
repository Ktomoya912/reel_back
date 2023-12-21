from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import api.models.message as message_model
import api.schemas.message as message_schema


async def create_message(
    db: AsyncSession, message_create: message_schema.MessageCreate
) -> message_model.Message:
    message = message_model.Message(**message_create.model_dump())
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def send_message(
    db: AsyncSession, user_list: list[int], message_id: int
) -> list[message_model.MessageBox]:
    message_box_list = []
    for user_id in user_list:
        message_box = message_model.MessageBox(user_id=user_id, message_id=message_id)
        db.add(message_box)
        message_box_list.append(message_box)
    await db.commit()
    return message_box_list


async def get_messages(
    db: AsyncSession, user_id: int, type: str = None
) -> list[message_model.Message]:
    sql = (
        select(message_model.Message)
        .join(message_model.MessageBox)
        .filter(
            message_model.MessageBox.user_id == user_id,
            ~message_model.MessageBox.is_read,
            message_model.Message.type == type,
        )
    )
    result: Result = await db.execute(sql)
    return result.scalars()
