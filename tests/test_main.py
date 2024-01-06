from fastapi.testclient import TestClient


def test_main(general_client: TestClient):
    response = general_client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world!"}


def test_create_and_read(general_client: TestClient, api_path: str):
    response = general_client.post(
        f"{api_path}/users/",
        json={
            "username": "username",
            "password": "password",
            "email": "email@example.com",
            "sex": "o",
            "birthday": "2021-01-01",
        },
    )
    assert response.status_code == 200, response.text


def test_create_plan(
    general_client: TestClient,
    company_client: TestClient,
    admin_client: TestClient,
    api_path: str,
):
    response = general_client.post(
        f"{api_path}/plans/",
        json={"name": "テストプラン", "price": 30_000, "period": 30},
    )
    assert response.status_code == 400, response.text
    response = company_client.post(
        f"{api_path}/plans/",
        json={"name": "テストプラン", "price": 30_000, "period": 30},
    )
    assert response.status_code == 400, response.text
    response = admin_client.post(
        f"{api_path}/plans",
        json={"name": "テストプラン", "price": 30_000, "period": 30},
    )
    assert response.status_code == 200, response.text
