"""도시·정렬·상한·0·오류 입력을 실제 임시 DB 파일에서 비교한다."""
import argparse
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=["main", "solution"])
    args = parser.parse_args()
    target = import_module(args.module)
    cases = [
        ("seoul_two", "서울", 2, [3, 5]),
        ("seoul_one", "서울", 1, [3]),
        ("seoul_all", "서울", 10, [3, 5, 1, 6]),
        ("busan", "부산", 2, [2]),
        ("daejeon", "대전", 2, [4]),
        ("no_match", "제주", 2, []),
        ("sql_text_is_a_value", "서울' OR 1=1 --", 10, []),
        ("zero_means_zero", "서울", 0, []),
    ]
    failures = 0
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "check.db"
        target.prepare_database(db_path)
        for name, city, limit, expected in cases:
            rows = target.find_users(db_path, city, limit)
            actual = [row[0] for row in rows]
            passed = actual == expected and all(len(row) == 4 and row[2] == city for row in rows)
            print(f"{'PASS' if passed else 'FAIL'} {name}: expected={expected}, actual={actual}")
            failures += int(not passed)
        try:
            target.find_users(db_path, "서울", -1)
        except ValueError:
            print("PASS negative_limit_rejected")
        else:
            print("FAIL negative_limit_rejected")
            failures += 1
        before = target.find_users(db_path, "서울", 10)
        target.prepare_database(db_path)
        after = target.find_users(db_path, "서울", 10)
        passed = before == after and after[-1][1] == "O'Neil"
        print(f"{'PASS' if passed else 'FAIL'} repeat_prepare_preserves_rows_and_quote")
        failures += int(not passed)
    print(f"RESULT failures={failures}")
    raise SystemExit(1 if failures else 0)
