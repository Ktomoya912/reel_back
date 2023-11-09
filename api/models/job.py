"""求人 ID(primary)
法人 ID(foreign)
イベント ID(foreign,optional)
作成日時
更新日時
給料
勤務時間
勤務場所
仕事内容
単発か否か
掲載期間
企業からの追加メッセージ(optional)"""
from sqlalchemy import Column, Integer, String, ForeignKey, Datetime
from sqlalchemy.orm import relationship

from api.db import Base


class Job(Base):
    __tablename__ = "job"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="jobs")
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    event = relationship("Event", back_populates="jobs", uselist=False)
    created_at = Column(Datetime)
    updated_at = Column(Datetime)
    salary = Column(String(50))
    working_hours = Column(String(50))
    working_location = Column(String(50))
    job_description = Column(String(1000))
    is_one_day = Column(String(10))
    period = Column(String(50))
    additional_message = Column(String(1000))
