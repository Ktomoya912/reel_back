from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    gender = Column(String(10))
    birthday = Column(DateTime)
    created_at = Column(DateTime)
    deleted_at = Column(DateTime)
    user_type = Column(String(10))
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="users")
    event_bookmarks = relationship(
        "Event", secondary="event_bookmark", back_populates="bookmark_users"
    )
    job_bookmarks = relationship(
        "Job", secondary="job_bookmark", back_populates="bookmark_users"
    )
    applications = relationship(
        "Job", secondary="job_application", back_populates="applicants"
    )
    watch_jobs = relationship(
        "Job", secondary="job_history", back_populates="watch_users"
    )
    watch_events = relationship(
        "Event", secondary="event_history", back_populates="watch_users"
    )
    messages = relationship("Message", back_populates="user")

    def __repr__(self):
        return f"<User({self.id}, {self.username})>"


# 閲覧履歴(Job)
class JobHistory(Base):
    __tablename__ = "job_history"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    count = Column(Integer)
    created_at = Column(DateTime)

    user = relationship("User")
    job = relationship("Job")


class EventHistory(Base):
    __tablename__ = "event_history"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("event.id"), primary_key=True)
    count = Column(Integer)
    created_at = Column(DateTime)

    user = relationship("User")
    event = relationship("Event")
