import pytest
import pytest_asyncio
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.db import Base, get_db
from api.routers.auth import is_product
from api.main import app

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
    app.dependency_overrides[is_product] = lambda: False

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def async_create_user(async_client: AsyncClient) -> Response:
    response = await async_client.post(
        "/users/",
        json={
            "username": "username",
            "password": "password",
            "email": "my@sample.com",
            "sex": "f",
            "birthday": "2023-12-27",
            "user_type": "u",
        },
    )
    yield response


@pytest.mark.asyncio
async def test_get_hello(async_client) -> None:
    response = await async_client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world!"}


@pytest.mark.asyncio
async def test_create_and_read(async_client: AsyncClient, async_create_user: Response):
    response = async_create_user
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["username"] == "username"
    assert response_json["password"] != "password"

    response = await async_client.get("/users")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["username"] == "username"
    assert response_json[0]["password"] != "password"


@pytest.mark.asyncio
async def test_create_and_update(
    async_client: AsyncClient, async_create_user: Response
):
    response = async_create_user

    assert response.status_code == 200, response.text
    response_json = response.json()
    id = response_json["id"]

    response = await async_client.put(
        f"/users/{id}",
        json={
            "username": "hoge123",
            "password": "i_am_password",
            "email": "i_am_email2@example.com",
            "sex": "m",
            "birthday": "2023-11-11",
            "user_type": "g",
        },
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json["username"] == "hoge123"
    assert response_json["password"] != "i_am_password"


@pytest.mark.asyncio
async def test_create_and_delete(
    async_client: AsyncClient, async_create_user: Response
):
    response = async_create_user
    assert response.status_code == 200, response.text
    response_json = response.json()
    id = response_json["id"]

    response = await async_client.delete(f"/users/{id}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json is None


@pytest.mark.asyncio
async def test_access_token(async_client: AsyncClient, async_create_user: Response):
    response = async_create_user

    response = await async_client.post(
        "/auth/token",
        data={
            "username": "username",
            "password": "password",
        },
    )
    # in_activeエラーが出ればOK
    assert response.status_code == 200 or response.status_code == 410, response.text
