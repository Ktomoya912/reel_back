"""法人 ID(primary)
法人名
郵便番号
都道府県
市区町村
番地・建物名
法人の電話番号
法人のメールアドレス
法人のホームページ (optional)
代表者名
作成日時
ユーザー ID(foreign)
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.db import Base


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    postal_code = Column(String(10))
    prefecture = Column(String(10))
    city = Column(String(50))
    address = Column(String(50))
    phone_number = Column(String(20))
    email = Column(String(50))
    homepage = Column(String(50))
    representative = Column(String(50))
    created_at = Column(DateTime)
    users = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")
