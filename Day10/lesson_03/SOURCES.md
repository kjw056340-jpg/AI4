# 공식 문서

확인일: 2026-10-27 (한국 기준).

- Python sqlite3·rowcount·autocommit·commit·rollback: https://docs.python.org/3/library/sqlite3.html
- SQLite UPDATE: https://www.sqlite.org/lang_update.html
- SQLite DELETE: https://www.sqlite.org/lang_delete.html
- SQLite 트랜잭션: https://www.sqlite.org/lang_transaction.html

UPDATE·DELETE에서 WHERE를 생략하면 전체 행을 대상으로 한다. 없는 id에 0행을 적용하는 것은 SQL 오류가 아니다.
정확히 1행이어야 한다는 검사와 ValueError는 이 실습 함수의 정책이다.
Python 3.12 이상의 autocommit=False를 명시하고 commit·rollback으로 트랜잭션을 제어한다.
이 설정에서 commit·rollback 뒤에는 새 트랜잭션이 자동으로 열린다. 별도의 BEGIN을 더하지 않는다.
SQLite 엔진의 자동 트랜잭션 설명과 Python 연결의 명시 설정을 혼동하지 않는다.
rollback은 현재 확정하지 않은 변경을 취소한다. 이미 commit한 변경까지 복원하는 기능은 아니다.
