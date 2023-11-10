from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from api.db import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(50), unique=True, index=True)
    jobs = relationship("Job", secondary="job_tag", back_populates="tags")
    events = relationship("Event", secondary="event_tag", back_populates="tags")

    def __repr__(self):
        return f"<Tag({self.id}, {self.tag_name})>"


class JobTag(Base):
    __tablename__ = "job_tag"

    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class EventTag(Base):
    __tablename__ = "event_tag"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    def __repr__(self):
        return f"<EventTag({self.event_id}, {self.tag_id})>"
