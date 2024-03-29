from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.db import BaseModel
from api.utils import get_jst_now


class JobTime(BaseModel):
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class JobTag(BaseModel):
    job_id = Column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id = Column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class JobReview(BaseModel):
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    review = Column(Text)
    review_point = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))


class JobBookmark(BaseModel):
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    job_id = Column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )


class JobWatched(BaseModel):
    __tablename__ = "job_watched"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    job_id = Column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    count = Column(Integer, default=1)

    user = relationship("User", back_populates="job_watched_link")
    job = relationship("Job", back_populates="watched_user_link")


class Job(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    salary = Column(String(255))
    postal_code = Column(String(8))
    prefecture = Column(String(10))
    city = Column(String(255))
    address = Column(String(255))
    description = Column(Text)
    is_one_day = Column(Boolean, default=False)
    additional_message = Column(Text)
    image_url = Column(String(255))
    status = Column(String(10), default="draft")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    purchase_id = Column(Integer, ForeignKey("purchases.id"))

    author = relationship("User", back_populates="job_postings")
    job_times = relationship(
        "JobTime",
        backref="job",
    )
    tags = relationship(
        "Tag",
        secondary="job_tags",
        back_populates="jobs",
    )
    reviews = relationship(
        "JobReview",
        backref="job",
    )
    bookmark_users = relationship(
        "User",
        secondary="job_bookmarks",
        back_populates="job_bookmarks",
    )
    applications = relationship(
        "Application",
        back_populates="job",
    )
    watched_user_link = relationship(
        "JobWatched", back_populates="job", cascade="all, delete-orphan"
    )
    purchase = relationship("Purchase", back_populates="job", uselist=False)

    @property
    def is_active(self):
        if self.purchase is None:
            return False
        return get_jst_now() < self.purchase.expiration_date

    @property
    def average_review_point(self):
        if len(self.reviews) == 0:
            return 0
        return round(
            sum([review.review_point for review in self.reviews]) / len(self.reviews), 1
        )
