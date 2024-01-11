from fastapi.testclient import TestClient


class TestUser:
    def test_create_user(self, general_client: TestClient, api_path: str):
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


class TestPlan:
    def test_create_plan(
        self,
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
        assert response.json()["name"] == "テストプラン"
