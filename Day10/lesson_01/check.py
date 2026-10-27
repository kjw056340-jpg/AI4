"""임시 DB 파일을 사용해 실제 저장·재연결·잘못된 입력 거절을 확인한다."""
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
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "check.db"
        inside = target.save_user(db_path, "민지")
        first_saved = target.read_users(db_path)
        literal_inside = target.save_user(db_path, "O'Neil")
        second_saved = target.read_users(db_path)
        rejected = False
        try:
            target.save_user(db_path, None)
        except sqlite3.IntegrityError:
            rejected = True
        after_error = target.read_users(db_path)
        checks = [
            ("visible_before_close", inside == [(1, "민지")]),
            ("saved_after_reconnect", first_saved == [(1, "민지")]),
            ("quote_in_name_preserved", any(row[1] == "O'Neil" for row in literal_inside)),
            ("both_rows_saved", second_saved == [(1, "민지"), (2, "O'Neil")]),
            ("null_rejected", rejected),
            ("existing_rows_preserved_on_error", after_error == second_saved),
        ]
        print("INSIDE:", inside)
        print("REOPENED:", first_saved)
        print("SECOND REOPENED:", second_saved)
        failures = 0
        for name, passed in checks:
            print(f"{'PASS' if passed else 'FAIL'} {name}")
            failures += int(not passed)
        print(f"RESULT failures={failures}")
        raise SystemExit(1 if failures else 0)
