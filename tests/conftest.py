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


class MockUser(BaseModel):
    id: int = 1
    username: str = "username"
    password: str = "password"


@pytest.fixture
def api_path():
    return "/api/v1"


@pytest.fixture
def client():
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
    app.dependency_overrides[get_current_user] = MockUser

    with TestClient(app) as client:
        yield client
