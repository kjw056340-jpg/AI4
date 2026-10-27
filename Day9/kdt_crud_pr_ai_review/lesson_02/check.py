from fastapi.testclient import TestClient
import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
client = TestClient(importlib.import_module(name).app)
found = client.get("/tasks/1")
missing = client.get("/tasks/999")
print("existing:", found.status_code, found.json())
print("missing:", missing.status_code, missing.json())
assert found.status_code == 200 and found.json()["id"] == 1
assert missing.status_code == 404
assert missing.json()["detail"] == "Task not found"
print("PASS")
