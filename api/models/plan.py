from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import BaseModel


class Plan(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    price = Column(Integer)
    period = Column(DateTime)

    users = relationship("Purchase", back_populates="plan")


class Purchase(BaseModel):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    is_paid = Column(Boolean, default=False)

    user = relationship("User", back_populates="purchases")
    plan = relationship("Plan", back_populates="users")
