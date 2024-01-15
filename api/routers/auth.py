from datetime import timedelta
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from pydantic import ValidationError
from sqlalchemy.orm.session import Session

import api.cruds.user as user_crud
from api import config, schemas
from api.dependencies import get_config, get_current_user, get_db
from api.utils import send_email

router = APIRouter(prefix="/auth", tags=["認証"])
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TIME_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
TIME_DELTA2 = timedelta(days=30)
HTML_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=HTML_DIR)


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
    if user.is_active and settings.IS_PRODUCT and user.user_type != "a":
        raise HTTPException(status_code=400, detail="User already active")
    token = user_crud.create_access_token(
        secret_key=settings.SECRET_KEY,
        data={"sub": user.username},
        expires_delta=timedelta(minutes=15),
    )
    html_file = HTML_DIR / "MAIL-verify-email.html"
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
    request: Request,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    token: str,
    db: Session = Depends(get_db),
) -> str:
    """
    このエンドポイントにアクセスすると、メール認証が完了する。
    ただし、トークンが有効でない場合は、エラーが返される。
    """
    try:
        user = get_current_user(settings=settings, db=db, token=token)
        user.is_active = True
        db.commit()
        db.refresh(user)
        return templates.TemplateResponse(
            "result.html",
            context={
                "request": request,
                "message": "メール認証が完了しました。アプリに戻りログインしてください。",
                "user": user,
                "title": "メール認証完了",
            },
        )
    except HTTPException:
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "error_code": 400,
                "error_message": "URLが不正です。再度、パスワードリセットのメールを送信してください。",
            },
        )


@router.post("/forgot-password", summary="パスワードリセットのメール送信")
def forgot_password(
    request: Request,
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
    html_file = Path(__file__).parent.parent / "templates" / "MAIL-reset-password.html"
    html = Template(html_file.read_text())
    background_tasks.add_task(
        send_email,
        from_=settings.MAIL_SENDER,
        to=email_body.email,
        subject="Reset your password",
        body=html.render(
            username=user.username,
            url=request.url_for("reset_password_form", token=token),
        ),
    )
    return "Email sent"


@router.get(
    "/reset-password/{token}", response_class=HTMLResponse, summary="パスワードリセットのフォーム"
)
def reset_password_form(
    request: Request,
    token: str,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    db: Session = Depends(get_db),
) -> str:
    """
    ここにアクセスして、新しいパスワードを入力すると、パスワードがリセットされる。
    ただし、トークンが有効でない場合は、エラーが返される。
    """
    try:
        get_current_user(settings=settings, db=db, token=token)
    except HTTPException:
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "error_code": 400,
                "error_message": "URLが不正です。再度、パスワードリセットのメールを送信してください。",
            },
        )
    return templates.TemplateResponse(
        "reset-password-form.html",
        context={"request": request},
    )


@router.post("/reset-password/{token}", summary="パスワードリセット")
def reset_password(
    request: Request,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    token: str,
    new_password: str = Form(),
    db: Session = Depends(get_db),
) -> None:
    """
    フォームから新しいパスワードを受け取り、パスワードをリセットする。
    ただし、トークンが有効でない場合は、エラーが返される。"""
    try:
        user = get_current_user(db, token, settings=settings)
        schema_user = schemas.UserPasswordChange(password=new_password)
        user_crud.update_user_password(db, user, schema_user)
    except ValidationError:
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "error_code": 400,
                "error_message": f"""パスワードが不正です。パスワードは8文字以上である必要があります。<br/>
                <a href="{token}">パスワードリセット</a>
                """,
            },
        )
    except HTTPException:
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "error_code": 400,
                "error_message": "URLが不正です。再度、パスワードリセットのメールを送信してください。",
            },
        )
    return templates.TemplateResponse(
        "result.html",
        context={
            "request": request,
            "message": "パスワードをリセットしました。",
            "user": user,
            "title": "パスワードリセット完了",
        },
    )
