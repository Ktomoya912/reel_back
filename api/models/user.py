from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    gender = Column(String(10))
    birthday = Column(DateTime)
    created_at = Column(DateTime)
    deleted_at = Column(DateTime)
    user_type = Column(String(10))
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="users")

    def __repr__(self):
        return f"<User({self.id}, {self.username})>"
