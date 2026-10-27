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
    content TEXT NOT NULL CHECK(length(trim(content)) > 0)
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
        connection.executemany("INSERT INTO users VALUES (?, ?)", [(1, "민지"), (2, "준호")])
        connection.executemany("INSERT INTO conversations VALUES (?, ?, ?)", [(1, 1, "민지의 방"), (2, 2, "준호의 방")])
        connection.commit()
    finally:
        connection.close()


def save_turn(db_path, user_id, conversation_id, user_text, assistant_text):
    connection = connect_database(db_path)
    try:
        owner = connection.execute(
            "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id),
        ).fetchone()
        if owner is None:
            raise ValueError("사용자의 대화방이 아닙니다.")
        first = connection.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, 'user', ?)",
            (conversation_id, user_text),
        )
        second = connection.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, 'assistant', ?)",
            (conversation_id, assistant_text),
        )
        connection.commit()
        return first.lastrowid, second.lastrowid
    except (ValueError, sqlite3.Error):
        connection.rollback()
        raise
    finally:
        connection.close()


def list_history(db_path, user_id, conversation_id):
    connection = connect_database(db_path)
    try:
        return connection.execute(
            "SELECT m.id, m.role, m.content FROM messages AS m "
            "JOIN conversations AS c ON c.id = m.conversation_id "
            "WHERE c.id = ? AND c.user_id = ? ORDER BY m.id", (conversation_id, user_id)
        ).fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "history.db"
        create_database(db_path)
        save_turn(db_path, 1, 1, "파이썬 질문", "파이썬 답변")
        save_turn(db_path, 2, 2, "준호 질문", "준호 답변")
        print("사용자 1의 이력:", list_history(db_path, 1, 1))
        print("사용자 2가 방 1을 조회:", list_history(db_path, 2, 1))
