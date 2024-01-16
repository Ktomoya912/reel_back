from fastapi.testclient import TestClient

MESSAGE = {
    "title": "this is message",
    "message": "string",
    "type": "J",
    "user_list": [2],
}


class TestMessage:
    def test_create1(self, general_client: TestClient, api_path: str):
        response = general_client.post(
            f"{api_path}/notices/",
            json=MESSAGE,
        )
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert response_json["title"] == "this is message", response_json

    def test_create2(self, general_client: TestClient, api_path: str):
        MESSAGE["type"] = "E"
        MESSAGE["title"] = "this is not message"
        response = general_client.post(
            f"{api_path}/notices/",
            json=MESSAGE,
        )
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert response_json["title"] == "this is not message", response_json

    def test_read(self, general_client: TestClient, api_path: str):
        response = general_client.get(f"{api_path}/notices/")
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert len(response_json) == 2, response_json
        assert response_json[1][0]["title"] == "this is message", response_json
        assert response_json[0][0]["title"] == "this is not message", response_json

    def test_read2(self, general_client: TestClient, api_path: str):
        response = general_client.post(
            f"{api_path}/notices/1/read",
        )
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert response_json["title"] == "this is message", response_json

        response = general_client.get(f"{api_path}/notices/")
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert len(response_json) == 2, response_json
        assert response_json[1] == [], response_json
