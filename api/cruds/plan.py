from typing import Literal

from sqlalchemy.orm.session import Session

from api import models, schemas


def create_plan(db: Session, plan_create: schemas.PlanCreate) -> models.Plan:
    plan = models.Plan(**plan_create.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_plans(db: Session) -> list[models.Plan]:
    plans = db.query(models.Plan).all()
    return plans


def update_plan(
    db: Session, plan_id: int, plan_update: schemas.PlanUpdate
) -> models.Plan:
    plan = db.query(models.Plan).get(plan_id)
    plan.update(**plan_update.model_dump())
    db.commit()
    db.refresh(plan)
    return plan


def delete_plan(db: Session, plan_id: int) -> Literal[True]:
    plan = db.query(models.Plan).get(plan_id)
    db.delete(plan)
    db.commit()
    return True


def purchase_plan(
    db: Session, plan_id: int, current_user: schemas.User
) -> models.Purchase:
    plan = db.query(models.Plan).get(plan_id)
    purchase = models.Purchase(user=current_user, plan=plan)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def cancel_plan(db: Session, purchase_id: int) -> Literal[True]:
    purchase = db.query(models.Purchase).get(purchase_id)
    db.delete(purchase)
    db.commit()
    return True


def get_paid_plans(db: Session, user_id: int) -> list[models.Purchase]:
    purchases = (
        db.query(models.Purchase)
        .filter(
            models.Purchase.user_id == user_id,
            models.Purchase.is_paid == True,  # noqa
        )
        .all()
    )
    return purchases


def get_no_paid_plans(db: Session, user_id: int) -> list[models.Purchase]:
    purchases = (
        db.query(models.Purchase)
        .filter(
            models.Purchase.user_id == user_id,
            models.Purchase.is_paid == False,  # noqa
        )
        .all()
    )
    return purchases


def get_no_paid_users(db: Session) -> list[models.User]:
    purchases = (
        db.query(models.Purchase).filter(models.Purchase.is_paid == False).all()  # noqa
    )
    return [purchase.user for purchase in purchases]


def paid_checked(db: Session, purchase_id: int) -> Literal[True]:
    purchase = db.query(models.Purchase).get(purchase_id)
    purchase.is_paid = True
    db.commit()
    db.refresh(purchase)
    return True
