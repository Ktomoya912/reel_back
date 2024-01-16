from fastapi.testclient import TestClient


class TestJob:
    def test_create_job(self, admin_client: TestClient, api_path: str):
        response = admin_client.post(
            f"{api_path}/jobs/",
            json={
                "name": "テスト求人",
                "salary": "時給1000円",
                "postal_code": "782-8502",
                "prefecture": "高知県",
                "city": "香美市",
                "address": "土佐山田町宮ノ口185",
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
        assert response.json()["status"] == "active"

    def test_get_jobs(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/jobs/")
        assert response.status_code == 200, response.text
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "テスト求人"

    def test_get_job(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(f"{api_path}/jobs/1")
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "テスト求人"

    def test_update_job(self, admin_client: TestClient, api_path: str):
        response = admin_client.put(
            f"{api_path}/jobs/1",
            json={
                "name": "テスト求人1",
                "salary": "時給1000円",
                "postal_code": "782-8502",
                "prefecture": "高知県",
                "city": "香美市",
                "address": "土佐山田町宮ノ口185",
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

    def test_post_job_review(self, admin_client: TestClient, api_path: str):
        response = admin_client.post(
            f"{api_path}/jobs/1/review",
            json={"title": "タイトル", "review": "レビュー", "review_point": 5},
        )
        assert response.status_code == 200, f"1. {response.text}"
        assert response.json()["review_point"] == 5, f"2. {response.text}"
        assert response.json()["title"] == "タイトル", f"1. {response.text}"
        assert response.json()["review"] == "レビュー", f"1. {response.text}"

    def test_apply_job(self, admin_client: TestClient, api_path: str):
        response = admin_client.post(f"{api_path}/jobs/1/apply")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "p"

    def test_get_applications(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(f"{api_path}/jobs/1/application")
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2
        assert response.json()["job_id"] == 1
        assert response.json()["users"][0]["user_id"] == 1

    def test_bookmark_job(self, general_client: TestClient, api_path: str):
        response = general_client.put(f"{api_path}/jobs/1/bookmark")
        assert response.status_code == 200, response.text
        assert response.json() is True
        response = general_client.put(f"{api_path}/jobs/1/bookmark")
        assert response.status_code == 200, response.text
        assert response.json() is False

    def test_delete_job(self, admin_client: TestClient, api_path: str):
        response = admin_client.delete(f"{api_path}/jobs/1")
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Job deleted"}
        response = admin_client.get(f"{api_path}/users/1")
        assert response.json() != {}, response.json()
