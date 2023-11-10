from sqlalchemy import Column, Integer, String, ForeignKey

from api.db import Base


class EventBookmark(Base):
    __tablename__ = "event_bookmark"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class JobBookmark(Base):
    __tablename__ = "job_bookmark"

    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
