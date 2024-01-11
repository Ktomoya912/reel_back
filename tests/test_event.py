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
    def test_create_event(self, company_client: TestClient, api_path: str):
        response = company_client.post(
            f"{api_path}/events/",
            json=CREATE_EVENT,
        )
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "イベント名"

    def test_activate_event(
        self, company_client: TestClient, admin_client: TestClient, api_path: str
    ):
        response = company_client.put(f"{api_path}/events/1/activate")
        assert response.status_code == 400, response.text
        response = admin_client.put(f"{api_path}/events/1/activate")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "1"

    def test_get_events(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/events/")
        assert response.status_code == 200, response.text
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "イベント名"

    def test_update_event(self, company_client: TestClient, api_path: str):
        response = company_client.put(
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

    def test_delete_event(self, company_client: TestClient, api_path: str):
        response = company_client.delete(f"{api_path}/events/1")
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Deleted successfully"}
