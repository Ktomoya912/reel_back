from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from api.db import BaseModel


class Tag(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    events = relationship("Event", secondary="event_tags", back_populates="tags")
    jobs = relationship("Job", secondary="job_tags", back_populates="tags")
