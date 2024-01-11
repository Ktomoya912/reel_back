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

    def test_read_user(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/users/")
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert len(response_json) == 1, response_json
        assert response_json[0]["username"] == "username", response_json

    def test_update_user(self, general_client: TestClient, api_path: str):
        response = general_client.put(
            f"{api_path}/users/1",
            json={
                "username": "username2",
                "password": "password2",
                "email": "email@sample.com",
                "sex": "f",
                "birthday": "2021-01-02",
            },
        )
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert response_json["username"] == "username2", response_json
        assert response_json["password"] != "password2", response_json
        assert response_json["email"] == "email@sample.com", response_json
        assert response_json["sex"] == "f", response_json
        assert response_json["birthday"] == "2021-01-02", response_json

    def test_change_password_user(self, general_client: TestClient, api_path: str):
        response = general_client.post(
            f"{api_path}/auth/token",
            data={"username": "username2", "password": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200, response.text
        response_json = response.json()
        token = response_json["access_token"]
        response = general_client.post(
            f"{api_path}/auth/reset-password/{token}",
            data={"new_password": "password3"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200, response.text
        response = general_client.post(
            f"{api_path}/auth/token",
            data={"username": "username2", "password": "password3"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
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

    def test_read_plan(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/plans/")
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert len(response_json) == 1, response_json
        assert response_json[0]["name"] == "テストプラン", response_json
