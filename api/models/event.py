"""イベント ID(primary)
イベント名
郵便番号
都道府県
市区町村
番地・建物名
イベントの電話番号(optional)
イベントのメールアドレス(optional)
イベントのホームページ(optional)
作成日時
更新日時
掲載期間
法人 ID(foreign)
求人 ID(foreign,optinal)
イベントの内容
イベントの日時
イベントの参加費(optional)
イベントの定員(optional)
イベントの注意事項(optional)
イベントの追加メッセージ(optional)"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    postal_code = Column(String(10))
    prefecture = Column(String(10))
    city = Column(String(50))
    address = Column(String(50))
    phone_number = Column(String(20))
    email = Column(String(50))
    homepage = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    period = Column(String(50))
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="events")
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    job = relationship("Job", back_populates="events", uselist=False)
    event_description = Column(String(1000))
    event_date = Column(DateTime)
    participation_fee = Column(String(50))
    capacity = Column(String(50))
    caution = Column(String(1000))
    additional_message = Column(String(1000))
