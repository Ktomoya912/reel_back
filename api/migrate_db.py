from sqlalchemy import create_engine

from api.db import Base
from api.models import company, event, job, message, plan, tag, user  # noqa F401

DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"
engine = create_engine(DB_URL, echo=True)


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    reset_db()
