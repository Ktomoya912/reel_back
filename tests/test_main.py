import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from api.db import Base, get_db
from api.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_hello() -> None:
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world!"}
