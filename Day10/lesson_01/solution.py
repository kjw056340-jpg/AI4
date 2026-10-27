"""사용자를 저장하고 연결을 다시 열어 확인한다. commit으로 저장을 확정한 비교 코드다."""
import argparse
from pathlib import Path
import sqlite3


def save_user(db_path, nickname):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY, nickname TEXT NOT NULL)"
        )
        connection.commit()  # 테이블 준비를 확정한다.
        connection.execute(
            "INSERT INTO users (nickname) VALUES (?)", (nickname,)
        )
        rows = connection.execute(
            "SELECT id, nickname FROM users ORDER BY id"
        ).fetchall()
        connection.commit()  # INSERT한 사용자 저장을 확정한다.
        return rows
    finally:
        connection.close()


def read_users(db_path):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        return connection.execute(
            "SELECT id, nickname FROM users ORDER BY id"
        ).fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(Path(__file__).with_name("practice.db")))
    parser.add_argument("--name", default="민지")
    args = parser.parse_args()
    print("연결 안에서:", save_user(args.db, args.name))
    print("다시 연결하면:", read_users(args.db))
