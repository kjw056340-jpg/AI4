import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
f = importlib.import_module(name).summarize_changes
sample = [{"path": "main.py", "status": "modified"}, {"path": "old.py", "status": "deleted"}]
result = f(sample)
print(result)
assert result == {"changed": ["main.py", "old.py"]}
print("PASS")
