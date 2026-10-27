from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

SCHEMA = """CREATE TABLE users (id INTEGER PRIMARY KEY, nickname TEXT NOT NULL);
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title TEXT NOT NULL
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE RESTRICT,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL
);"""

def connect_database(db_path):
    connection = sqlite3.connect(db_path, autocommit=True)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.autocommit = False
    return connection


def create_database(db_path):
    connection = connect_database(db_path)
    try:
        connection.executescript(SCHEMA)
        connection.execute("INSERT INTO users VALUES (1, '민지')")
        connection.execute("INSERT INTO conversations VALUES (10, 1, 'SQL 질문')")
        connection.execute("INSERT INTO messages VALUES (1, 10, 'user', '안녕')")
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "foreign_keys.db"
        create_database(db_path)
        connection = connect_database(db_path)
        try:
            print("외래키 설정:", connection.execute("PRAGMA foreign_keys").fetchone()[0])
            try:
                connection.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (2, 999, "user", "고아 메시지"))
                connection.commit()
            except sqlite3.IntegrityError as exc:
                connection.rollback()
                print("없는 대화방 거절:", exc)
            else:
                print("문제: 없는 대화방의 메시지가 저장되었습니다.")
        finally:
            connection.close()
