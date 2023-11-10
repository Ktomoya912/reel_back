from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    postal_code = Column(String(10))
    prefecture = Column(String(10))
    city = Column(String(50))
    address = Column(String(50))
    phone_number = Column(String(20))
    email = Column(String(50))
    homepage = Column(String(50))
    representative = Column(String(50))  # 代表者
    created_at = Column(DateTime)
    users = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")
    events = relationship("Event", back_populates="company")
