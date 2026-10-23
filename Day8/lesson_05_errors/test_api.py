import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("product_id, status, expected", [
    (1, 200, {"id": 1, "name": "tea"}),
    (99, 404, {"detail": "Product not found"}),
])
def test_product(product_id, status, expected):
    response = client.get(f"/products/{product_id}")
    assert response.status_code == status
    assert response.json() == expected


@pytest.mark.parametrize("product_id", ["0", "abc"])
def test_product_invalid(product_id):
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "product_id"]


@pytest.mark.parametrize("status", ["200", "404", "422"])
def test_error_document(status):
    schema = client.get("/openapi.json").json()
    assert status in schema["paths"]["/products/{product_id}"]["get"]["responses"]
