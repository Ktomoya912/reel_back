import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession

import api.cruds.user as user_crud
import api.routers.auth as auth_router
import api.schemas.user as user_schema
from api.db import get_db
from api.modules.email import send_email

router = APIRouter()


@router.post("/users", response_model=user_schema.UserCreateResponse)
async def create_user(
    user_body: user_schema.UserCreate,
    db: AsyncSession = Depends(get_db),
    mail_auth: bool = True,
):
    user = await user_crud.create_user(db, user_body)
    if mail_auth:
        await auth_router.send_verification_email(user.email, db)
    return user


@router.post("/users/company", response_model=user_schema.UserCreateResponse)
async def create_user_company(
    user_body: user_schema.UserCreateCompany,
    db: AsyncSession = Depends(get_db),
    mail_auth: bool = True,
):
    user = await user_crud.create_user_company(db, user_body)
    if mail_auth:
        await auth_router.send_verification_email(user.email, db)
    return user


@router.get("/users", response_model=list[user_schema.User])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await user_crud.get_users(db)


@router.get("/users/me", response_model=user_schema.User)
async def get_user_me(
    current_user: user_schema.User = Depends(auth_router.get_current_user),
):
    return current_user


@router.get("/users/{user_id}", response_model=user_schema.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_crud.get_user(db, user_id)


@router.put("/users/{user_id}", response_model=user_schema.UserCreateResponse)
async def update_user(
    user_id: int, user_body: user_schema.UserCreate, db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_crud.update_user(db, user_body, original=user)


@router.delete("/users/{user_id}", response_model=None)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_crud.delete_user(db, user)


@router.post("/users/send-mail-to-admin", response_model=None)
async def send_mail_to_admin(mail_body: user_schema.MailBody):
    """お問い合わせを管理者にメール送信"""
    html_file = Path(__file__).parent.parent / "templates" / "mail-to-admin.html"
    html = Template(html_file.read_text())
    to_list = [os.getenv("MAIL_SENDER"), mail_body.email]
    send_email(
        os.getenv("MAIL_SENDER"),
        to_list,
        f"お問い合わせ: {mail_body.subject}",
        html.render(
            email=mail_body.email,
            body=mail_body.body,
        ),
    )
    return {"message": "success"}
