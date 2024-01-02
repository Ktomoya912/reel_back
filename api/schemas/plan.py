from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    name: str = Field(..., max_length=255)
    price: int
    period: datetime


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class Plan(PlanBase):
    id: int

    class Config:
        orm_mode = True


class PurchaseBase(BaseModel):
    plan_id: int


class PurchaseCreate(PurchaseBase):
    pass


class Purchase(PurchaseBase):
    id: int
    is_paid: bool

    class Config:
        orm_mode = True
