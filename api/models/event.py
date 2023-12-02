from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from api.db import BaseModel


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

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))

    user = relationship("User", back_populates="event_watched")
    event = relationship("Event", back_populates="watched_users")


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
    event_description = Column(Text)
    particication_fee = Column(String(255))
    capacity = Column(Integer)
    period = Column(DateTime)
    status = Column(String(2))
    user_id = Column(Integer, ForeignKey("users.id"))

    event_times = relationship("EventTime", backref="event")
    tags = relationship("Tag", secondary="event_tags", back_populates="events")
    reviews = relationship("EventReview", backref="event")
    bookmark_users = relationship(
        "User", secondary="event_bookmarks", back_populates="event_bookmarks"
    )
    watched_users = relationship("EventWatched", back_populates="event")
