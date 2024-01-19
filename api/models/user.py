from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import BaseModel


class Application(BaseModel):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    status = Column(String(2), default="p")

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class User(BaseModel):
    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True)
    password = Column(String(255))
    email = Column(String(255), unique=True)
    sex = Column(String(1), default="o")
    birthday = Column(Date)
    image_url = Column(String(255))
    user_type = Column(String(1), default="u")
    is_active = Column(Boolean, default=False)

    company = relationship("Company", backref="user", uselist=False)

    job_reviews = relationship(
        "JobReview", backref="user", cascade="all, delete-orphan"
    )
    job_bookmarks = relationship(
        "Job",
        secondary="job_bookmarks",
        back_populates="bookmark_users",
    )
    job_postings = relationship(
        "Job",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    job_watched_link = relationship("JobWatched", back_populates="user")

    event_reviews = relationship(
        "EventReview", backref="user", cascade="all, delete-orphan"
    )
    event_bookmarks = relationship(
        "Event",
        secondary="event_bookmarks",
        back_populates="bookmark_users",
    )
    event_postings = relationship(
        "Event", back_populates="author", cascade="all, delete-orphan"
    )
    event_watched_link = relationship("EventWatched", back_populates="user")

    applications = relationship(
        "Application", back_populates="user", cascade="all, delete-orphan"
    )
    messages = relationship(
        "MessageBox",
        back_populates="user",
    )
    purchases = relationship(
        "Purchase", back_populates="user", cascade="all, delete-orphan"
    )
