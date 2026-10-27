# Codex 분석·최소 수정·검토

아래 프롬프트를 분석 → 최소 수정 → 검토 순서로 사용한다. 실제 개인정보가 없는 실습 DB만 이용한다.
Codex가 없어도 같은 질문을 코드에 대입하며 직접 분석할 수 있다.

## 분석

```text
lesson_01의 main.py, check.py, README.md를 읽어줘. solution.py는 아직 읽지 마.
Python 3.12 이상, 표준 sqlite3 모듈 환경이야. python check.py main으로 재현해줘.
기대: 민지가 연결을 닫았다가 열어도 [(1, '민지')]로 남아야 해.
실제: 같은 연결에서는 보이지만 새 연결에서는 []야. DB 파일은 존재해.
아직 수정하지 말고 save_user의 connect → CREATE → commit → INSERT →
SELECT → return → finally close와 read_users의 새 연결 흐름을 추적해줘.
각 commit 시점 이전과 이후에 어떤 변경이 있는지 나누어 설명해줘.
autocommit=False에서 close가 저장을 확정하는지 공식 문서와 대조해줘.
실행한 사실·코드에서 확인한 사실·추론을 구분해줘.
```

같은 연결과 새 연결을 비교하면 '조회는 됐다'와 '저장됐다'를 구분할 수 있다.
이미 있는 commit의 위치까지 추적해야 단순히 함수에 commit이 있다는 이유로 원인을 놓치지 않는다.

## 최소 수정

```text
main.py의 save_user에서 INSERT한 사용자 저장이 확정되도록 한 줄만 추가해줘.
DB 경로, 함수 인자, CREATE TABLE·INSERT·SELECT SQL과 반환 rows 구조는 보존해줘.
autocommit=False, ? 자리표시자와 finally close도 유지해줘.
check.py, solution.py, 검사 기대값은 바꾸지 마.
메모리 전역 목록이나 출력 문자열 하드코딩, :memory: 전환으로 우회하지 마.
새 테이블·패키지·다음 차시 기능을 추가하지 마.
python check.py main에서 여섯 검사 PASS, failures=0, 종료 코드 0을 확인해줘.
NULL 거절과 따옴표가 있는 이름 보존도 유지해줘. 실행 불가 항목은 미실행이라고 밝혀줘.
```

검사와 데이터는 그대로 두어야 원래의 저장 약속을 만족한 것인지 확인할 수 있다.
경로와 연결 종료 보존은 다른 DB를 조회하거나 자원을 닫지 않는 편법을 막는다.

## 검토

```text
추가한 commit 한 줄과 원인을 연결해서 설명해줘.
python check.py main과 python check.py solution의 실제 결과를 비교해줘.
첫 사용자와 두 번째 사용자가 재연결 후 남고, O'Neil이 그대로 저장되고,
None은 IntegrityError로 거절되며 기존 데이터가 유지되는지 보여줘.
try 안에서 return하더라도 finally가 실행되는지 설명해줘.
미사용 import·함수·변수와 새 기능이 추가되지 않았는지 확인해줘.
검증한 실행 환경과 실행하지 못한 환경을 명시해줘.
```

정상 저장과 잘못된 입력을 함께 검사해야 기존 동작을 지키면서 원인을 해결했는지 판단할 수 있다.
