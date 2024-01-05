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


def reset_db():
    load_dotenv()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = next(get_db())
    admin_user = user.User(
        username="admin",
        password=pwd_context.hash("password"),
        email=os.getenv("MAIL_SENDER"),
        birthday=date(2000, 1, 1),
        user_type="a",
        is_active=True,
    )
    db.add(admin_user)
    db.commit()


if __name__ == "__main__":
    reset_db()
