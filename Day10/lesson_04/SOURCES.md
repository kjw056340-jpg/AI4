# 공식 문서

확인일: 2026-10-27 (한국 기준). 아래 공식 페이지를 열어 확인했다.

- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite CREATE TABLE·제약조건: https://www.sqlite.org/lang_createtable.html
- SQLite 외래키: https://www.sqlite.org/foreignkeys.html
- SQLite SELECT·JOIN·GROUP BY·집계: https://www.sqlite.org/lang_select.html


## 현재 실습의 해석

CHECK 식이 NULL이면 해당 CHECK만으로 거절하지 않는다. 따라서 필수값 조건은 NOT NULL로 따로 표현해야 한다.

- 빈 문자열과 NULL은 다르다. NOT NULL이 빈 문자열이나 이메일 형식까지 검증하지는 않는다.
- 이 실습은 점수 범위·누락 검사를 다룬다. INTEGER 표기만으로 소수 입력이 모두 거절된다고 주장하지 않는다.

Python 3.12 이상의 autocommit 설정을 명시한다. SQL 제약과 앱 함수의 정책을 구분하고,
직접 실행한 임시 파일 DB 결과와 실제 서비스·인증·동시성 검증을 혼동하지 않는다.
