"""
レビュー ID(primary)
レビュー内容
レビューの評価(1~5)
作成日時
更新日時
ユーザー ID(foreign)
求人 ID(foreign,optinal)
イベント ID(foreign,optinal)
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True, index=True)
    review_description = Column(String(1000))
    review_score = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="reviews")
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    job = relationship("Job", back_populates="reviews", uselist=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    event = relationship("Event", back_populates="reviews", uselist=False)
