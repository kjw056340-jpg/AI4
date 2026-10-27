import importlib
import sys
from fastapi.testclient import TestClient

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
client = TestClient(importlib.import_module(name).app, raise_server_exceptions=False)
assert [t["id"] for t in client.get("/tasks").json()] == [1, 3]
created = client.post("/tasks", json={"title": "넷째"})
assert created.status_code == 201 and created.json()["id"] == 4
changed = client.put("/tasks/3", json={"title": "수정"})
assert changed.status_code == 200 and changed.json()["title"] == "수정"
removed = client.delete("/tasks/3")
print("DELETE /tasks/3:", removed.status_code)
assert removed.status_code == 204, "Task ID를 리스트 인덱스로 잘못 사용했을 수 있습니다"
ids = [t["id"] for t in client.get("/tasks").json()]
print("remaining IDs:", ids)
assert ids == [1, 4]
assert client.delete("/tasks/999").status_code == 404
print("PASS")
