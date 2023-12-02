from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, InternalError

from api.models import bookmark, company, event, job, message, review, tag, user
from api.db import Base, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


DB_URL = f"""mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:
{DB_PORT}/?charset=utf8"""

DEMO_DB_URL = f"""mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}\
/demo?charset=utf8"""

engine = create_engine(DEMO_DB_URL, echo=True)


def database_exists():
    # 接続を試みることでデータベースの存在を確認する
    try:
        engine.connect()
        return True
    except (OperationalError, InternalError) as e:
        print(e)
        print("データベースが存在しません")
        return False


def create_database():
    if not database_exists():
        root = create_engine(DB_URL, echo=True)
        with root.connect() as conn:
            conn.execute(text("CREATE DATABASE demo"))
        print("データベースを作成しました")


if __name__ == "__main__":
    create_database()
