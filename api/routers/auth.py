import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

import api.cruds.user as user_crud
import api.schemas.user as user_schema
from api.db import get_db
from api.modules.email import send_email

router = APIRouter(prefix="/auth")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    is_email: bool = False,
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
    if is_email:
        user.is_active = True
        await db.commit()
        await db.refresh(user)
    return user


@router.post("/token", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> dict:
    user = await user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user.is_active:
        # メールでの認証が完了していない場合
        raise HTTPException(status_code=400, detail="Inactive user")
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await user_crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/send-verification-email")
async def send_verification_email(
    email: str, db: AsyncSession = Depends(get_db)
) -> None:
    """メール認証のメール送信

    Args:
        email (str): メールアドレス
        db (AsyncSession, optional): DBセッション. Defaults to Depends(get_db).
    """
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # if user.is_active:
    #     raise HTTPException(status_code=400, detail="User already active")
    token = await user_crud.create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=15)
    )
    sender = os.getenv("MAIL_SENDER")
    if not sender:
        raise Exception("環境変数が設定されていません。.envファイルにMAIL_SENDERを設定してください。")
    send_email(
        from_=sender,
        to=email,
        subject="Verify your email",
        body=f"""
        <html>
            <head></head>
            <body>
                <p>Verify your email</p>
                <a href="http://localhost:8000/auth/email-confirmation/{token}">Verify</a>
            </body>
        </html>
        """,
    )
    return "Email sent"


@router.get("/email-confirmation/{token}", response_class=HTMLResponse)
async def email_confirmation(token: str, db: AsyncSession = Depends(get_db)) -> str:
    """メール認証

    Args:
        token (str, optional): 認証トークン. Defaults to Depends(oauth2_scheme).

    Returns:
        str: 確認結果
    """
    user = await get_current_user(db, token, is_email=True)
    return f"""
    <html>
        <head></head>
        <body>
            <h1>メール認証が完了しました</h1>
            <p>ユーザー名: {user.username}</p>
            <p>メールアドレス: {user.email}</p>
        </body>
    </html>
    """
