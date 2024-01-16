from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from jinja2 import Template
from sqlalchemy.orm.session import Session

import api.cruds.user as user_crud
import api.routers.auth as auth_router
from api import config, models, schemas
from api.utils import send_email

from ..dependencies import get_config, get_current_active_user, get_current_user, get_db

router = APIRouter(prefix="/users", tags=["ユーザー"])


@router.post("/", response_model=schemas.UserCreateResponse, summary="ユーザー作成")
def create_user(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Annotated[config.BaseConfig, Depends(get_config)],
    user_body: schemas.UserCreate,
    send_verification_email: bool = Query(True, description="認証メールを送信するか"),
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
    if settings.IS_PRODUCT and send_verification_email:
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
    send_verification_email: bool = Query(True, description="認証メールを送信するか"),
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
    if settings.IS_PRODUCT and send_verification_email:
        auth_router.send_verification_email(
            request, background_tasks, settings=settings, email=user.email, db=db
        )
    return user


@router.get("/", response_model=list[schemas.User], summary="ユーザー一覧")
def get_users(db: Session = Depends(get_db)):
    """
    ユーザー一覧を取得する。"""
    return user_crud.get_users(db)


@router.get(
    "/event-bookmarks",
    response_model=list[schemas.EventListView],
    summary="お気に入りイベント一覧取得",
)
def get_bookmark_events(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    お気に入り登録しているイベントの一覧を取得する。
    """
    return current_user.event_bookmarks


@router.get(
    "/event-watched", response_model=list[schemas.EventListView], summary="イベントの閲覧履歴"
)
def get_event_watched(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    イベントの閲覧履歴を取得する。
    """
    return [link.event for link in current_user.event_watched_link]


@router.get(
    "/event-postings", response_model=list[schemas.EventListView], summary="イベントの投稿履歴"
)
def get_event_postings(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    type: Literal["all", "active", "inactive", "draft", "posted"] = "all",
):
    """
    イベントの投稿履歴を取得する。
    """
    if type == "all":
        return current_user.event_postings
    elif type == "posted":
        return [
            event for event in current_user.event_postings if event.status != "draft"
        ]
    else:
        return [event for event in current_user.event_postings if event.status == type]


@router.get(
    "/job-bookmarks", response_model=list[schemas.JobListView], summary="お気に入り求人取得"
)
def get_bookmark_jobs(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    お気に入り登録している求人の一覧を取得する。
    """
    return current_user.job_bookmarks


@router.get("/job-watched", response_model=list[schemas.JobListView], summary="求人の閲覧履歴")
def get_job_watched(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    求人の閲覧履歴を取得する。
    """
    return [link.job for link in current_user.job_watched_link]


@router.get(
    "/job-postings", response_model=list[schemas.JobListView], summary="求人の投稿履歴"
)
def get_job_postings(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    type: Literal["all", "active", "inactive", "draft", "posted"] = "all",
):
    """
    求人の投稿履歴を取得する。
    """
    if type == "all":
        return current_user.job_postings
    elif type == "posted":
        return [job for job in current_user.job_postings if job.status != "draft"]
    else:
        return [job for job in current_user.job_postings if job.status == type]


@router.get(
    "/job-applications", response_model=list[schemas.JobApplication], summary="応募一覧取得"
)
def get_job_applications(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    応募一覧を取得する。
    """
    return current_user.applications


@router.get("/me", response_model=schemas.User, summary="自分自身のユーザー情報")
def get_user_me(
    current_user: schemas.User = Depends(get_current_user),
):
    """自分自身のユーザー情報を取得する。"""
    return current_user


@router.get("/{user_id}", response_model=schemas.User, summary="ユーザー情報")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザーIDを指定して、ユーザー情報を取得する。"""
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user


@router.put("/{user_id}/activate", response_model=schemas.User, summary="ユーザー有効化")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """ユーザーIDを指定して、ユーザーを有効化する。
    デバッグ用。のちに削除されるので、本番環境では使用しないこと。"""
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=schemas.UserCreateResponse, summary="ユーザー情報更新")
def update_user(
    user_id: int,
    user_body: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
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
    current_user: models.User = Depends(get_current_active_user),
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
    html_file = Path(__file__).parent.parent / "templates" / "MAIL-to-admin.html"
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
