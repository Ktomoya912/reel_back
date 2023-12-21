from sqlalchemy import Column, ForeignKey, Integer, String

from api.db import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    postal_code = Column(String(8), nullable=False)
    prefecture = Column(String(10), nullable=False)
    city = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    homepage = Column(String(255), nullable=False)
    representative = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
