import os
import re
from datetime import date

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, sessionmaker

from api.utils import get_jst_now

load_dotenv()
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")

DB_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/demo?charset=utf8"
)

engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class NoEnvironmentError(Exception):
    def __init__(self, message=""):
        self.message = f'環境変数が設定されていません。\n".env"ファイルに"{message}"を設定してください。'
        super().__init__(self.message)


class BaseModel(Base):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "s"

    created_at = Column(DateTime, default=get_jst_now)
    updated_at = Column(DateTime, default=get_jst_now, onupdate=get_jst_now)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    # @declared_attr
    def __str__(self):
        return (
            getattr(self, "name", None) or getattr(self, "title", None) or str(self.id)
        )

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


def get_db() -> Session:
    db = Session()
    try:
        yield db
    finally:
        db.close()


def make_admin_user():
    from api.models import user

    if os.getenv("ADMIN_PASSWORD") is None:
        raise NoEnvironmentError("ADMIN_PASSWORD")
    if os.getenv("ADMIN_EMAIL") is None:
        raise NoEnvironmentError("ADMIN_EMAIL")
    db = next(get_db())
    admin_user = user.User(
        username="admin",
        password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(
            os.getenv("ADMIN_PASSWORD")
        ),
        email=os.getenv("ADMIN_EMAIL"),
        birthday=date(2000, 1, 1),
        user_type="a",
        is_active=True,
    )
    db.add(admin_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
