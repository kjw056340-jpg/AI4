import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_reservations():
    app.state.remaining = 4
    app.state.reservations.clear()
    yield
    app.state.remaining = 4
    app.state.reservations.clear()


@pytest.mark.parametrize("seats", [1, 4])
def test_create_and_read(seats):
    response = client.post("/reservations", json={"name": "Min", "seats": seats})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Min", "seats": seats, "remaining": 4 - seats}
    read = client.get("/reservations/1")
    assert read.status_code == 200
    assert read.json() == {"id": 1, "name": "Min", "seats": seats}


@pytest.mark.parametrize("first_seats, rejected_seats, final_seats", [(3, 2, 1), (2, 3, 2)])
def test_reject_then_success(first_seats, rejected_seats, final_seats):
    first = client.post("/reservations", json={"name": "A", "seats": first_seats})
    rejected = client.post("/reservations", json={"name": "B", "seats": rejected_seats})
    final = client.post("/reservations", json={"name": "C", "seats": final_seats})
    first_read = client.get("/reservations/1")
    second_read = client.get("/reservations/2")
    assert first.status_code == 201
    assert rejected.status_code == 409
    assert rejected.json() == {"detail": "Not enough seats"}
    assert final.status_code == 201
    assert final.json() == {"id": 2, "name": "C", "seats": final_seats, "remaining": 0}
    assert first_read.json() == {"id": 1, "name": "A", "seats": first_seats}
    assert second_read.status_code == 200
    assert second_read.json() == {"id": 2, "name": "C", "seats": final_seats}


@pytest.mark.parametrize("body, field", [
    ({"name": "A", "seats": 0}, "seats"),
    ({"name": "A", "seats": 5}, "seats"),
    ({"name": "A", "seats": "1"}, "seats"),
    ({"name": "A", "seats": True}, "seats"),
    ({"name": "A"}, "seats"),
    ({"name": "", "seats": 1}, "name"),
    ({"name": "A", "seats": 1, "vip": True}, "vip"),
])
def test_invalid_keeps_state(body, field):
    response = client.post("/reservations", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]
    assert app.state.remaining == 4
    assert app.state.reservations == {}


@pytest.mark.parametrize("reservation_id, status", [(99, 404), (0, 422)])
def test_read_error(reservation_id, status):
    response = client.get(f"/reservations/{reservation_id}")
    assert response.status_code == status
    if status == 404:
        assert response.json() == {"detail": "Reservation not found"}
    else:
        assert response.json()["detail"][0]["loc"] == ["path", "reservation_id"]


@pytest.mark.parametrize("path, method, status", [
    ("/reservations", "post", "409"),
    ("/reservations/{reservation_id}", "get", "404"),
])
def test_final_document(path, method, status):
    schema = client.get("/openapi.json").json()
    assert status in schema["paths"][path][method]["responses"]
    model = schema["components"]["schemas"]["ReservationIn"]
    assert model["properties"]["seats"]["minimum"] == 1
    assert model["properties"]["seats"]["maximum"] == 4
