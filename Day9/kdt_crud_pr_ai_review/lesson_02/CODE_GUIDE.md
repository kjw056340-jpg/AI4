# 2차시 코드 해설

## 전체 학생 코드 (`main.py`)

```python
from fastapi import FastAPI

app = FastAPI()
tasks = {1: {"id": 1, "title": "Git 준비"}}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return tasks.get(task_id)
```

## 강사용 최소 수정 코드 (`solution.py`)

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()
tasks = {1: {"id": 1, "title": "Git 준비"}}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

## 검증 코드 전체 (`check.py`)

```python
from fastapi.testclient import TestClient
import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
client = TestClient(importlib.import_module(name).app)
found = client.get("/tasks/1")
missing = client.get("/tasks/999")
print("existing:", found.status_code, found.json())
print("missing:", missing.status_code, missing.json())
assert found.status_code == 200 and found.json()["id"] == 1
assert missing.status_code == 404
assert missing.json()["detail"] == "Task not found"
print("PASS")
```

## 코드 흐름과 역할

`main.py`와 `solution.py`는 **둘 다 동시에 실행하는 파일이 아닙니다.** `check.py` 인자를 통해 하나만 로딩합니다. `check.py`는 입력을 공급하고 출력/상태를 확인합니다. `assert`는 기대가 다를 때 `AssertionError`를 발생시킵니다.

- **오류 원인:** 없는 항목에 None을 그대로 반환해 200 null이 된다.
- **최소 수정:** 찾지 못하면 HTTPException(status_code=404)을 발생시킨다.
- **핵심 관찰:** 기존 /tasks/1 → 200; 미존재 /tasks/999 → 학생 200 null, 정답 404
- **비유:** 식당 주문표에 없는 번호는 존재하지 않는 주문으로 처리하고, 주문번호와 줄 번호는 구별합니다.

## 자주 막히는 지점

- `ModuleNotFoundError` → `lesson_02`에서 가상환경 및 패키지 설치를 확인합니다.
- `AssertionError` → 오류 재현 단계에서 학생 코드 실패는 정상적인 관찰입니다.
- 포트 8000 사용 중 → 서버 Ctrl+C 후 재시작; `check.py`는 서버 실행 없이 동작합니다.
- AI가 검사 코드를 통과시키기 위해 `assert`를 삭제하자고 하면 거부합니다. 코드를 최소 변경하고 의미 있는 검증을 유지합니다.
