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
        ("one_user_many_conversations", [(1, "민지")], [(10, 1, "A"), (20, 1, "B")],
         [(1, 10, "user", "질문 A"), (2, 20, "user", "질문 B")], False, (1, 2, 2)),
        ("different_users", [(1, "민지"), (2, "준호")], [(10, 1, "A"), (20, 2, "B")], [], False, (2, 2, 0)),
        ("many_messages", [(1, "민지")], [(10, 1, "A")],
         [(1, 10, "user", "질문"), (2, 10, "assistant", "답변")], False, (1, 1, 2)),
        ("same_display_name", [(1, "민지"), (2, "민지")], [], [], False, (2, 0, 0)),
        ("duplicate_conversation_id", [(1, "민지")], [(10, 1, "A"), (10, 1, "B")], [], True, (0, 0, 0)),
    ]
    failures = 0
    with TemporaryDirectory() as folder:
        for index, (name, users, conversations, messages, expected_rejection, expected_counts) in enumerate(cases):
            db_path = Path(folder) / f"case{index}.db"
            target.create_database(db_path)
            connection = sqlite3.connect(db_path, autocommit=False)
            rejected = False
            try:
                try:
                    connection.executemany("INSERT INTO users VALUES (?, ?)", users)
                    connection.executemany("INSERT INTO conversations VALUES (?, ?, ?)", conversations)
                    connection.executemany("INSERT INTO messages VALUES (?, ?, ?, ?)", messages)
                    connection.commit()
                except sqlite3.IntegrityError:
                    connection.rollback()
                    rejected = True
                counts = tuple(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                               for table in ["users", "conversations", "messages"])
            finally:
                connection.close()
            passed = rejected == expected_rejection and counts == expected_counts
            print(f"{'PASS' if passed else 'FAIL'} {name}: rejected={rejected}; counts={counts}")
            failures += int(not passed)
    print(f"RESULT failures={failures}")
    raise SystemExit(1 if failures else 0)
