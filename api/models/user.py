from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import BaseModel


class Application(BaseModel):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String(2))

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

    job_reviews = relationship("JobReview", backref="user")
    job_bookmarks = relationship(
        "Job", secondary="job_bookmarks", back_populates="bookmark_users"
    )
    job_postings = relationship("Job", backref="author")
    job_watched = relationship(
        "Job",
        back_populates="watched_users",
        secondary="job_watched",
    )

    event_reviews = relationship("EventReview", backref="user")
    event_bookmarks = relationship(
        "Event", secondary="event_bookmarks", back_populates="bookmark_users"
    )
    event_postings = relationship("Event", backref="author")
    event_watched = relationship(
        "Event",
        back_populates="watched_users",
        secondary="event_watched",
    )

    applications = relationship("Application", back_populates="user")
    messages = relationship("MessageBox", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")
