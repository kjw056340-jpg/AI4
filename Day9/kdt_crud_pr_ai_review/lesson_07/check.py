import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
can_edit = importlib.import_module(name).can_edit
print('admin:', can_edit('admin'))
print('not-admin:', can_edit('not-admin'))
assert can_edit('admin') is True
assert can_edit('not-admin') is False
assert can_edit('viewer') is False
print('PASS')
