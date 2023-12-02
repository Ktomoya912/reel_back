from sqlalchemy import create_engine

from api.models import company, event, job, message, tag, user, plan  # noqa F401
from api.db import Base

DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"
engine = create_engine(DB_URL, echo=True)


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    reset_db()
