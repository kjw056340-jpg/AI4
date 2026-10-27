import argparse
from importlib import import_module
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=["main", "solution"])
    target = import_module(parser.parse_args().module)
    cases = [
        ("normal", (2, "수아", "sua@example.test", 50), False),
        ("zero", (2, "수아", "sua@example.test", 0), False),
        ("hundred", (2, "수아", "sua@example.test", 100), False),
        ("null_points", (2, "수아", "sua@example.test", None), True),
        ("negative", (2, "수아", "sua@example.test", -1), True),
        ("above_hundred", (2, "수아", "sua@example.test", 101), True),
        ("duplicate_id", (1, "수아", "sua@example.test", 50), True),
        ("duplicate_email", (2, "수아", "minji@example.test", 50), True),
        ("null_name", (2, None, "sua@example.test", 50), True),
        ("null_email", (2, "수아", None, 50), True),
    ]
    failures = 0
    with TemporaryDirectory() as folder:
        for index, (name, values, expected_rejection) in enumerate(cases):
            db_path = Path(folder) / f"case{index}.db"
            target.create_database(db_path)
            target.add_user(db_path, 1, "민지", "minji@example.test", 80)
            before = target.read_users(db_path)
            rejected = False
            try:
                target.add_user(db_path, *values)
            except sqlite3.IntegrityError:
                rejected = True
            after = target.read_users(db_path)
            expected = before if expected_rejection else before + [values]
            passed = rejected == expected_rejection and after == expected
            print(f"{'PASS' if passed else 'FAIL'} {name}: rejected={rejected}; rows={after}")
            failures += int(not passed)
    print(f"RESULT failures={failures}")
    raise SystemExit(1 if failures else 0)
