from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session

import api.cruds.job as job_crud
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

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=schemas.JobCreateResponse, summary="求人作成")
def create_job(
    current_user: Annotated[dict, Depends(get_company_user)],
    job_create: schemas.JobCreate,
    db: Session = Depends(get_db),
):
    """
    必要データを受け取り、求人を作成する。
    レスポンスとして、作成された求人の情報を返す。
    """
    job = job_crud.create_job(db, job_create, current_user.id)
    job = job_crud.create_job_times(db, job, job_create.job_times)
    job = tag_crud.create_job_tags(db, job, job_create.tags)
    return job


@router.get("/", response_model=list[schemas.JobListView], summary="求人一覧取得")
def get_jobs(
    common: Annotated[dict, Depends(common_parameters)],
    tag: str = "",
    only_active: bool = False,
):
    """
    求人の一覧を取得する。
    パラメータとして、limit, offset, sort, order, keywordを受け取る。
    それぞれ、「取得する件数」「取得する開始位置」「ソートする項目」「ソート順」「検索キーワード」を表す。
    ただし、現状「order」は機能していないので無視してよい。

    続いて、tagを受け取る。
    これは、求人のタグを指定する。
    もし、タグを指定している場合は、そのタグに紐づく求人のみを取得する。

    最後に、only_activeを受け取る。
    これは、求人のステータスが「公開中」のもののみを取得するかどうかを指定する。
    何も指定しない状態ならば、すべての求人を取得する。
    """
    if tag:
        data = job_crud.get_job_by_tag(
            common["db"],
            tag,
        )
    else:
        data = job_crud.get_jobs(only_active=only_active, **common)
    return data[common["offset"] : common["offset"] + common["limit"]]  # noqa E203


@router.get("/recent/", response_model=list[schemas.JobListView], summary="最近の求人取得")
def get_recent_jobs(db: Session = Depends(get_db)):
    """
    仕事が行われる3日前で、ステータスが「公開中」の求人を取得する。
    """
    return job_crud.get_recent_jobs(db)


@router.get("/{job_id}", response_model=schemas.Job, summary="求人詳細取得")
def get_job(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    求人の詳細情報を取得する。
    このエンドポイントにアクセスできるユーザーは、メールアドレスの認証が完了しているユーザーのみである。
    追加のデータで、お気に入り登録しているかどうかを返す。"""
    job = job_crud.watch_job(db, job_id, current_user.id)
    setattr(job, "is_favorite", job in current_user.job_bookmarks)
    return job


@router.put("/{job_id}", response_model=schemas.JobCreateResponse, summary="求人更新")
def update_job(
    job_id: int,
    job_update: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """
    求人を更新する。
    更新できるのは、求人を作成したユーザーか、管理者のみである。"""
    job = job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    elif job.user_id != current_user.id and current_user.user_type != "a":
        raise HTTPException(status_code=403, detail="You don't have permission")
    return job_crud.update_job(db, job_id, job_update)


@router.delete("/{job_id}", summary="求人削除")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """
    求人を削除する。
    削除できるのは、求人を作成したユーザーか、管理者のみである。"""
    job = job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    elif job.user_id != current_user.id and current_user.user_type != "a":
        raise HTTPException(status_code=403, detail="You don't have permission")
    job_crud.delete_job(db, job_id)
    return {"message": "Job deleted"}


@router.put("/{job_id}/activate", response_model=schemas.JobListView, summary="求人公開")
def activate_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    求人を公開する。
    このエンドポイントは管理者のみがアクセスできる。
    """
    job = job_crud.get_job(db, job_id)
    job.status = "1"
    db.commit()
    db.refresh(job)
    return job


@router.post(
    "/purchase-job", response_model=schemas.JobCreateResponse, summary="求人広告購入"
)
def purchase_job(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    purchase_data: schemas.JobArticleCreate,
    db: Session = Depends(get_db),
):
    """
    求人広告を購入する。
    プランの購入と求人の作成を同時に行う。"""
    purchase = plan_crud.purchase_plan(db, purchase_data.purchase, current_user)
    job = create_job(current_user, purchase_data.job, db)
    job.purchase = purchase
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/bookmark", summary="求人お気に入り登録")
def bookmark_job(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    求人をお気に入り登録する。
    失敗した場合は、Falseを返す。"""
    return job_crud.bookmark_job(db, job_id, current_user.id)


@router.delete("/{job_id}/bookmark", summary="求人お気に入り削除")
def unbookmark_job(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    求人のお気に入りを削除する。
    失敗した場合は、Falseを返す。
    """
    return job_crud.unbookmark_job(db, job_id, current_user.id)


@router.post("/{job_id}/review", response_model=schemas.JobReview, summary="レビュー作成")
def post_review(
    job_id: int,
    review: schemas.JobReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    求人にレビューを投稿する。
    """
    return job_crud.create_review(db, job_id, current_user.id, review)


@router.put("/{job_id}/review", response_model=schemas.JobReview, summary="レビュー更新")
def update_review(
    job_id: int,
    review_update: schemas.JobReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    求人のレビューを更新する。
    オプションとしてuser_idを受け取ることができるが、これは管理者のみが指定できる。
    user_idを指定しない場合は、ログインしているユーザーのレビューを更新する。
    """
    if user_id is None or current_user.user_type != "a":
        user_id = current_user.id
    review = job_crud.get_review(db, job_id, user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return job_crud.update_review(db, job_id, current_user.id, review_update)


@router.delete("/{job_id}/review", summary="レビュー削除")
def delete_review(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    求人のレビューを削除する。
    オプションとしてuser_idを受け取ることができるが、これは管理者のみが指定できる。
    user_idを指定しない場合は、ログインしているユーザーのレビューを削除する。
    """
    if user_id is None or current_user.user_type != "a":
        user_id = current_user.id
    review = job_crud.get_review(db, job_id, user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return job_crud.delete_review(db, job_id, user_id)
