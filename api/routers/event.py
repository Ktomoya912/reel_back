from typing import Annotated, Optional, Literal

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
    type: Literal["all", "active", "inactive", "draft"] = "all",
):
    """
    イベントの一覧を取得する。
    パラメータとして、limit, offset, sort, order, keywordを受け取る。
    それぞれ、「取得する件数」「取得する開始位置」「ソートする項目」「ソート順」「検索キーワード」を表す。
    ただし、現状「order」は機能していないので無視してよい。

    続いて、tagを受け取る。
    これは、イベントのタグを指定する。
    もし、タグを指定している場合は、そのタグに紐づくイベントのみを取得する。

    最後に、only_activeを受け取る。
    これは、イベントのステータスが「公開中」のもののみを取得するかどうかを指定する。
    何も指定しない状態ならば、すべてのイベントを取得する。
    """
    if tag:
        data = event_crud.get_event_by_tag(
            common["db"],
            tag,
        )
    else:
        data = event_crud.get_events(type=type, **common)
    return data[common["offset"] : common["offset"] + common["limit"]]  # noqa E203


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
        raise HTTPException(status_code=404, detail="Not found")
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
        raise HTTPException(status_code=404, detail="Not found")
    elif event.user_id != current_user.id and current_user.user_type != "a":
        raise HTTPException(status_code=403, detail="You don't have permission")
    event_crud.delete_event(db, event_id)
    return {"message": "Event Deleted"}


@router.put(
    "/{event_id}/activate", response_model=schemas.EventListView, summary="イベント公開"
)
def activate_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    イベントを公開する。
    公開できるのは、管理者のみである。
    """
    event = event_crud.get_event(db, event_id)
    event.status = "1"
    db.commit()
    db.refresh(event)
    return event


@router.put(
    "/{event_id}/deactivate", response_model=schemas.EventListView, summary="イベント非公開"
)
def deactivate_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    イベントを非公開にする。
    公開できるのは、管理者のみである。
    """
    event = event_crud.get_event(db, event_id)
    event.status = "inactive"
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


@router.post("/{event_id}/bookmark", summary="イベントお気に入り登録")
def bookmark_event(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    イベントをお気に入り登録する。
    失敗した場合は、Falseを返す。
    """
    return event_crud.bookmark_event(db, event_id, current_user.id)


@router.delete("/{event_id}/bookmark", summary="イベントお気に入り登録解除")
def unbookmark_event(
    event_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    イベントをお気に入り登録から削除する。
    失敗した場合は、Falseを返す。
    """
    return event_crud.unbookmark_event(db, event_id, current_user.id)


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
        raise HTTPException(status_code=404, detail="Not found")
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
        raise HTTPException(status_code=404, detail="Not found")
    return event_crud.delete_review(db, event_id, user_id)
