from fastapi.testclient import TestClient


def test_create_and_read(client: TestClient):
    response = client.post(
        "/notices/",
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

    response = client.get("/notices/")
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert len(response_json) == 2, response_json
