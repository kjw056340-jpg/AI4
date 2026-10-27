# 공식 문서

확인일: 2026-10-27 (한국 기준). 아래 공식 페이지를 열어 확인했다.

- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite CREATE TABLE·제약조건: https://www.sqlite.org/lang_createtable.html
- SQLite 외래키: https://www.sqlite.org/foreignkeys.html
- SQLite SELECT·JOIN·GROUP BY·집계: https://www.sqlite.org/lang_select.html


## 현재 실습의 해석

조회 함수가 user_id 인자를 받아도 실제 SQL에 쓰지 않았다. 저장 경로의 소유 검사로 조회 경로까지 검증된 것은 아니다.

- user_id는 로그인 검증을 마친 신뢰 가능한 호출자가 제공한다는 전제다. 이 실습은 인증·암호화·파일 권한을 구현하지 않는다.
- 각 직접 실행·검사는 실제 임시 DB 파일을 만들고 종료 때 정리한다. 실제 AI API를 호출하지 않으며 assistant_text는 제공한 문자열이다.

Python 3.12 이상의 autocommit 설정을 명시한다. SQL 제약과 앱 함수의 정책을 구분하고,
직접 실행한 임시 파일 DB 결과와 실제 서비스·인증·동시성 검증을 혼동하지 않는다.
