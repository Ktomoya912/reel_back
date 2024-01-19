from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session

import api.cruds.event as event_crud
import api.cruds.plan as plan_crud
import api.cruds.tag as tag_crud
from api import models, schemas
from api.dependencies import (
    common_parameters,
    get_admin_user,
    get_company_user,
    get_current_active_user,
    get_db,
)

router = APIRouter(prefix="/events", tags=["イベント"])


@router.post("/", response_model=schemas.EventCreateResponse, summary="イベント作成")
def create_event(
    current_user: Annotated[dict, Depends(get_company_user)],
    event_create: schemas.EventCreate,
    db: Session = Depends(get_db),
):
    """
    必要データを受け取り、イベントを作成する。
    レスポンスとして、作成されたイベントの情報を返す。
    """
    event = event_crud.create_event(db, event_create, current_user.id)
    event = event_crud.create_event_times(db, event, event_create.event_times)
    event = tag_crud.create_event_tags(db, event, event_create.tags)
    return event


@router.get("/", response_model=list[schemas.EventListView], summary="イベント一覧取得")
def get_events(
    common: Annotated[dict, Depends(common_parameters)],
    tag: str = "",
):
    """
    ## イベントの一覧を取得する。

        - limit: 取得するイベントの最大数を指定する。デフォルトは100。
        - offset: 取得するイベントの開始位置を指定する。デフォルトは0。
        - sort: ソートする項目を指定する。デフォルトはid。
        - order: ソート順を指定する。デフォルトはasc。(現状機能していない)
        - keyword: キーワードを指定する。指定した場合は、タイトルとタグのどちらかにキーワードが含まれるイベントを取得する。
        - status: ステータスを指定する。デフォルトはall。
        - user_id: ユーザーIDを指定する。
        - target: 絞り込み内容を指定する。user_idを指定しないと無視される。


    ## status:

        - all: 全てのイベントを取得する。
        - active: ステータスが「公開中」のイベントを取得する。
        - inactive: ステータスが「非公開」のイベントを取得する。
        - draft: ステータスが「下書き」のイベントを取得する。
        - posted: ステータスが「公開中」かつ、公開日が過去のイベントを取得する。


    ## target:

        - favorite: お気に入り登録しているイベントを取得する。
        - favorite: お気に入り登録しているイベントを取得する。
        - posted: 自分が作成したイベントを取得する。
    """
    return event_crud.get_events(**common, tag_name=tag)


@router.get(
    "/recent/", response_model=list[schemas.EventListView], summary="近日開催のイベント一覧取得"
)
def get_recent_events(db: Session = Depends(get_db)):
    """
    開催3日前で、ステータスが「公開中」のイベントを取得する。
    """
    return event_crud.get_recent_events(db)


@router.get("/{event_id}", response_model=schemas.Event, summary="イベント詳細取得")
def get_event(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    イベントの詳細情報を取得する。
    このエンドポイントにアクセスできるユーザーは、メールアドレスの認証が完了しているユーザーのみである。
    追加のデータで、お気に入り登録しているかどうかを返す。
    """
    event = event_crud.watch_event(db, event_id, current_user.id)
    setattr(event, "is_favorite", event in current_user.event_bookmarks)
    return event


@router.put("/{event_id}", response_model=schemas.EventCreateResponse, summary="イベント更新")
def update_event(
    event_id: int,
    event_update: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """
    イベントの情報を更新する。
    更新できるのは、イベントを作成したユーザーか、管理者のみである。
    """
    event = event_crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event Not found")
    elif event.user_id != current_user.id and current_user.user_type != "a":
        raise HTTPException(status_code=403, detail="You don't have permission")
    return event_crud.update_event(db, event_id, event_update)


@router.delete("/{event_id}", summary="イベント削除")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """
    イベントを削除する。
    削除できるのは、イベントを作成したユーザーか、管理者のみである。
    """
    event = event_crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event Not found")
    elif event.user_id != current_user.id and current_user.user_type != "a":
        raise HTTPException(status_code=403, detail="You don't have permission")
    event_crud.delete_event(db, event_id)
    return {"message": "Event Deleted"}


@router.put(
    "/{event_id}/change-status",
    response_model=schemas.EventListView,
    summary="イベントステータス変更",
)
def change_event_status(
    event_id: int,
    status: Literal["active", "inactive", "draft"],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    イベントのステータスを変更する。
    このエンドポイントは管理者のみがアクセスできる。
    """
    event = event_crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.status = status
    db.commit()
    db.refresh(event)
    return event


@router.post(
    "/purchase-event", response_model=schemas.EventCreateResponse, summary="イベント広告購入"
)
def purchase_event(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    purchase_data: schemas.EventArticleCreate,
    db: Session = Depends(get_db),
):
    """
    イベント広告を購入する。
    プランの購入とイベントの作成を同時に行う。
    """
    purchase = plan_crud.purchase_plan(db, purchase_data.purchase, current_user)
    event = create_event(current_user, purchase_data.event, db)
    event.purchase = purchase
    db.commit()
    db.refresh(event)
    return event


@router.put("/{event_id}/bookmark", summary="イベントお気に入り登録切り替え")
def bookmark_event(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    イベントをお気に入り登録切り替えを行う。
    すでにお気に入り登録している場合は、お気に入り登録を解除する。
    """
    event = event_crud.get_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event Not Found")
    return event_crud.toggle_bookmark_event(db, event_id, current_user.id)


@router.post("/{event_id}/review", response_model=schemas.EventReview, summary="レビュー投稿")
def post_review(
    event_id: int,
    review_create: schemas.EventReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    イベントにレビューを投稿する。
    """
    event = event_crud.get_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event Not Found")
    review = event_crud.get_review(db, event_id, current_user.id)
    if review:
        raise HTTPException(status_code=400, detail="Already posted")
    return event_crud.create_review(db, event_id, current_user.id, review_create)


@router.put("/{event_id}/review", response_model=schemas.EventReview, summary="レビュー更新")
def update_review(
    event_id: int,
    review_update: schemas.EventReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    イベントのレビューを更新する。
    オプションとしてuser_idを受け取ることができるが、これは管理者のみが指定できる。
    user_idを指定しない場合は、ログインしているユーザーのレビューを更新する。
    """
    if user_id is None or current_user.user_type != "a":
        user_id = current_user.id
    review = event_crud.get_review(db, event_id, user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review Not found")
    return event_crud.update_review(db, event_id, user_id, review_update)


@router.delete("/{event_id}/review", summary="レビュー削除")
def delete_review(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    イベントのレビューを削除する。
    オプションとしてuser_idを受け取ることができるが、これは管理者のみが指定できる。
    user_idを指定しない場合は、ログインしているユーザーのレビューを削除する。
    """
    if user_id is None or current_user.user_type != "a":
        user_id = current_user.id
    review = event_crud.get_review(db, event_id, user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review Not found")
    return event_crud.delete_review(db, event_id, user_id)


@router.get(
    "/{event_id}/impressions",
    summary="イベント広告のインプレッション取得",
    tags=["広告インプレッション"],
)
def get_event_impressions(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """
    イベント広告のインプレッションを取得する。
    """
    return event_crud.get_event_impressions(db, event_id)
