from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session

import api.cruds.job as job_crud
import api.cruds.message as message_crud
import api.cruds.plan as plan_crud
import api.cruds.tag as tag_crud
from api import models, schemas
from api.dependencies import (
    common_parameters,
    get_admin_user,
    get_company_user,
    get_current_active_user,
    get_db,
    get_general_user,
)

router = APIRouter(prefix="/jobs", tags=["求人"])


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
    type: Literal["all", "active", "inactive", "draft"] = "all",
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
    return job_crud.get_jobs(type=type, **common, tag=tag)


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
    job.status = "active"
    db.commit()
    db.refresh(job)
    return job


@router.put("/{job_id}/deactivate", response_model=schemas.JobListView, summary="求人非公開")
def deactivate_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    求人を非公開にする。
    このエンドポイントは管理者のみがアクセスできる。
    """
    job = job_crud.get_job(db, job_id)
    job.status = "inactive"
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


@router.post("/{job_id}/apply", response_model=schemas.JobApplication, summary="応募")
def apply_job(
    job_id: int,
    current_user: models.User = Depends(get_general_user),
    db: Session = Depends(get_db),
):
    """
    求人に応募する。
    """
    job = job_crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job Not Found")
    response_data = job_crud.apply_job(db, job_id, current_user)
    message = message_crud.create_message(
        db,
        schemas.MessageCreate(
            title="応募がありました",
            message=f"{current_user.username}さんが応募しました。",
            type="J",
            user_list=[response_data.job.author.id],
        ),
    )
    message_crud.send_message(db, [response_data.job.author.id], message.id)
    return response_data


@router.get(
    "/{job_id}/application",
    response_model=schemas.JobApplicationUsers,
    summary="応募一覧取得",
)
def get_applications(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    求人に応募したユーザーの一覧を取得する。
    """
    return {
        "job_id": job_id,
        "users": job_crud.get_applications(db, job_id),
    }


@router.put(
    "/{job_id}/application/approve",
    response_model=schemas.JobApplication,
    summary="応募承認",
)
def approve_application(
    job_id: int,
    user_id: int,
    current_user: models.User = Depends(get_company_user),
    db: Session = Depends(get_db),
):
    """
    求人に応募したユーザーの応募を承認する。
    """
    response_data = job_crud.approve_application(db, job_id, user_id)
    message = message_crud.create_message(
        db,
        schemas.MessageCreate(
            title="応募が承認されました",
            message=f"{response_data.job.author.username}さんが応募を承認しました。",
            type="J",
            user_list=[user_id],
        ),
    )
    message_crud.send_message(db, [user_id], message.id)
    return response_data


@router.put(
    "/{job_id}/application/reject",
    response_model=schemas.JobApplication,
    summary="応募拒否",
)
def reject_application(
    job_id: int,
    user_id: int,
    current_user: models.User = Depends(get_company_user),
    db: Session = Depends(get_db),
):
    """
    求人に応募したユーザーの応募を拒否する。
    """
    response_data = job_crud.reject_application(db, job_id, user_id)
    message = message_crud.create_message(
        db,
        schemas.MessageCreate(
            title="応募が拒否されました",
            message=f"{response_data.job.author.username}さんが応募を拒否しました。",
            type="J",
            user_list=[user_id],
        ),
    )
    message_crud.send_message(db, [user_id], message.id)
    return response_data


@router.put("/{job_id}/bookmark", summary="イベントお気に入り登録切り替え")
def bookmark_job(
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    イベントをお気に入り登録切り替えを行う。
    すでにお気に入り登録している場合は、お気に入り登録を解除する。
    """
    job = job_crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job Not Found")
    return job_crud.toggle_bookmark_job(db, job_id, current_user.id)


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
    job = job_crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job Not Found")
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
    job = job_crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job Not Found")
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


@router.get(
    "/{job_id}/impressions",
    summary="イベント広告のインプレッション取得",
    tags=["広告インプレッション"],
)
def get_job_impressions(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """
    イベント広告のインプレッションを取得する。
    """
    return job_crud.get_job_impressions(db, job_id)
