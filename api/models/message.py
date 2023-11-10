from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="messages")
    message = Column(String(1000))
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<Message({self.id}, {self.message})>"
