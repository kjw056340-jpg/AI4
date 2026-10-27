import importlib
import sys
from fastapi.testclient import TestClient

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
client = TestClient(importlib.import_module(name).app)
put = client.put("/tasks/1", json={"title": "완전교체", "done": True})
print("PUT:", put.status_code, put.json())
assert put.status_code == 200 and put.json()["done"] is True
invalid = client.put("/tasks/1", json={"title": "누락"})
print("PUT invalid:", invalid.status_code)
assert invalid.status_code == 422
patch = client.patch("/tasks/1", json={"title": "제목만"})
print("PATCH:", patch.status_code, patch.json())
assert patch.status_code == 200 and patch.json()["title"] == "제목만"
assert patch.json()["done"] is True, "PATCH가 지정하지 않은 done을 변경했습니다"
print("PASS")
