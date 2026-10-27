import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
combine = importlib.import_module(name).combine_tasks
main_items = [{"id": 1, "title": "메인"}]
feature_items = [{"id": 2, "title": "기능"}]
result = combine(main_items, feature_items)
print(result)
assert [x["id"] for x in result] == [1, 2]
assert combine([{"id": 1, "title": "기존"}], [{"id": 1, "title": "기능 우선"}])[0]["title"] == "기능 우선"
print("PASS")
