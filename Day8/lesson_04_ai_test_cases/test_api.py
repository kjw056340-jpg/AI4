import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("amount, discount, payable", [
    (1, 0, 1), (5000, 0, 5000), (9999, 0, 9999),
    (10000, 1000, 9000), (10001, 1000, 9001),
    (20000, 1000, 19000), (100000, 1000, 99000),
])
def test_quote(amount, discount, payable):
    response = client.post("/quotes", json={"amount": amount})
    assert response.status_code == 200
    assert response.json() == {"amount": amount, "discount": discount, "payable": payable}


@pytest.mark.parametrize("body", [{"amount": 0}, {"amount": 100001}, {"amount": "10000"}, {}])
def test_quote_invalid(body):
    response = client.post("/quotes", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "amount"]
