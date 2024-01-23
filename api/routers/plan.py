from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from jinja2 import Template
from sqlalchemy.orm.session import Session

import api.cruds.message as message_crud
import api.cruds.plan as plan_crud
from api import config, models, schemas
from api.dependencies import get_admin_user, get_company_user, get_config, get_db
from api.utils import send_email

router = APIRouter(prefix="/plans", tags=["プラン"])


@router.get("/", response_model=list[schemas.Plan], summary="プラン取得")
def get_plans(
    db: Session = Depends(get_db),
):
    """
    プランの一覧を取得する。"""
    return plan_crud.get_plans(db)


@router.post("/", response_model=schemas.Plan, summary="プラン作成")
def create_plan(
    plan_create: schemas.PlanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    必要データを受け取り、プランを作成する。
    レスポンスとして、作成されたプランの情報を返す。
    プランを作成できるのは管理者のみ。"""
    return plan_crud.create_plan(db, plan_create)


@router.put("/{plan_id}", response_model=schemas.Plan, summary="プラン更新")
def update_plan(
    plan_id: int,
    plan_update: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    必要データを受け取り、プランを更新する。
    レスポンスとして、更新されたプランの情報を返す。
    プランを更新できるのは管理者のみ。"""
    return plan_crud.update_plan(db, plan_id, plan_update)


@router.delete("/{plan_id}", response_model=bool, summary="プラン削除")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """
    プランを削除する。
    プランを削除できるのは管理者のみ。
    """
    if plan_crud.delete_plan(db, plan_id):
        return True
    else:
        raise HTTPException(status_code=404, detail="Plan not found")


@router.post("/purchase", response_model=schemas.Purchase)
def purchase_plan(
    plan: schemas.PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    return plan_crud.purchase_plan(db, plan, current_user)


@router.post("/cancel/{purchase_id}", response_model=bool, summary="プランキャンセル")
def cancel_plan(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """
    プランをキャンセルする。"""
    if plan_crud.cancel_plan(db, purchase_id):
        return True
    else:
        raise HTTPException(status_code=404, detail="purchase not found")


@router.get("/no-paid", response_model=list[schemas.Purchase], summary="未払いプラン")
def get_no_paid_plans(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """企業ユーザーが未払いのプランを取得する。"""
    return plan_crud.get_no_paid_plans(db, current_user.id)


@router.get("/paid", response_model=list[schemas.Purchase], summary="支払い済みプラン")
def get_paid_plans(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_company_user),
):
    """企業ユーザーが支払い済みのプランを取得する。"""
    return plan_crud.get_paid_plans(db, current_user.id)


@router.get("/no-paid-users", response_model=list[schemas.User], summary="未払いユーザー")
def get_no_paid_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user),
):
    """管理者が未払いのユーザーを取得する。"""
    return plan_crud.get_no_paid_users(db)


@router.post(
    "/paid-checked/{purchase_id}", response_model=schemas.Purchase, summary="支払い確認"
)
def paid_checked(
    purchase_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    settings: config.BaseConfig = Depends(get_config),
    current_user: models.User = Depends(get_admin_user),
):
    """管理者が支払い確認をした後、支払い済みにする。"""
    purchase = plan_crud.paid_checked(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=400, detail="purchase is already checked")
    html_file = Path(__file__).parent.parent / "templates" / "MAIL-paid-check.html"
    html = Template(html_file.read_text()).render(
        plan_name=purchase.plan.name,
        plan_price=purchase.plan.price,
        plan_amount=purchase.contract_amount,
    )
    type = purchase.job if purchase.job else purchase.event
    type_s = "J" if type == purchase.job else "E"
    message = message_crud.create_message(
        db,
        schemas.MessageCreate(
            title=f"「{type.name}」が有効化されました。",
            message=f"あなたが購入した、「{purchase.plan.name}」プランの「{type.name}」が有効化されました。",
            type=type_s,
            user_list=[purchase.user.id],
        ),
    )
    message_crud.send_message(db, [purchase.user.id], message.id)
    background_tasks.add_task(
        send_email,
        from_=settings.MAIL_SENDER,
        to=purchase.user.email,
        subject="支払い確認完了のお知らせ",
        body=html,
    )
    return purchase


@router.get("/{plan_id}", response_model=schemas.Plan, tags=["プラン"])
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    プランの詳細を取得する。
    """
    plan = plan_crud.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
