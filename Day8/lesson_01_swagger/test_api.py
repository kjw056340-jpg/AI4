import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("name, expected", [(None, "Hello, guest!"), ("Min", "Hello, Min!")])
def test_greet(name, expected):
    params = {} if name is None else {"name": name}
    response = client.get("/greet", params=params)
    assert response.status_code == 200
    assert response.json() == {"message": expected}


@pytest.mark.parametrize("url", ["/docs", "/openapi.json"])
def test_document_transport(url):
    response = client.get(url)
    assert response.status_code == 200
    if url == "/docs":
        assert "swagger-ui" in response.text.lower()
    else:
        assert "/greet" in response.json()["paths"]
