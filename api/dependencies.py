from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

import api.cruds.user as user_crud
import api.schemas.user as user_schema
from api import config
from api.db import get_db

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@lru_cache
def get_config():
    return config.ProductConfig()


@lru_cache
def get_develop_config():
    return config.DevelopConfig()


@lru_cache
def get_test_config():
    return config.TestConfig()


async def get_current_user(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> user_schema.User:
    """現在のユーザーの取得"""
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = user_schema.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await user_crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    if settings.IS_PRODUCT:
        user.is_active = True
        await db.commit()
        await db.refresh(user)
    return user
