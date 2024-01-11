from fastapi.testclient import TestClient


class TestJob:
    def test_create_job(self, company_client: TestClient, api_path: str):
        response = company_client.post(
            f"{api_path}/jobs/",
            json={
                "name": "テスト求人",
                "salary": "時給1000円",
                "working_location": "高知県香美市",
                "description": "説明",
                "is_one_day": True,
                "additional_message": "追加メッセージ",
                "image_url": "https://example.com",
                "tags": [{"name": "タグ"}],
                "job_times": [
                    {
                        "start_time": "2024-01-11 10:00:00",
                        "end_time": "2024-01-11 18:00:00",
                    }
                ],
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "テスト求人"

    def test_activate_job(
        self, company_client: TestClient, admin_client: TestClient, api_path: str
    ):
        response = company_client.put(f"{api_path}/jobs/1/activate")
        assert response.status_code == 400, response.text
        response = admin_client.put(f"{api_path}/jobs/1/activate")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "1"

    def test_get_jobs(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/jobs/")
        assert response.status_code == 200, response.text
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "テスト求人"

    def test_update_job(self, company_client: TestClient, api_path: str):
        response = company_client.put(
            f"{api_path}/jobs/1",
            json={
                "name": "テスト求人1",
                "salary": "時給1000円",
                "working_location": "高知県香美市",
                "description": "説明",
                "is_one_day": True,
                "additional_message": "追加メッセージ",
                "image_url": "https://example.com",
                "tags": [{"name": "タグ"}],
                "job_times": [
                    {
                        "start_time": "2024-01-11 10:00:00",
                        "end_time": "2024-01-11 18:00:00",
                    }
                ],
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "テスト求人1"

    def test_delete_job(self, company_client: TestClient, api_path: str):
        response = company_client.delete(f"{api_path}/jobs/1")
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Deleted successfully"}
