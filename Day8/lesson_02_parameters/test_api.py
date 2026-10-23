import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("params, qty", [({}, 1), ({"qty": 1}, 1), ({"qty": 5}, 5)])
def test_valid_quantity(params, qty):
    response = client.get("/items/1", params=params)
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "qty": qty, "total": qty * 1000}


@pytest.mark.parametrize("url, field", [
    ("/items/0", "item_id"), ("/items/abc", "item_id"),
    ("/items/1?qty=0", "qty"), ("/items/1?qty=6", "qty"),
    ("/items/1?qty=abc", "qty"),
])
def test_invalid_quantity(url, field):
    response = client.get(url)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == field


@pytest.mark.parametrize("field, default", [("qty", 1)])
def test_document_default(field, default):
    schema = client.get("/openapi.json").json()
    parameters = schema["paths"]["/items/{item_id}"]["get"]["parameters"]
    parameter = next(p for p in parameters if p["name"] == field)
    assert parameter["in"] == "query"
    assert parameter["required"] is False
    assert parameter["schema"]["default"] == default
    assert parameter["schema"]["minimum"] == 1
    assert parameter["schema"]["maximum"] == 5
