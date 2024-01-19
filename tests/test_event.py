from fastapi.testclient import TestClient

CREATE_EVENT = {
    "name": "イベント名",
    "image_url": "https://example.com",
    "postal_code": "782-8502",
    "prefecture": "高知県",
    "city": "香美市",
    "address": "土佐山田町宮ノ口185",
    "phone_number": "0887-53-1111",
    "email": "sample@ugs.ac.jp",
    "homepage": "https://kochi-tech.ac.jp/",
    "participation_fee": "無料",
    "caution": "注意事項",
    "capacity": 100,
    "additional_message": "",
    "description": "",
    "tags": [{"name": "タグ名"}],
    "event_times": [
        {
            "start_time": "2024-01-12 14:26:22",
            "end_time": "2024-01-12 15:26:22",
        }
    ],
}


class TestEvent:
    def test_create_event(
        self, company_client: TestClient, api_path: str, admin_client: TestClient
    ):
        response = admin_client.post(
            f"{api_path}/events/",
            json=CREATE_EVENT,
        )
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "イベント名"

    def test_activate_event(
        self, company_client: TestClient, admin_client: TestClient, api_path: str
    ):
        response = admin_client.put(
            f"{api_path}/events/1/change-status", params={"status": "active"}
        )
        assert response.status_code == 200, response.text
        response = company_client.put(
            f"{api_path}/events/1/change-status", params={"status": "active"}
        )
        assert response.status_code == 400, response.text

    def test_get_events(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/events/")
        assert response.status_code == 200, response.text
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "イベント名"

    def test_get_event(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(f"{api_path}/events/1")
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "イベント名"

    def test_update_event(
        self, company_client: TestClient, api_path: str, admin_client: TestClient
    ):
        response = admin_client.put(
            f"{api_path}/events/1",
            json={
                "name": "イベント名1",
                "image_url": "https://example.com",
                "postal_code": "782-8502",
                "prefecture": "高知県",
                "city": "香美市",
                "address": "土佐山田町宮ノ口185",
                "phone_number": "0887-53-1111",
                "email": "sample@ugs.ac.jp",
                "homepage": "https://kochi-tech.ac.jp/",
                "participation_fee": "無料",
                "capacity": 100,
                "caution": "注意事項",
                "additional_message": "",
                "description": "",
                "tags": [{"name": "タグ名"}],
                "event_times": [
                    {
                        "start_time": "2024-01-12 14:26:22",
                        "end_time": "2024-01-12 15:26:22",
                    }
                ],
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "イベント名1"

    def test_post_event_review(self, admin_client: TestClient, api_path: str):
        response = admin_client.post(
            f"{api_path}/events/1/review",
            json={"title": "タイトル", "review": "レビュー", "review_point": 5},
        )
        assert response.status_code == 200, f"1. {response.text}"
        assert response.json()["review_point"] == 5, f"2. {response.text}"
        assert response.json()["title"] == "タイトル", f"1. {response.text}"
        assert response.json()["review"] == "レビュー", f"1. {response.text}"

    def test_bookmark_event(self, general_client: TestClient, api_path: str):
        response = general_client.put(f"{api_path}/events/1/bookmark")
        assert response.status_code == 200, response.text
        assert response.json() is True
        response = general_client.put(f"{api_path}/events/1/bookmark")
        assert response.status_code == 200, response.text
        assert response.json() is False

    def test_delete_event(self, admin_client: TestClient, api_path: str):
        response = admin_client.delete(f"{api_path}/events/1")
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Event Deleted"}
        response = admin_client.get(f"{api_path}/users/1")
        assert response.json() != {}, response.json()

    def test_create_many_events(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(f"{api_path}/events/")
        assert response.status_code == 200, response.text
        assert len(response.json()) == 0
        for i in range(30):
            data = CREATE_EVENT.copy()
            data["name"] = f"テスト求人{i}"
            response = admin_client.post(f"{api_path}/events/", json=data)
            assert response.status_code == 200, response.text
            assert response.json()["name"] == f"テスト求人{i}"

    def test_change_event_status(self, admin_client: TestClient, api_path: str):
        status_list = ["active", "inactive", "draft"]
        for i in range(30):
            response = admin_client.put(
                f"{api_path}/events/{i+1}/change-status",
                params={"status": status_list[i % 3]},
            )
            assert response.status_code == 200, response.text
            assert response.json()["status"] == status_list[i % 3]

    def test_get_events_with_status(self, general_client: TestClient, api_path: str):
        response = general_client.get(
            f"{api_path}/events/", params={"status": "active"}
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10, 1
        response = general_client.get(
            f"{api_path}/events/", params={"status": "inactive"}
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10, 2
        response = general_client.get(f"{api_path}/events/", params={"status": "draft"})
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10, 3
        response = general_client.get(f"{api_path}/events/", params={"status": "all"})
        assert response.status_code == 200, response.text
        assert len(response.json()) == 30

    def test_favorite_event(self, admin_client: TestClient, api_path: str):
        for i in range(30):
            if i % 2 == 0:
                response = admin_client.put(f"{api_path}/events/{i+1}/bookmark")
                assert response.status_code == 200, response.text
                assert response.json() is True

    def test_get_all_favorite_events(self, general_client: TestClient, api_path: str):
        response = general_client.get(
            f"{api_path}/events/", params={"user_id": 1, "target": "favorite"}
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 15

    def test_read_event_detail(self, admin_client: TestClient, api_path: str):
        for i in range(30):
            if i % 5 == 0:
                response = admin_client.get(f"{api_path}/events/{i+1}")
                assert response.status_code == 200, response.text
                assert response.json() != {}

    def test_get_event_history(self, admin_client: TestClient, api_path: str):
        response = admin_client.get(
            f"{api_path}/events/", params={"user_id": 1, "target": "history"}
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 6

    def test_get_event_history_with_status(
        self, admin_client: TestClient, api_path: str
    ):
        response = admin_client.get(
            f"{api_path}/events/",
            params={"user_id": 1, "target": "history", "status": "active"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2
        response = admin_client.get(
            f"{api_path}/events/",
            params={"user_id": 1, "target": "history", "status": "inactive"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2
        response = admin_client.get(
            f"{api_path}/events/",
            params={"user_id": 1, "target": "history", "status": "draft"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2
        response = admin_client.get(
            f"{api_path}/events/",
            params={"user_id": 1, "target": "history", "status": "all"},
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 6
