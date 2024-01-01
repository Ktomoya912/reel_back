from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.db import BaseModel


class JobTime(BaseModel):
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class JobTag(BaseModel):
    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class JobReview(BaseModel):
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    review = Column(Text)
    review_point = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))


class JobBookmark(BaseModel):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)


class JobWatched(BaseModel):
    __tablename__ = "job_watched"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    count = Column(Integer, default=1)


class Job(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    salary = Column(String(255))
    working_location = Column(String(255))
    description = Column(Text)
    is_one_day = Column(Boolean, default=False)
    period = Column(DateTime)
    additional_message = Column(Text)
    status = Column(String(2))
    user_id = Column(Integer, ForeignKey("users.id"))

    job_times = relationship("JobTime", backref="job")
    tags = relationship("Tag", secondary="job_tags", back_populates="jobs")
    reviews = relationship("JobReview", backref="job")
    bookmark_users = relationship(
        "User", secondary="job_bookmarks", back_populates="job_bookmarks"
    )
    applications = relationship("Application", back_populates="job")
    watched_users = relationship(
        "User",
        back_populates="job_watched",
        secondary="job_watched",
    )
