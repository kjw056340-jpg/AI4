import argparse
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=["main", "solution"])
    target = import_module(parser.parse_args().module)
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "check.db"
        target.create_database(db_path)
        checks = [
            ("empty_conversation_count_zero", target.conversation_summary(db_path, 1),
             [(10, "민지", "빈 대화", 0), (20, "민지", "파이썬", 2)]),
            ("other_user_summary", target.conversation_summary(db_path, 2), [(30, "준호", "SQL", 1)]),
            ("missing_user", target.conversation_summary(db_path, 999), []),
            ("ordered_history", target.message_history(db_path, 20), [(1, "user", "질문"), (2, "assistant", "답변")]),
            ("empty_history", target.message_history(db_path, 10), []),
            ("missing_history", target.message_history(db_path, 999), []),
            ("sql_text_is_value", target.conversation_summary(db_path, "1 OR 1=1"), []),
        ]
    failures = 0
    for name, actual, expected in checks:
        passed = actual == expected
        print(f"{'PASS' if passed else 'FAIL'} {name}: actual={actual}; expected={expected}")
        failures += int(not passed)
    print(f"RESULT failures={failures}")
    raise SystemExit(1 if failures else 0)
