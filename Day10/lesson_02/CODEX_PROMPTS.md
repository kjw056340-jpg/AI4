# Codex 분석 → 최소 수정 → 검토

실습 데이터만 사용한다. 실제 개인정보가 있는 DB나 로그는 프롬프트에 넣지 않는다.

## 1. 분석

```text
lesson_02의 main.py, check.py, README.md를 읽어줘. solution.py는 아직 읽지 마.
Python 3.12 이상·표준 sqlite3 환경에서 python check.py main으로 재현해줘.
정상: 서울 limit=2는 id [3, 5], limit=1은 [3], 제주 조회는 []야.
문제: 서울 limit=0이면 []여야 하는데 [3, 5]가 반환돼.
아직 수정하지 말고 CLI --limit → argparse int 변환 → find_users →
normalize_limit → effective_limit → SQL의 두 번째 ? → 결과를 추적해줘.
0이 처음 바뀌는 줄과 Python or의 값 선택 규칙을 설명해줘.
SQL의 LIMIT 0 자체가 문제인지 구분하고 실제 실행 사실과 추론을 나누어줘.
```

정상 입력은 조회 전체가 고장 난 것이 아님을 보여준다. 인자부터 SQL까지 추적하면 SQL에 도착하기 전 값이 바뀌는 경우를 찾을 수 있다.

## 2. 최소 수정

```text
main.py의 normalize_limit에서 0이 보존되도록 한 줄만 수정해줘.
음수의 ValueError, argparse의 기본값 2, SQL·출력 열·정렬·? 자리표시자,
파일 경로와 연결 종료는 보존해줘. check.py·solution.py와 데이터는 바꾸지 마.
limit=0만 별도 하드코딩해서 []를 반환하거나 조회를 우회하지 마.
새 API·패키지·테이블·다음 차시 기능도 추가하지 마.
python check.py main의 10개 검사 PASS, failures=0과 종료 코드 0을 확인해줘.
CLI에서 --city 서울 --limit 0도 []인지 재검증해줘.
실행하지 못했다면 미실행이라고 밝혀줘.
```

기본값은 이미 argparse에서 정한다. 입력 0을 기본값으로 덮어쓰지 않아야 한다.
검사 기대값을 유지해야 원래의 조회 계약을 만족하는지 알 수 있다.

## 3. 검토

```text
변경 한 줄과 0을 잃은 원인을 연결해 설명해줘.
python check.py main과 python check.py solution의 실제 결과를 비교해줘.
도시 필터, 동점 id 정렬, LIMIT 1·2·10·0, 없는 도시, SQL처럼 보이는 값,
음수 거절, 준비 재실행과 O'Neil 보존이 유지되는지 확인해줘.
미사용 코드·우회 처리·다음 차시 기능이 추가되지 않았는지 검토해줘.
실제 실행한 환경과 실행하지 못한 항목을 명시해줘.
```

0 검사만 통과시키는 수정이 기존 조회·오류 처리를 바꾸지 않았는지 확인하는 단계다.
