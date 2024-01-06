from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    name: str = Field(..., max_length=255)
    price: int
    period: int = Field(30, description="契約日数")


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
    contract_amount: int = Field(1, description="契約数", ge=1)


class Purchase(PurchaseBase):
    id: int
    is_paid: bool
    expiration_date: datetime

    class Config:
        orm_mode = True
