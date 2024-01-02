from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm.session import Session

import api.cruds.user as user_crud
from api import models, schemas
from api import config
from api.db import Session

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


@lru_cache
def get_config():
    return config.ProductConfig()


@lru_cache
def get_develop_config():
    return config.DevelopConfig()


@lru_cache
def get_test_config():
    return config.TestConfig()


def get_db(request: Request) -> Session:
    return request.state.db


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    settings: config.BaseConfig = Depends(get_config),
) -> models.User:
    """現在のユーザーの取得"""
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active and settings.IS_PRODUCT:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_general_user(
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.user_type in ["a", "g"]:
        return current_user
    raise HTTPException(status_code=400, detail="General user only")


def get_company_user(
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.user_type in ["a", "c"]:
        return current_user
    raise HTTPException(status_code=400, detail="Company user only")


def get_admin_user(
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.user_type == "a":
        return current_user
    raise HTTPException(status_code=400, detail="Admin user only")
