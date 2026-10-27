"""매 사례에 새 DB를 만들어 전체 성공·실패 뒤 데이터 상태를 검사한다."""
import argparse
from importlib import import_module
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=["main", "solution"])
    args = parser.parse_args()
    target = import_module(args.module)
    original = [(1, "민지", 80), (2, "준호", 95), (3, "수아", 70)]
    cases = [
        ("normal_commit", 1, 90, 3, None, [(1, "민지", 90), (2, "준호", 95)]),
        ("missing_delete_rolls_back_update", 1, 90, 999, ValueError, original),
        ("missing_update_preserves_all", 999, 90, 3, ValueError, original),
        ("null_points_rejected", 1, None, 3, sqlite3.IntegrityError, original),
        ("zero_points_is_valid", 1, 0, 3, None, [(1, "민지", 0), (2, "준호", 95)]),
        ("different_delete_target", 1, 90, 2, None, [(1, "민지", 90), (3, "수아", 70)]),
    ]
    failures = 0
    with TemporaryDirectory() as folder:
        for index, (name, update_id, points, delete_id, expected_error, expected_rows) in enumerate(cases):
            db_path = Path(folder) / f"case_{index}.db"
            target.prepare_database(db_path)
            actual_error = None
            counts = None
            try:
                counts = target.apply_changes(db_path, update_id, points, delete_id)
            except (ValueError, sqlite3.Error) as exc:
                actual_error = type(exc)
            actual_rows = target.read_users(db_path)
            passed = actual_error is expected_error and actual_rows == expected_rows
            if expected_error is None:
                passed = passed and counts == (1, 1)
            print(f"{'PASS' if passed else 'FAIL'} {name}")
            print(f"  expected={expected_rows}")
            print(f"  actual={actual_rows}; error={actual_error}; counts={counts}")
            failures += int(not passed)
    print(f"RESULT failures={failures}")
    raise SystemExit(1 if failures else 0)
