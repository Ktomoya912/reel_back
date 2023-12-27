import os
import re
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, sessionmaker

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
ASYNC_DB_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/demo?charset=utf8"
)

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "s"

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    # @declared_attr
    def __str__(self):
        return (
            getattr(self, "name", None) or getattr(self, "title", None) or str(self.id)
        )

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
