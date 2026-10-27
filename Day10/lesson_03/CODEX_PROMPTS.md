# Codex 분석 → 최소 수정 → 검토

## 1. 분석

```text
lesson_03의 main.py, check.py, README.md를 읽어줘. solution.py는 아직 읽지 마.
Python 3.12 이상·표준 sqlite3 환경에서 python main.py --delete-id 999와
python check.py main으로 재현해줘. 두 명령은 매번 임시 DB를 사용해.
업무 약속: id=1 점수를 90으로 바꾸고 id=3을 삭제하는 두 작업을 한 묶음으로 처리해.
삭제 id=999가 없으면 ValueError로 거절하고 점수도 원래 80이어야 해.
실제: 오류는 나지만 새 연결에서 id=1의 점수가 90으로 남아.
수정하지 말고 UPDATE → rowcount → commit → DELETE → rowcount →
ValueError → except rollback → 새 연결 SELECT의 호출·트랜잭션 경계를 추적해줘.
prepare_database의 준비 commit과 apply_changes 안의 commit을 구분해줘.
DB가 자동 오류를 낸 것과 Python에서 만든 오류를 구분하고, 실행 사실과 추론을 나누어줘.
```

단순히 'rollback이 있다'고 확인하는 대신 어느 commit 이후에 호출되는지 따라가야 한다.
준비와 업무 변경을 나누면 정상 샘플을 만드는 commit까지 지우는 일을 피할 수 있다.

## 2. 최소 수정

```text
main.py의 apply_changes에서 두 작업의 중간 commit 한 줄을 제거해줘.
UPDATE·DELETE의 WHERE와 ? 값, 반환 (1, 1), rowcount 검사, 오류 메시지,
두 작업 성공 후 commit·예외 시 rollback·finally close는 보존해줘.
prepare_database·read_users·check.py·reproduce.py·solution.py는 변경하지 마.
입력을 바꾸거나 오류를 삼키거나 원래 점수를 수동 UPDATE하는 보상 코드로 우회하지 마.
새 테이블·패키지·다음 차시 기능을 추가하지 마.
python check.py main의 여섯 검사 PASS, failures=0, 종료 코드 0을 확인해줘.
python main.py는 성공하고, python main.py --delete-id 999는 종료 코드 1이지만
재연결 결과는 원본 세 행으로 유지되는지 보여줘. 실행 불가는 미실행이라고 밝혀줘.
```

최종 상태와 성공·실패 계약을 보존해야 전체 성공과 전체 취소를 함께 만족할 수 있다.
직접 원상복구 SQL을 더하는 대신 확정 시점을 고치는 것이 원인에 맞는 수정이다.

## 3. 검토

```text
삭제한 commit 한 줄과 rollback이 복원할 수 있는 범위를 연결해 설명해줘.
python check.py main과 python check.py solution의 실제 결과를 비교해줘.
정상 (1, 1), 없는 수정 대상, 없는 삭제 대상, None 거절, 0점 저장,
다른 삭제 대상에서 나머지 행이 보존되는지 확인해줘.
python reproduce.py로 WHERE 누락 영향 행 수 3과 rollback 후 원복도 확인해줘.
미사용 코드·추가 기능과 실제 실행하지 못한 환경을 밝혀줘.
```

성공 결과만 검사하면 중간 실패의 부분 저장을 놓친다. 새 연결의 전체 행을 비교해야 저장된 실제 상태를 알 수 있다.
