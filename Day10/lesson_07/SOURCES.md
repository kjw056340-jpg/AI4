# 공식 문서

확인일: 2026-10-27 (한국 기준). 아래 공식 페이지를 열어 확인했다.

- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite CREATE TABLE·제약조건: https://www.sqlite.org/lang_createtable.html
- SQLite 외래키: https://www.sqlite.org/foreignkeys.html
- SQLite SELECT·JOIN·GROUP BY·집계: https://www.sqlite.org/lang_select.html


## 현재 실습의 해석

LEFT JOIN은 자식이 없어도 부모 행을 남긴다. COUNT(*)는 그 행을 세지만 COUNT(m.id)는 NULL 메시지 id를 세지 않는다.

- 물리적인 DB 처리 순서를 설명하는 것이 아니라 쿼리 의미를 따라가며 결과를 분석한다.
- 현재 이력 조회는 대화방 id 기준이다. 호출자의 신원 검증 기능이 있는 것으로 설명하지 않는다.

Python 3.12 이상의 autocommit 설정을 명시한다. SQL 제약과 앱 함수의 정책을 구분하고,
직접 실행한 임시 파일 DB 결과와 실제 서비스·인증·동시성 검증을 혼동하지 않는다.
