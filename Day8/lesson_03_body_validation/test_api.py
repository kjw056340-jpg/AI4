import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("quantity", [1, 5])
def test_order_valid(quantity):
    response = client.post("/orders", json={"name": "tea", "quantity": quantity})
    assert response.status_code == 201
    assert response.json() == {"name": "tea", "quantity": quantity, "total": quantity * 3000}


@pytest.mark.parametrize("body, field", [
    ({"name": "tea", "quantity": 0}, "quantity"),
    ({"name": "tea", "quantity": 6}, "quantity"),
    ({"name": "tea", "quantity": "2"}, "quantity"),
    ({"name": "tea", "quantity": True}, "quantity"),
    ({"name": "tea", "quantity": None}, "quantity"),
    ({"name": "tea"}, "quantity"),
    ({"quantity": 1}, "name"),
    ({"name": "", "quantity": 1}, "name"),
    ({"name": "x" * 21, "quantity": 1}, "name"),
    ({"name": "tea", "quantity": 1, "admin": True}, "admin"),
])
def test_order_invalid(body, field):
    response = client.post("/orders", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]


@pytest.mark.parametrize("field, minimum", [("quantity", 1)])
def test_order_schema(field, minimum):
    schema = client.get("/openapi.json").json()
    model = schema["components"]["schemas"]["OrderIn"]
    assert model["properties"][field]["minimum"] == minimum
    assert set(model["required"]) == {"name", "quantity"}
    assert model["additionalProperties"] is False
