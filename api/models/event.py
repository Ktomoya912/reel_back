from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.db import BaseModel
from api.utils import get_jst_now


class EventTime(BaseModel):
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class EventReview(BaseModel):
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    review = Column(Text)
    review_point = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))


class EventTag(BaseModel):
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class EventBookmark(BaseModel):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)


class EventWatched(BaseModel):
    __tablename__ = "event_watched"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    count = Column(Integer, default=1)


class Event(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    postal_code = Column(String(8))
    prefecture = Column(String(10))
    city = Column(String(255))
    address = Column(String(255))
    phone_number = Column(String(20))
    email = Column(String(255))
    homepage = Column(String(255))
    description = Column(Text)
    participation_fee = Column(String(255))
    capacity = Column(Integer)
    status = Column(String(10), default="draft")
    additional_message = Column(Text)
    image_url = Column(String(255))
    caution = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    purchase_id = Column(Integer, ForeignKey("purchases.id"))

    event_times = relationship("EventTime", backref="event")
    tags = relationship("Tag", secondary="event_tags", back_populates="events")
    reviews = relationship("EventReview", backref="event")
    bookmark_users = relationship(
        "User", secondary="event_bookmarks", back_populates="event_bookmarks"
    )
    watched_users = relationship(
        "User",
        back_populates="event_watched",
        secondary="event_watched",
    )
    purchase = relationship("Purchase", backref="event")

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
