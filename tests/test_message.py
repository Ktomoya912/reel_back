import pytest
import pytest_asyncio
from httpx import AsyncClient, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.db import Base, get_db
from api.main import app
from api.routers.auth import get_current_user

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


class MockUser(BaseModel):
    id: int = 1
    username: str = "username"
    password: str = "password"


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_current_user] = MockUser

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_create_and_read(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/notices/?mail_auth=false",
        json={
            "title": "this is message",
            "message": "string",
            "type": "J",
            "user_list": [1],
        },
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json["title"] == "this is message", response_json

    response = await async_client.get("/notices/")
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert len(response_json) == 2, response_json
