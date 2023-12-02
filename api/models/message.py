from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from api.db import BaseModel


class MessageBox(BaseModel):
    __tablename__ = "message_box"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))
    is_read = Column(Boolean, default=False)

    user = relationship("User", back_populates="messages")
    message = relationship("Message", back_populates="users")


class Message(BaseModel):
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    message = Column(Text)

    users = relationship("MessageBox", back_populates="message")
