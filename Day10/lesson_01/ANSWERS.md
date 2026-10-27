# 실습 후 비교·자기 점검

## 최소 수정

save_user에서 return rows 직전에 한 줄을 추가한다.

```python
connection.commit()
return rows
```

테이블 준비 뒤의 첫 commit은 그 시점까지의 준비를 확정한다. 그 다음 INSERT의 변경까지 미리 확정하지 않는다.
같은 연결에서 SELECT하면 아직 확정하지 않은 자신의 변경도 보인다.
autocommit=False에서 사용자 INSERT 후 commit을 하지 않고 닫으면 보류 중인 변경은 되돌려진다.
DB 파일·테이블이 존재하는 것과 사용자 행이 저장된 것은 서로 다른 확인 항목이다.
return을 만나도 finally가 실행되므로 connection.close()도 실행된다.

## 확인 질문 답

1. sqlite3는 Python에서 SQLite DB를 다루는 표준 라이브러리 모듈이다. 이 실습에는 별도 DB 서버가 없다.
2. practice.db는 데이터가 남는 파일이다. Python 리스트는 프로그램 실행 중 메모리의 값이다.
3. 테이블은 데이터 종류별 표, 행은 한 사용자, 열은 id와 nickname 같은 속성이다.
4. connect는 연결, execute는 SQL 실행, fetchall은 조회 행 수집이다.
5. commit은 현재 트랜잭션의 변경 확정이고 close는 연결 종료다. 둘은 같은 동작이 아니다.
6. 같은 연결의 조회만으로 재시작 뒤에도 남는다고 판단할 수 없다. 새 연결로 다시 조회해야 한다.
7. ?는 값 자리표시자다. 값은 (nickname,)으로 전달하며 Python 문자열 이어붙이기로 SQL을 만들지 않는다.
8. (nickname,)의 쉼표는 원소가 하나인 튜플을 만든다.
9. None은 SQL NULL로 전달되고 nickname TEXT NOT NULL 조건을 위반하므로 거절된다.
10. nickname은 중복 가능하다. id로 사용자 행을 구분한다. 이 표는 로그인 인증 시스템이 아니다.

## 제출 평가 — 10점

- 연결 안의 조회와 재연결 결과를 수정 전후로 기록: 3점
- 기존 commit과 누락된 commit의 위치·역할 설명: 3점
- 한 줄 수정·여섯 검사 통과·기존 코드 보존: 3점
- DB 파일 경로와 재실행 시 행 추가를 설명: 1점

실제 DB 파일은 제출하지 않아도 된다. main.py와 검사 출력·설명으로 결과를 공유한다.
