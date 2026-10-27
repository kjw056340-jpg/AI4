import argparse
from importlib import import_module
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=["main", "solution"])
    target = import_module(parser.parse_args().module)
    failures = 0
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "check.db"
        target.create_database(db_path)
        first_ids = target.save_turn(db_path, 1, 1, "질문 A", "답변 A")
        target.save_turn(db_path, 2, 2, "질문 B", "답변 B")
        checks = [
            ("own_history_a", target.list_history(db_path, 1, 1) == [(1, "user", "질문 A"), (2, "assistant", "답변 A")]),
            ("own_history_b", target.list_history(db_path, 2, 2) == [(3, "user", "질문 B"), (4, "assistant", "답변 B")]),
            ("cross_read_a_denied", target.list_history(db_path, 2, 1) == []),
            ("cross_read_b_denied", target.list_history(db_path, 1, 2) == []),
            ("missing_conversation", target.list_history(db_path, 1, 999) == []),
            ("saved_ids", first_ids == (1, 2)),
        ]
        for name, passed in checks:
            print(f"{'PASS' if passed else 'FAIL'} {name}")
            failures += int(not passed)
        for name, user_id, conversation_id, question, answer, expected_error in [
            ("cross_write_denied", 2, 1, "타인 질문", "타인 답변", ValueError),
            ("empty_answer_rolls_back_both", 1, 1, "새 질문", "   ", sqlite3.IntegrityError),
            ("null_answer_rolls_back_both", 1, 1, "새 질문", None, sqlite3.IntegrityError),
        ]:
            before = target.list_history(db_path, 1, 1)
            rejected = False
            try:
                target.save_turn(db_path, user_id, conversation_id, question, answer)
            except expected_error:
                rejected = True
            passed = rejected and target.list_history(db_path, 1, 1) == before
            print(f"{'PASS' if passed else 'FAIL'} {name}")
            failures += int(not passed)
        target.save_turn(db_path, 1, 1, "O'Neil 질문", "따옴표 답변")
        history = target.list_history(db_path, 1, 1)
        passed = [(row[1], row[2]) for row in history] == [
            ("user", "질문 A"), ("assistant", "답변 A"),
            ("user", "O'Neil 질문"), ("assistant", "따옴표 답변"),
        ] and [row[0] for row in history] == sorted(row[0] for row in history)
        print(f"{'PASS' if passed else 'FAIL'} quote_and_chronological_order")
        failures += int(not passed)
    print(f"RESULT failures={failures}")
    raise SystemExit(1 if failures else 0)
