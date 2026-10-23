-- AUTOINCREMENT를 쓰지 않아 sqlite_sequence 테이블도 생성하지 않습니다.
CREATE TABLE IF NOT EXISTS guestbook (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(trim(name)) BETWEEN 1 AND 20),
    message TEXT NOT NULL CHECK(length(trim(message)) BETWEEN 1 AND 1000),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
);
