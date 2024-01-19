from fastapi.testclient import TestClient

CREATE_JOB = {
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
}


class TestJob:
    def test_create_job(self, admin_client: TestClient, api_path: str):
        response = admin_client.post(f"{api_path}/jobs/", json=CREATE_JOB)
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "テスト求人"

    def test_activate_job(
        self, company_client: TestClient, admin_client: TestClient, api_path: str
    ):
        response = admin_client.put(
            f"{api_path}/jobs/1/change-status", params={"status": "active"}
        )
        assert response.status_code == 200, response.text
        response = company_client.put(
            f"{api_path}/jobs/1/change-status", params={"status": "active"}
        )
        assert response.status_code == 400, response.text

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

    def test_create_many_jobs(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(f"{api_path}/jobs/")
        assert response.status_code == 200, response.text
        assert len(response.json()) == 0
        for i in range(30):
            data = CREATE_JOB.copy()
            data["name"] = f"テスト求人{i}"
            response = admin_client.post(f"{api_path}/jobs/", json=data)
            assert response.status_code == 200, response.text
            assert response.json()["name"] == f"テスト求人{i}"

    def test_change_job_status(self, admin_client: TestClient, api_path: str):
        status_list = ["active", "inactive", "draft"]
        for i in range(30):
            response = admin_client.put(
                f"{api_path}/jobs/{i+1}/change-status",
                params={"status": status_list[i % 3]},
            )
            assert response.status_code == 200, response.text
            assert response.json()["status"] == status_list[i % 3]

    def test_get_jobs_with_status(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/jobs/", params={"status": "active"})
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10, 1
        response = general_client.get(
            f"{api_path}/jobs/", params={"status": "inactive"}
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10, 2
        response = general_client.get(f"{api_path}/jobs/", params={"status": "draft"})
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10, 3
        response = general_client.get(f"{api_path}/jobs/", params={"status": "all"})
        assert response.status_code == 200, response.text
        assert len(response.json()) == 30

    def test_favorite_job(self, admin_client: TestClient, api_path: str):
        for i in range(30):
            if i % 2 == 0:
                response = admin_client.put(f"{api_path}/jobs/{i+1}/bookmark")
                assert response.status_code == 200, response.text
                assert response.json() is True

    def test_get_all_favorite_jobs(self, general_client: TestClient, api_path: str):
        response = general_client.get(
            f"{api_path}/jobs/", params={"user_id": 1, "target": "favorite"}
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 15

    def test_read_job_detail(self, admin_client: TestClient, api_path: str):
        for i in range(30):
            if i % 5 == 0:
                response = admin_client.get(f"{api_path}/jobs/{i+1}")
                assert response.status_code == 200, response.text
                assert response.json() != {}

    def test_get_job_history(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(
            f"{api_path}/jobs/", params={"user_id": 1, "target": "history"}
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 6

    def test_get_job_history_with_status(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(
            f"{api_path}/jobs/",
            params={"user_id": 1, "target": "history", "status": "active"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2
        response = admin_client.get(
            f"{api_path}/jobs/",
            params={"user_id": 1, "target": "history", "status": "inactive"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2
        response = admin_client.get(
            f"{api_path}/jobs/",
            params={"user_id": 1, "target": "history", "status": "draft"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2
        response = admin_client.get(
            f"{api_path}/jobs/",
            params={"user_id": 1, "target": "history", "status": "all"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 6

    def test_create_user_and_review(self, general_client: TestClient, api_path: str):
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
        response = general_client.post(
            f"{api_path}/auth/token",
            data={"username": "username", "password": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200, response.text
        response_json = response.json()
        token = response_json["access_token"]
        response = general_client.post(
            f"{api_path}/jobs/1/review",
            json={"title": "タイトル", "review": "レビュー", "review_point": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text

    def test_delete_user_and_detail(self, admin_client: TestClient, api_path: str):
        response = admin_client.delete(f"{api_path}/users/2")
        assert response.status_code == 200, response.text
        response = admin_client.get(f"{api_path}/jobs/1")
        assert response.json() != {}, response.json()
