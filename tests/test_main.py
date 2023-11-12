import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from api.db import Base, get_db
from api.main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pytest_asyncio

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


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

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_get_hello(async_client) -> None:
    response = await async_client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world!"}


@pytest.mark.asyncio
async def test_create_and_read(async_client):
    respose = await async_client.post(
        "/users",
        json={
            "username": "hoge1",
            "password": "i_am_password",
            "email": "i_am_email1",
            "gender": "",
            "birthday": "2023-11-11 00:00:00",
            "user_type": "default",
        },
    )
    assert respose.status_code == 200
    respose_json = respose.json()
    assert respose_json["username"] == "hoge1"
    assert respose_json["password"] != "i_am_password"

    respose = await async_client.get("/users")
    assert respose.status_code == 200
    respose_json = respose.json()
    assert len(respose_json) == 1
    assert respose_json[0]["username"] == "hoge1"
    assert respose_json[0]["password"] != "i_am_password"


@pytest.mark.asyncio
async def test_create_and_update(async_client):
    respose = await async_client.post(
        "/users",
        json={
            "username": "hoge2",
            "password": "i_am_password",
            "email": "i_am_email2",
            "gender": "男",
            "birthday": "2023-11-11 00:00:00",
            "user_type": "default",
        },
    )
    assert respose.status_code == 200, respose.text
    respose_json = respose.json()
    id = respose_json["id"]

    respose = await async_client.put(
        f"/users/{id}",
        json={
            "username": "hoge123",
            "password": "i_am_password",
            "email": "i_am_email2",
            "gender": "男",
            "birthday": "2023-11-11 00:00:00",
            "user_type": "default",
        },
    )
    assert respose.status_code == 200, respose.text
    respose_json = respose.json()
    assert respose_json["username"] == "hoge123"
    assert respose_json["password"] != "i_am_password"


@pytest.mark.asyncio
async def test_create_and_delete(async_client):
    respose = await async_client.post(
        "/users",
        json={
            "username": "hoge3",
            "password": "i_am_password",
            "email": "i_am_email3",
            "gender": "女",
            "birthday": "2023-11-11 00:00:00",
            "user_type": "default",
        },
    )
    assert respose.status_code == 200, respose.text
    respose_json = respose.json()
    id = respose_json["id"]

    respose = await async_client.delete(f"/users/{id}")
    assert respose.status_code == 200
    respose_json = respose.json()
    assert respose_json is None
