# 공식 문서

확인일: 2026-10-27 (한국 기준).

- Python sqlite3·executemany·자리표시자·트랜잭션: https://docs.python.org/3/library/sqlite3.html
- SQLite SELECT·WHERE·ORDER BY·LIMIT: https://www.sqlite.org/lang_select.html

ORDER BY의 모든 정렬 키가 같은 행들끼리는 순서가 확정되지 않는다. 이 실습은 고유 id를 추가 정렬 키로 쓴다.
LIMIT 0은 0행이고 음수 LIMIT은 상한 없는 조회를 뜻한다. 음수를 거절하는 것은 본 실습 함수의 정책이다.
학습할 때는 WHERE로 조건을 고르고 ORDER BY로 정렬한 뒤 LIMIT으로 상한을 정한다고 이해한다.
이는 의미를 이해하기 위한 설명이며 DB 내부의 물리적 실행 순서를 보장하는 설명은 아니다.
prepare_database는 고정 PK와 INSERT OR IGNORE로 샘플 준비 재실행 시 행이 늘지 않도록 한다.
기존 행을 수정하는 코드가 아니며 실습 전용 DB 파일에서만 사용한다.
