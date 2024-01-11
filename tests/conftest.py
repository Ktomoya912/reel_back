import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext
from api.db import Base
from api.dependencies import get_config, get_current_user, get_db, get_test_config
from api.main import create_app

TEST_DB_URL = "sqlite:///:memory:"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MockBaseUser(BaseModel):
    id: int = 1
    username: str = "username"
    password: str = pwd_context.hash("password")
    is_active: bool = True
    job_bookmarks: list = []
    event_bookmarks: list = []


class MockCompanyUser(MockBaseUser):
    user_type: str = "c"


class MockGeneralUser(MockBaseUser):
    user_type: str = "g"


class MockAdminUser(MockBaseUser):
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
