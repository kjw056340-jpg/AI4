import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("profile_id, status", [(1, 200), (99, 404), (0, 422)])
def test_profile(profile_id, status):
    response = client.get(f"/profiles/{profile_id}")
    assert response.status_code == status
    if status == 200:
        assert response.json() == {"id": 1, "name": "Min"}
        assert "internal_note" not in response.json()
    elif status == 404:
        assert response.json() == {"detail": "Profile not found"}
    else:
        assert response.json()["detail"][0]["loc"] == ["path", "profile_id"]


@pytest.mark.parametrize("path", ["/profiles/{profile_id}"])
def test_response_schema(path):
    schema = client.get("/openapi.json").json()
    response = schema["paths"][path]["get"]["responses"]["200"]
    assert response["content"]["application/json"]["schema"].get("$ref") == "#/components/schemas/ProfileOut"
    model = schema["components"]["schemas"]["ProfileOut"]
    assert set(model["properties"]) == {"id", "name"}
