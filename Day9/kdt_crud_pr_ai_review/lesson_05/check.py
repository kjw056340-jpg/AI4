import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
ready = importlib.import_module(name).is_ready
print('true:', ready('true'))
print('false:', ready('false'))
assert ready('true') is True
assert ready('false') is False
print('PASS')
