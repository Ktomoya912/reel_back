from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import BaseModel


class Plan(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    price = Column(Integer)
    period = Column(Integer)  # x日間

    users = relationship("Purchase", back_populates="plan")


class Purchase(BaseModel):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    # 契約数
    contract_amount = Column(Integer, default=1)
    is_paid = Column(Boolean, default=False)

    user = relationship("User", back_populates="purchases", uselist=False)
    plan = relationship("Plan", back_populates="users", uselist=False)

    @property
    def contract_days(self) -> timedelta:
        return timedelta(days=self.plan.period * self.contract_amount)

    @property
    def expiration_date(self) -> datetime:
        return self.updated_at + self.contract_days
