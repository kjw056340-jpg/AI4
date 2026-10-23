from main import app

import pytest
from fastapi.testclient import TestClient


# Expected values come from the business contract, not calculate_discount().
# Each case independently sends one POST /quotes; no persisted state is needed.
@pytest.mark.parametrize(
    "request_kwargs, expected_status, expected_body",
    [
        pytest.param({"json": {"amount": 5000}}, 200,
                     {"amount": 5000, "discount": 0, "payable": 5000}, id="N01"),
        pytest.param({"json": {"amount": 20000}}, 200,
                     {"amount": 20000, "discount": 1000, "payable": 19000}, id="N02"),
        pytest.param({"json": {"amount": 1}}, 200,
                     {"amount": 1, "discount": 0, "payable": 1}, id="L01"),
        pytest.param({"json": {"amount": 100000}}, 200,
                     {"amount": 100000, "discount": 1000, "payable": 99000}, id="L02"),
        pytest.param({"json": {"amount": 9999}}, 200,
                     {"amount": 9999, "discount": 0, "payable": 9999}, id="R01"),
        pytest.param({"json": {"amount": 10000}}, 200,
                     {"amount": 10000, "discount": 1000, "payable": 9000}, id="R02"),
        pytest.param({"json": {"amount": 10001}}, 200,
                     {"amount": 10001, "discount": 1000, "payable": 9001}, id="R03"),
        pytest.param({"json": {"amount": 0}}, 422, None, id="B01"),
        pytest.param({"json": {"amount": 100001}}, 422, None, id="B02"),
        pytest.param({"json": {}}, 422, None, id="M01"),
        pytest.param({}, 422, None, id="M02"),
        pytest.param({"json": {"amount": "10000"}}, 422, None, id="T01"),
        pytest.param({"json": {"amount": 10000.0}}, 422, None, id="T02"),
        pytest.param({"json": {"amount": 1.5}}, 422, None, id="T03"),
        pytest.param({"json": {"amount": True}}, 422, None, id="T04"),
        pytest.param({"json": {"amount": False}}, 422, None, id="T05"),
        pytest.param({"json": {"amount": None}}, 422, None, id="T06"),
        pytest.param({"json": {"amount": []}}, 422, None, id="T07"),
        pytest.param({"json": {"amount": {}}}, 422, None, id="T08"),
    ],
)
def test_quotes_contract(request_kwargs, expected_status, expected_body):
    with TestClient(app) as client:
        response = client.post("/quotes", **request_kwargs)

    assert response.status_code == expected_status, response.text
    if expected_status == 200:
        actual = response.json()
        assert actual == expected_body
        # JSON numeric equality alone would accept floats or booleans as ints.
        assert all(type(actual[field]) is int for field in expected_body)
    # The contract specifies 422 but does not fix the error body's structure.
