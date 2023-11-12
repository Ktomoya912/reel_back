from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    postal_code = Column(String(10))
    prefecture = Column(String(10))
    city = Column(String(50))
    address = Column(String(50))
    phone_number = Column(String(20))
    email = Column(String(50))
    homepage = Column(String(50))
    participation_fee = Column(String(50))  # 参加費
    capacity = Column(String(50))  # 定員
    caution = Column(String(1000))
    additional_message = Column(String(1000))
    period = Column(String(50))
    event_description = Column(String(1000))

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    reviews = relationship("Review", back_populates="event")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="events")
    bookmark_users = relationship(
        "User", secondary="event_bookmark", back_populates="event_bookmarks"
    )
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True, unique=True)
    job = relationship("Job", back_populates="event", uselist=False)
    tags = relationship("Tag", secondary="event_tag", back_populates="events")
    event_date = Column(DateTime)
    watch_users = relationship(
        "User", secondary="event_history", back_populates="watch_events"
    )
