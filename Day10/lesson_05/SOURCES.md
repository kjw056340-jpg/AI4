# 공식 문서

확인일: 2026-10-27 (한국 기준). 아래 공식 페이지를 열어 확인했다.

- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite CREATE TABLE·제약조건: https://www.sqlite.org/lang_createtable.html
- SQLite 외래키: https://www.sqlite.org/foreignkeys.html
- SQLite SELECT·JOIN·GROUP BY·집계: https://www.sqlite.org/lang_select.html


## 현재 실습의 해석

conversations의 PK는 대화방 id다. user_id까지 유일하게 만들면 같은 사용자를 참조하는 행이 두 개 존재할 수 없다.

- 이 차시의 핵심 검사는 관계의 개수다. id 값만 가진 구조는 부모 존재를 강제하지 않는다.
- 제목·표시 이름은 식별자가 아니다. 같은 내용도 서로 다른 id의 행일 수 있다.

Python 3.12 이상의 autocommit 설정을 명시한다. SQL 제약과 앱 함수의 정책을 구분하고,
직접 실행한 임시 파일 DB 결과와 실제 서비스·인증·동시성 검증을 혼동하지 않는다.
