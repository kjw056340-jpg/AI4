# 8차시 코드 해설

## 전체 학생 코드 (`main.py`)

```python
def combine_tasks(main_tasks: list[dict], feature_tasks: list[dict]) -> list[dict]:
    return feature_tasks
```

## 강사용 최소 수정 코드 (`solution.py`)

```python
def combine_tasks(main_tasks: list[dict], feature_tasks: list[dict]) -> list[dict]:
    by_id = {task["id"]: task for task in main_tasks}
    for task in feature_tasks:
        by_id[task["id"]] = task
    return [by_id[key] for key in sorted(by_id)]
```

## 검증 코드 전체 (`check.py`)

```python
import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
combine = importlib.import_module(name).combine_tasks
main_items = [{"id": 1, "title": "메인"}]
feature_items = [{"id": 2, "title": "기능"}]
result = combine(main_items, feature_items)
print(result)
assert [x["id"] for x in result] == [1, 2]
assert combine([{"id": 1, "title": "기존"}], [{"id": 1, "title": "기능 우선"}])[0]["title"] == "기능 우선"
print("PASS")
```

## 코드 흐름과 역할

`main.py`와 `solution.py`는 **둘 다 동시에 실행하는 파일이 아닙니다.** `check.py` 인자를 통해 하나만 로딩합니다. `check.py`는 입력을 공급하고 출력/상태를 확인합니다. `assert`는 기대가 다를 때 `AssertionError`를 발생시킵니다.

- **오류 원인:** 서로 다른 변경 목록을 병합하면서 한쪽만 반환해 상대 수정이 소실된다.
- **최소 수정:** ID별로 병합해 양쪽의 다른 ID를 유지하고 충돌되는 ID 정책을 명시한다.
- **핵심 관찰:** 서로 다른 변경 목록을 병합하면서 한쪽만 반환해 상대 수정이 소실된다. 정답에서 ID별로 병합해 양쪽의 다른 ID를 유지하고 충돌되는 ID 정책을 명시한다.
- **비유:** 동료에게 보내는 변경 내역에는 실제로 수정한 내용과 삭제한 내용이 모두 보이도록 하고, 승인 전 검증을 끝냅니다.

## 자주 막히는 지점

- `ModuleNotFoundError` → `lesson_08`에서 가상환경 및 패키지 설치를 확인합니다.
- `AssertionError` → 오류 재현 단계에서 학생 코드 실패는 정상적인 관찰입니다.
- GitHub 접근 실패 → 로컬 Python과 Git 단계까지 수행하고 원격 관련 증빙은 별도 수집합니다.
- AI가 검사 코드를 통과시키기 위해 `assert`를 삭제하자고 하면 거부합니다. 코드를 최소 변경하고 의미 있는 검증을 유지합니다.
