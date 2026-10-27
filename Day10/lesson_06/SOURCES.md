# 공식 문서

확인일: 2026-10-27 (한국 기준). 아래 공식 페이지를 열어 확인했다.

- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite CREATE TABLE·제약조건: https://www.sqlite.org/lang_createtable.html
- SQLite 외래키: https://www.sqlite.org/foreignkeys.html
- SQLite SELECT·JOIN·GROUP BY·집계: https://www.sqlite.org/lang_select.html


## 현재 실습의 해석

foreign_keys 설정을 열린 트랜잭션 안에서 바꾸려 하면 적용되지 않는다. 명령의 존재가 아니라 실행 시점과 조회한 설정값을 확인해야 한다.

- 잘못된 연결에서 만들어진 고아 데이터는 설정을 고쳤다고 자동 삭제되지 않는다. 각 검사는 새 DB에서 시작한다.
- foreign_key_check 결과와 foreign_keys 설정값은 서로 다른 확인 항목이다.

Python 3.12 이상의 autocommit 설정을 명시한다. SQL 제약과 앱 함수의 정책을 구분하고,
직접 실행한 임시 파일 DB 결과와 실제 서비스·인증·동시성 검증을 혼동하지 않는다.
