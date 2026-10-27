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
        connection.executemany("INSERT INTO users VALUES (?, ?)", [(1, "민지"), (2, "준호")])
        connection.executemany("INSERT INTO conversations VALUES (?, ?, ?)",
                               [(10, 1, "빈 대화"), (20, 1, "파이썬"), (30, 2, "SQL")])
        connection.executemany("INSERT INTO messages VALUES (?, ?, ?, ?)",
                               [(1, 20, "user", "질문"), (2, 20, "assistant", "답변"), (3, 30, "user", "SQL 질문")])
        connection.commit()
    finally:
        connection.close()


def conversation_summary(db_path, user_id):
    connection = connect_database(db_path)
    try:
        return connection.execute(
            "SELECT c.id, u.nickname, c.title, COUNT(*) AS message_count "
            "FROM conversations AS c JOIN users AS u ON u.id = c.user_id "
            "LEFT JOIN messages AS m ON m.conversation_id = c.id "
            "WHERE c.user_id = ? "
            "GROUP BY c.id, u.nickname, c.title ORDER BY c.id", (user_id,)
        ).fetchall()
    finally:
        connection.close()


def message_history(db_path, conversation_id):
    connection = connect_database(db_path)
    try:
        return connection.execute(
            "SELECT m.id, m.role, m.content FROM messages AS m "
            "JOIN conversations AS c ON c.id = m.conversation_id "
            "WHERE c.id = ? ORDER BY m.id", (conversation_id,)
        ).fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    with TemporaryDirectory() as folder:
        db_path = Path(folder) / "joins.db"
        create_database(db_path)
        print("사용자 1 대화 목록:", conversation_summary(db_path, 1))
        print("대화 20 이력:", message_history(db_path, 20))
        print("빈 대화 이력:", message_history(db_path, 10))
