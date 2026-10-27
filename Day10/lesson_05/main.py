from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

SCHEMA = """CREATE TABLE users (id INTEGER PRIMARY KEY, nickname TEXT NOT NULL);
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY, conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL, content TEXT NOT NULL
);"""


def create_database(db_path):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()


def populate_demo(db_path):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        connection.execute("INSERT INTO users VALUES (?, ?)", (1, "민지"))
        connection.executemany(
            "INSERT INTO conversations VALUES (?, ?, ?)",
            [(10, 1, "파이썬 질문"), (20, 1, "SQL 질문")],
        )
        connection.executemany(
            "INSERT INTO messages VALUES (?, ?, ?, ?)",
            [(1, 10, "user", "리스트란?"), (2, 20, "user", "SQL이란?")],
        )
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "erd.db"
        create_database(db_path)
        try:
            populate_demo(db_path)
        except sqlite3.IntegrityError as exc:
            print("관계 요구사항과 충돌:", exc)
        connection = sqlite3.connect(db_path, autocommit=False)
        try:
            print("대화방:", connection.execute("SELECT * FROM conversations ORDER BY id").fetchall())
            print("메시지:", connection.execute("SELECT * FROM messages ORDER BY id").fetchall())
        finally:
            connection.close()
