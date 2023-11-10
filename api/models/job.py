from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from api.db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="jobs")
    event = relationship("Event", back_populates="job")
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime)
    salary = Column(String(50))
    tags = relationship("Tag", secondary="job_tag", back_populates="jobs")
    bookmark_users = relationship(
        "User", secondary="job_bookmark", back_populates="job_bookmarks"
    )
    reviews = relationship("Review", back_populates="job")
    working_hours = Column(String(50))
    working_location = Column(String(50))
    job_description = Column(String(1000))
    is_one_day = Column(String(10))
    period = Column(String(50))
    additional_message = Column(String(1000))
    applicants = relationship(
        "User", secondary="job_application", back_populates="applications"
    )
    watch_users = relationship(
        "User", secondary="job_history", back_populates="watch_jobs"
    )


# 応募リスト
class JobApplication(Base):
    __tablename__ = "job_application"

    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime)
    status = Column(String(50))  # 応募の状態

    job = relationship("Job")
    user = relationship("User")