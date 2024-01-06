from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from jinja2 import Template
from sqlalchemy.orm.session import Session

import api.cruds.user as user_crud
import api.routers.auth as auth_router
from api import config, schemas
from api.utils import send_email

from ..dependencies import get_config, get_current_user, get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserCreateResponse)
def create_user(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    user_body: schemas.UserCreate,
    db: Session = Depends(get_db),
):
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


@router.post("/company", response_model=schemas.UserCreateResponse)
def create_user_company(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    user_body: schemas.UserCreateCompany,
    db: Session = Depends(get_db),
):
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


@router.get("", response_model=list[schemas.User])
def get_users(db: Session = Depends(get_db)):
    return user_crud.get_users(db)


@router.get("/me", response_model=schemas.User)
def get_user_me(
    current_user: schemas.User = Depends(get_current_user),
):
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_crud.get_user(db, user_id)


@router.put("/{user_id}", response_model=schemas.UserCreateResponse)
def update_user(
    user_id: int, user_body: schemas.UserCreate, db: Session = Depends(get_db)
):
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update_user(db, user_body, original=user)


@router.delete("/{user_id}", response_model=None)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.delete_user(db, user)


@router.post("/send-mail-to-admin", response_model=None)
def send_mail_to_admin(
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    mail_body: schemas.MailBody,
):
    """お問い合わせを管理者にメール送信"""
    html_file = Path(__file__).parent.parent / "templates" / "mail-to-admin.html"
    html = Template(html_file.read_text())
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
