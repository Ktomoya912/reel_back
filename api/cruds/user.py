from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import api.models.user as user_model
import api.schemas.user as user_schema
from sqlalchemy.engine import Result
from typing import Optional
from hashlib import sha256


async def create_user(
    db: AsyncSession, user_create: user_schema.UserCreate
) -> user_model.User:
    tmp = user_create.model_dump()
    user = user_model.User(**tmp)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession) -> list[tuple[int, str, str, str, str]]:
    result: Result = await db.execute(
        select(
            user_model.User.id,
            user_model.User.username,
            user_model.User.email,
            user_model.User.gender,
            user_model.User.user_type,
            user_model.User.password,
            user_model.User.birthday,
        )
    )
    return result.all()


async def get_user(db: AsyncSession, user_id: int) -> Optional[user_model.User]:
    result: Result = await db.execute(
        select(
            user_model.User.id,
            user_model.User.username,
            user_model.User.email,
            user_model.User.password,
            user_model.User.birthday,
        )
    )
    return result.all()[0]


async def get_user_model(db: AsyncSession, user_id: int) -> Optional[user_model.User]:
    result: Result = await db.execute(
        select(user_model.User).filter(user_model.User.id == user_id)
    )
    user: Optional[tuple[user_model.User]] = result.first()
    return user[0] if user else None


async def update_user(
    db: AsyncSession, user_create: user_schema.UserCreate, original: user_model.User
) -> user_model.User:
    original.username = user_create.username
    await db.commit()
    await db.refresh(original)
    return original


async def delete_user(db: AsyncSession, user: user_model.User) -> None:
    await db.delete(user)
    await db.commit()
