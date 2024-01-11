from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from jinja2 import Template
from sqlalchemy.orm.session import Session

import api.cruds.user as user_crud
import api.routers.auth as auth_router
from api import config, models, schemas
from api.utils import send_email

from ..dependencies import get_config, get_current_user, get_db, get_general_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserCreateResponse, summary="ユーザー作成")
def create_user(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    user_body: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """必要データを受け取り、ユーザーを作成する。
    レスポンスとして、作成されたユーザーの情報を返す。
    """
    if user_crud.get_user_by_email(db, user_body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_crud.get_user_by_username(db, user_body.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = user_crud.create_user(db, user_body)
    if settings.IS_PRODUCT:
        auth_router.send_verification_email(
            request, background_tasks, settings=settings, email=user.email, db=db
        )
    return user


@router.post("/company", response_model=schemas.UserCreateResponse, summary="企業ユーザー作成")
def create_user_company(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    user_body: schemas.UserCreateCompany,
    db: Session = Depends(get_db),
):
    """必要データを受け取り、企業ユーザーを作成する。
    レスポンスとして、作成された企業ユーザーの情報を返す。
    """
    if user_crud.get_user_by_email(db, user_body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_crud.get_user_by_username(db, user_body.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = user_crud.create_user_company(db, user_body)
    if settings.IS_PRODUCT:
        auth_router.send_verification_email(
            request, background_tasks, settings=settings, email=user.email, db=db
        )
    return user


@router.get("/", response_model=list[schemas.User], summary="ユーザー一覧")
def get_users(db: Session = Depends(get_db)):
    """
    ユーザー一覧を取得する。"""
    return user_crud.get_users(db)


@router.get("/me", response_model=schemas.User, summary="自分自身のユーザー情報")
def get_user_me(
    current_user: schemas.User = Depends(get_current_user),
):
    """自分自身のユーザー情報を取得する。"""
    return current_user


@router.get("/{user_id}", response_model=schemas.User, summary="ユーザー情報")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザーIDを指定して、ユーザー情報を取得する。"""
    return user_crud.get_user(db, user_id)


@router.put("/{user_id}", response_model=schemas.UserCreateResponse, summary="ユーザー情報更新")
def update_user(
    user_id: int,
    user_body: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_general_user),
):
    """ユーザーIDを指定して、ユーザー情報を更新する。
    自分自身のユーザー情報を更新する場合は、認証が必要。
    管理者ユーザーは他のユーザーの情報を更新できる。"""
    if current_user.id != user_id and current_user.user_type != "a":
        raise HTTPException(
            status_code=403, detail="You don't have permission to access"
        )
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update_user(db, user_body, original=user)


@router.delete("/{user_id}", response_model=None, summary="ユーザー削除")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_general_user),
):
    """ユーザーIDを指定して、ユーザーを削除する。
    自分自身のユーザーを削除する場合は、認証が必要。
    管理者ユーザーは他のユーザーを削除できる。"""
    if current_user.id != user_id and current_user.user_type != "a":
        raise HTTPException(
            status_code=403, detail="You don't have permission to access"
        )
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.delete_user(db, user)


@router.post("/send-mail-to-admin", response_model=None, summary="お問い合わせ")
def send_mail_to_admin(
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    mail_body: schemas.MailBody,
):
    """お問い合わせを管理者にメール送信"""
    html_file = Path(__file__).parent.parent / "templates" / "mail-to-admin.html"
    html = Template(html_file.read_text())
    if settings.MAIL_PASSWORD is None:
        raise HTTPException(
            status_code=500,
            detail="MAIL_PASSWORD is not set. Please set MAIL_PASSWORD in .env file.",
        )
    to_list = [settings.MAIL_SENDER, mail_body.email]
    background_tasks.add_task(
        send_email,
        settings.MAIL_SENDER,
        to_list,
        f"お問い合わせ: {mail_body.subject}",
        html.render(
            email=mail_body.email,
            body=mail_body.body,
        ),
    )
    return {"message": "success"}
