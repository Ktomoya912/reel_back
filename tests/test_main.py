from fastapi.testclient import TestClient


def test_main(client: TestClient):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world!"}


def test_create_and_read(client: TestClient):
    response = client.post(
        "/users/",
        json={
            "username": "username",
            "password": "password",
            "email": "email@example.com",
            "sex": "o",
            "birthday": "2021-01-01",
        },
    )
    assert response.status_code == 200, response.text
