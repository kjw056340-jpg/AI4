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
        ("valid_message", "INSERT INTO messages VALUES (?, ?, ?, ?)", (2, 10, "assistant", "답변"), False),
        ("missing_conversation", "INSERT INTO messages VALUES (?, ?, ?, ?)", (2, 999, "user", "질문"), True),
        ("missing_user", "INSERT INTO conversations VALUES (?, ?, ?)", (20, 999, "대화"), True),
        ("parent_conversation_delete", "DELETE FROM conversations WHERE id = ?", (10,), True),
        ("parent_user_delete", "DELETE FROM users WHERE id = ?", (1,), True),
        ("invalid_role", "INSERT INTO messages VALUES (?, ?, ?, ?)", (2, 10, "admin", "질문"), True),
        ("null_content", "INSERT INTO messages VALUES (?, ?, ?, ?)", (2, 10, "user", None), True),
    ]
    failures = 0
    with TemporaryDirectory() as folder:
        for index, (name, sql, params, expected_rejection) in enumerate(cases):
            db_path = Path(folder) / f"case{index}.db"
            target.create_database(db_path)
            connection = target.connect_database(db_path)
            try:
                if index == 0:
                    enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
                    print(f"{'PASS' if enabled else 'FAIL'} foreign_keys_enabled")
                    failures += int(not enabled)
                rejected = False
                try:
                    connection.execute(sql, params)
                    connection.commit()
                except sqlite3.IntegrityError:
                    connection.rollback()
                    rejected = True
                violations = connection.execute("PRAGMA foreign_key_check").fetchall()
            finally:
                connection.close()
            passed = rejected == expected_rejection and violations == []
            print(f"{'PASS' if passed else 'FAIL'} {name}: rejected={rejected}; violations={violations}")
            failures += int(not passed)
    print(f"RESULT failures={failures}")
    raise SystemExit(1 if failures else 0)
