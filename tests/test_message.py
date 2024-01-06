from fastapi.testclient import TestClient


def test_create_and_read(general_client: TestClient, api_path: str):
    response = general_client.post(
        f"{api_path}/notices/",
        json={
            "title": "this is message",
            "message": "string",
            "type": "J",
            "user_list": [1],
        },
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json["title"] == "this is message", response_json

    response = general_client.get(f"{api_path}/notices/")
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert len(response_json) == 2, response_json
