import os
from datetime import date

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import create_engine

from api.db import Base, get_db
from api.models import company, event, job, message, plan, tag, user  # noqa F401

DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"
engine = create_engine(DB_URL, echo=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def make_admin_user():
    load_dotenv()
    db = next(get_db())
    admin_user = user.User(
        username="admin",
        password=pwd_context.hash(os.getenv("ADMIN_PASSWORD")),
        email=os.getenv("ADMIN_EMAIL"),
        birthday=date(2000, 1, 1),
        user_type="a",
        is_active=True,
    )
    db.add(admin_user)
    db.commit()


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    reset_db()
    make_admin_user()
