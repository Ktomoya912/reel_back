from datetime import timedelta
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from jinja2 import Template
from sqlalchemy.orm.session import Session

import api.cruds.user as user_crud
from api import config, schemas
from api.dependencies import get_config, get_current_user, get_db
from api.utils import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TIME_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
TIME_DELTA2 = timedelta(days=30)


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """ログインを行い、アクセストークンを返す"""
    user = user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # if not user.is_active and settings.IS_PRODUCT:
    #     # メールでの認証が完了していない場合
    #     raise HTTPException(status_code=410, detail="Inactive user")
    access_token_expires = TIME_DELTA2
    access_token = user_crud.create_access_token(
        secret_key=settings.SECRET_KEY,
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/send-verification-email")
def send_verification_email(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str,
    settings: config.BaseConfig = Depends(get_config),
    db: Session = Depends(get_db),
) -> None:
    """メール認証のメール送信"""
    user = user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active and settings.IS_PRODUCT:
        raise HTTPException(status_code=400, detail="User already active")
    token = user_crud.create_access_token(
        secret_key=settings.SECRET_KEY,
        data={"sub": user.username},
        expires_delta=timedelta(minutes=15),
    )
    html_file = Path(__file__).parent.parent / "templates" / "verify-email.html"
    html = Template(html_file.read_text())
    background_tasks.add_task(
        send_email,
        from_=settings.MAIL_SENDER,
        to=email,
        subject="Verify your email",
        body=html.render(
            username=user.username,
            url=request.url_for("email_confirmation", token=token),
        ),
    )
    return "Email sent"


@router.get("/email-confirmation/{token}", response_class=HTMLResponse)
def email_confirmation(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    token: str,
    db: Session = Depends(get_db),
) -> str:
    """メール認証の完了"""
    user = get_current_user(settings=settings, db=db, token=token)
    user.is_active = True
    db.commit()
    db.refresh(user)
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


@router.post("/forgot-password")
def forgot_password(
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    email: str,
    db: Session = Depends(get_db),
) -> None:
    """パスワードリセットのメール送信"""
    user = user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = user_crud.create_access_token(
        secret_key=settings.SECRET_KEY,
        data={"sub": user.username},
        expires_delta=timedelta(minutes=15),
    )
    html_file = Path(__file__).parent.parent / "templates" / "reset-password.html"
    html = Template(html_file.read_text())
    background_tasks.add_task(
        send_email,
        from_=settings.MAIL_SENDER,
        to=email,
        subject="Reset your password",
        body=html.render(
            username=user.username,
            url=f"http://localhost:8000/auth/reset-password/{token}",
        ),
    )
    return "Email sent"


@router.get("/reset-password/{token}", response_class=HTMLResponse)
def reset_password_form(token: str) -> str:
    """パスワードリセットのフォーム"""
    return """
    <html>
        <head></head>
        <body>
            <form method="post">
                <label for="new_password">New password</label>
                <input type="password" id="new_password" name="new_password" required>
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """


@router.post("/reset-password/{token}")
def reset_password(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    token: str,
    new_password: str = Form(),
    db: Session = Depends(get_db),
) -> None:
    """パスワードリセット"""
    user = get_current_user(db, token, settings=settings)
    schema_user = schemas.UserPasswordChange(password=new_password)
    user_crud.update_user_password(db, user, schema_user)
    return "Password updated successfully"
