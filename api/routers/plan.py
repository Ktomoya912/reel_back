from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

import api.cruds.plan as plan_crud
from api import schemas
from api.dependencies import get_admin_user, get_company_user, get_db

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/", response_model=list[schemas.Plan])
def get_plans(
    db: Session = Depends(get_db),
):
    return plan_crud.get_plans(db)


@router.post("/", response_model=schemas.Plan)
def create_plan(
    plan_create: schemas.PlanCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    return plan_crud.create_plan(db, plan_create)


@router.put("/{plan_id}", response_model=schemas.Plan)
def update_plan(
    plan_id: int,
    plan_update: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    return plan_crud.update_plan(db, plan_id, plan_update)


@router.delete("/{plan_id}", response_model=bool)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    return plan_crud.delete_plan(db, plan_id)


@router.post("/{plan_id}/purchase", response_model=schemas.Purchase)
def purchase_plan(
    plan: schemas.PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_company_user),
):
    return plan_crud.purchase_plan(db, plan, current_user)


@router.post("/cancel/{purchase_id}", response_model=bool)
def cancel_plan(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_company_user),
):
    return plan_crud.cancel_plan(db, purchase_id)


@router.get("/no-paid", response_model=list[schemas.Purchase])
def get_no_paid_plans(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_company_user),
):
    return plan_crud.get_no_paid_plans(db, current_user.id)


@router.get("/paid", response_model=list[schemas.Purchase])
def get_paid_plans(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_company_user),
):
    return plan_crud.get_paid_plans(db, current_user.id)


@router.get("/no-paid-users", response_model=list[schemas.User])
def get_no_paid_users(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    return plan_crud.get_no_paid_users(db)


@router.post("/paid-checked/{purchase_id}", response_model=bool)
def paid_checked(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    return plan_crud.paid_checked(db, purchase_id)
