from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.db import BaseModel


class MessageBox(BaseModel):
    __tablename__ = "message_box"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"))
    is_read = Column(Boolean, default=False)

    user = relationship("User", back_populates="messages")
    message = relationship("Message", back_populates="users")


class Message(BaseModel):
    id = Column(Integer, primary_key=True)
    type = Column(String(1), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)

    users = relationship(
        "MessageBox",
        back_populates="message",
    )
