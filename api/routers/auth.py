import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

import api.cruds.user as user_crud
import api.schemas.user as user_schema
from api.db import get_db

router = APIRouter(prefix="/auth")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> user_schema.User:
    """現在のユーザーの取得

    Args:
        db (AsyncSession, optional): DBセッション
        token (str, optional): アクセストークン

    Raises:
        credentials_exception: 認証エラー

    Returns:
        user_schema.User: ユーザー情報
    """
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = user_schema.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await user_crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def confirm_verification_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> str:
    """メール認証トークンの確認

    Args:
        token (str, optional): 認証トークン. Defaults to Depends(oauth2_scheme).
        db (AsyncSession, optional): DBセッション. Defaults to Depends(get_db).

    Raises:
        credentials_exception: 認証エラー

    Returns:
        str: 確認結果
    """
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await user_crud.get_user_by_username(db, username=username)
    except JWTError:
        raise credentials_exception
    if not user:
        raise credentials_exception
    user.is_active = True
    await db.commit()
    return "ok"


@router.post("/token", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> dict:
    user = await user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await user_crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
