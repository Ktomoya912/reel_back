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

router = APIRouter(prefix="/auth", tags=["認証"])
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TIME_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
TIME_DELTA2 = timedelta(days=30)


@router.post("/token", response_model=schemas.Token, summary="ログインを行い、アクセストークンを返す")
def login_for_access_token(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """
    フォームからユーザー名とパスワードを受け取り、アクセストークンを返す
    """
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


@router.post("/send-verification-email", summary="認証用のメール送信")
def send_verification_email(
    request: Request,
    background_tasks: BackgroundTasks,
    email_body: schemas.MailBase,
    settings: config.BaseConfig = Depends(get_config),
    db: Session = Depends(get_db),
) -> None:
    """
    データとしてメールアドレスを受け取り、データベースに登録されているメールアドレスであれば、認証用のメールを送信する。
    """
    user = user_crud.get_user_by_email(db, email_body.email)
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
    if settings.MAIL_PASSWORD is None:
        raise HTTPException(
            status_code=500,
            detail="MAIL_PASSWORD is not set. Please set MAIL_PASSWORD in .env file.",
        )
    background_tasks.add_task(
        send_email,
        from_=settings.MAIL_SENDER,
        to=email_body.email,
        subject="Verify your email",
        body=html.render(
            username=user.username,
            url=request.url_for("email_confirmation", token=token),
        ),
    )
    return {"detail": "Email sent"}


@router.get("/email-confirmation/{token}", response_class=HTMLResponse, summary="メール認証")
def email_confirmation(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    token: str,
    db: Session = Depends(get_db),
) -> str:
    """
    このエンドポイントにアクセスすると、メール認証が完了する。
    ただし、トークンが有効でない場合は、エラーが返される。
    """
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


@router.post("/forgot-password", summary="パスワードリセットのメール送信")
def forgot_password(
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    email_body: schemas.MailBase,
    db: Session = Depends(get_db),
) -> None:
    """ """
    user = user_crud.get_user_by_email(db, email_body.email)
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
        to=email_body.email,
        subject="Reset your password",
        body=html.render(
            username=user.username,
            url=f"http://localhost:8000/auth/reset-password/{token}",
        ),
    )
    return "Email sent"


@router.get(
    "/reset-password/{token}", response_class=HTMLResponse, summary="パスワードリセットのフォーム"
)
def reset_password_form(
    token: str,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    db: Session = Depends(get_db),
) -> str:
    """
    ここにアクセスして、新しいパスワードを入力すると、パスワードがリセットされる。
    ただし、トークンが有効でない場合は、エラーが返される。
    """
    get_current_user(settings=settings, db=db, token=token)
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


@router.post("/reset-password/{token}", summary="パスワードリセット")
def reset_password(
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    token: str,
    new_password: str = Form(),
    db: Session = Depends(get_db),
) -> None:
    """
    フォームから新しいパスワードを受け取り、パスワードをリセットする。
    ただし、トークンが有効でない場合は、エラーが返される。"""
    user = get_current_user(db, token, settings=settings)
    schema_user = schemas.UserPasswordChange(password=new_password)
    user_crud.update_user_password(db, user, schema_user)
    return "Password updated successfully"
