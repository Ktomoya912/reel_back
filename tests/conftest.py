import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.db import Base
from api.dependencies import get_config, get_current_user, get_db, get_test_config
from api.main import create_app

TEST_DB_URL = "sqlite:///:memory:"


class MockCompanyUser(BaseModel):
    id: int = 1
    username: str = "username"
    password: str = "password"
    is_active: bool = True
    user_type: str = "c"


class MockGeneralUser(BaseModel):
    id: int = 1
    username: str = "username"
    password: str = "password"
    is_active: bool = True
    user_type: str = "g"


class MockAdminUser(BaseModel):
    id: int = 1
    username: str = "username"
    password: str = "password"
    is_active: bool = True
    user_type: str = "a"


@pytest.fixture
def api_path():
    return "/api/v1"


def get_test_app():
    app = create_app()
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def get_test_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_config] = get_test_config
    return app


@pytest.fixture
def general_client():
    app = get_test_app()
    app.dependency_overrides[get_current_user] = MockGeneralUser

    with TestClient(app) as client:
        yield client


@pytest.fixture
def company_client():
    app = get_test_app()
    app.dependency_overrides[get_current_user] = MockCompanyUser

    with TestClient(app) as client:
        yield client


@pytest.fixture
def admin_client():
    app = get_test_app()
    app.dependency_overrides[get_current_user] = MockAdminUser

    with TestClient(app) as client:
        yield client
