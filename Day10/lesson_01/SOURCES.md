# 공식 문서

확인일: 2026-10-27 (한국 기준).

- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite 외래키: https://www.sqlite.org/foreignkeys.html

1차시에서는 Python 3.12 이상에서 지원하는 autocommit=False를 명시한다.
connect는 경로에 DB 파일을 만들거나 기존 파일을 연다. commit으로 변경을 확정하고 close로 연결을 닫는다.
보류 중인 변경이 있는 상태에서 연결을 닫으면 변경이 사라질 수 있으므로 재연결로 저장을 확인한다.
연결을 with 문에서 사용하더라도 문맥 관리가 연결 종료를 자동으로 대신하는 것은 아니다.
본 예제는 try/finally로 종료를 명시한다.

SQLite는 별도 서버 없이 동작한다. Python 배포판에 sqlite3가 포함되어 있는지 import로 확인한다.
DB의 접근 권한·사용자 인증을 자동으로 제공하는 구조가 아니다.
외래키를 다룰 때는 연결마다 트랜잭션 시작 전에 PRAGMA foreign_keys=ON을 설정하고 적용 여부를 확인한다.
1차시는 사용자 단일 테이블을 저장하므로 외래키 코드를 포함하지 않는다.
