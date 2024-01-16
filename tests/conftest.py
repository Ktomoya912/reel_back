from datetime import date

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.db import Base
from api.dependencies import get_config, get_current_user, get_db, get_test_config
from api.main import create_app
from api.models import User

TEST_DB_URL = "sqlite:///:memory:"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MockBaseUser(BaseModel):
    id: int = 2
    username: str = "username"
    password: str = pwd_context.hash("password")
    is_active: bool = True
    job_bookmarks: list = []
    job_watched_link: list = []
    event_bookmarks: list = []
    event_watched_link: list = []


class MockCompanyUser(MockBaseUser):
    user_type: str = "c"


class MockGeneralUser(MockBaseUser):
    user_type: str = "g"


class MockAdminUser(MockBaseUser):
    id: int = 1
    username: str = "admin"
    password: str = pwd_context.hash("admin")
    user_type: str = "a"


@pytest.fixture
def api_path():
    return "/api/v1"


@pytest.fixture(scope="class")
def db_session():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    user = User(
        username="admin",
        password=pwd_context.hash("admin"),
        email="samnple@sample.com",
        sex="o",
        birthday=date(2000, 1, 1),
        image_url="https://example.com",
        user_type="a",
        is_active=True,
    )
    session.add(user)
    session.commit()
    yield session
    session.close()


@pytest.fixture
def general_client(db_session):
    app = create_app()

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_config] = get_test_config
    app.dependency_overrides[get_current_user] = MockGeneralUser

    with TestClient(app) as client:
        yield client


@pytest.fixture
def company_client(db_session):
    app = create_app()

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_config] = get_test_config
    app.dependency_overrides[get_current_user] = MockCompanyUser

    with TestClient(app) as client:
        yield client


@pytest.fixture
def admin_client(db_session):
    app = create_app()

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_config] = get_test_config
    app.dependency_overrides[get_current_user] = MockAdminUser

    with TestClient(app) as client:
        yield client
