import os
from datetime import datetime, timedelta
from typing import Optional, Union

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import api.models.company as company_model
import api.models.user as user_model
import api.schemas.user as user_schema

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    """パスワードの検証"""
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Union[bool, user_model.User]:
    """ユーザーの認証"""
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """アクセストークンの生成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
    return encoded_jwt


async def create_company(
    db: AsyncSession, company_create: user_schema.CompanyCreate
) -> company_model.Company:
    """会社の作成"""
    tmp = company_create.model_dump()
    company = company_model.Company(**tmp)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def create_user_company(
    db: AsyncSession, user_create: user_schema.UserCreateCompany
) -> user_model.User:
    """ユーザーと会社の作成"""
    tmp = user_create.model_dump()
    company = await create_company(db, user_create.company)
    tmp["company"] = company
    user = user_model.User(**tmp)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_user(
    db: AsyncSession, user_create: user_schema.UserCreate
) -> user_model.User:
    """ユーザーの作成"""
    tmp = user_create.model_dump()
    user = user_model.User(**tmp)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession) -> list[user_model.User]:
    sql = select(user_model.User).options(selectinload(user_model.User.company))
    result: Result = await db.execute(sql)
    return result.scalars()


async def get_user_by_username(
    db: AsyncSession, username: str
) -> Optional[user_model.User]:
    """ユーザー名からユーザー情報を取得"""
    sql = (
        select(user_model.User)
        .options(selectinload(user_model.User.company))
        .filter(user_model.User.username == username)
    )
    result: Result = await db.execute(sql)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[user_model.User]:
    """メールアドレスからユーザー情報を取得"""
    sql = (
        select(user_model.User)
        .options(selectinload(user_model.User.company))
        .filter(user_model.User.email == email)
    )
    result: Result = await db.execute(sql)
    return result.scalar_one_or_none()


async def get_user(db: AsyncSession, user_id: int) -> Optional[user_model.User]:
    """idからユーザー情報を取得"""
    sql = (
        select(user_model.User)
        .options(selectinload(user_model.User.company))
        .filter(user_model.User.id == user_id)
    )
    result: Result = await db.execute(sql)
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession, user_create: user_schema.UserCreate, original: user_model.User
) -> user_model.User:
    original.username = user_create.username
    await db.commit()
    await db.refresh(original)
    return original


async def update_user_password(
    db: AsyncSession, user: user_model.User, password: str
) -> user_model.User:
    user.password = password
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: user_model.User) -> None:
    await db.delete(user)
    await db.commit()
