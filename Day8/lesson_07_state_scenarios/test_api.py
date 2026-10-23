import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tasks():
    app.state.tasks.clear()
    yield
    app.state.tasks.clear()


@pytest.mark.parametrize("titles", [("read", "write"), ("same", "same")])
def test_two_tasks(titles):
    first = client.post("/tasks", json={"title": titles[0]})
    second = client.post("/tasks", json={"title": titles[1]})
    assert first.status_code == second.status_code == 201
    first_id = first.json()["id"]
    second_id = second.json()["id"]
    first_read = client.get(f"/tasks/{first_id}")
    second_read = client.get(f"/tasks/{second_id}")
    assert first_read.status_code == second_read.status_code == 200
    assert first_read.json() == first.json()
    assert second_read.json() == second.json()
    assert first_id > 0 and second_id > 0
    assert first_id != second_id


@pytest.mark.parametrize("body", [{"title": "one"}, {"title": "two"}])
def test_single_task(body):
    response = client.post("/tasks", json=body)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": body["title"]}


@pytest.mark.parametrize("task_id, status", [(99, 404), (0, 422)])
def test_missing_task(task_id, status):
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status
    if status == 404:
        assert response.json() == {"detail": "Task not found"}
    else:
        assert response.json()["detail"][0]["loc"] == ["path", "task_id"]


@pytest.mark.parametrize("body", [{}, {"title": ""}, {"title": "x" * 21}])
def test_invalid_task(body):
    response = client.post("/tasks", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]
    assert app.state.tasks == {}
