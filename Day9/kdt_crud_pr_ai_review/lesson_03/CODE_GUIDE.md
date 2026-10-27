# 3차시 코드 해설

## 전체 학생 코드 (`main.py`)

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
item = {"id": 1, "title": "처음", "done": True}

class TaskPut(BaseModel):
    title: str = Field(min_length=1)
    done: bool

class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    done: bool = False

@app.put("/tasks/1")
def replace_task(payload: TaskPut):
    item.update(payload.model_dump())
    return item

@app.patch("/tasks/1")
def patch_task(payload: TaskPatch):
    item.update(payload.model_dump())
    return item
```

## 강사용 최소 수정 코드 (`solution.py`)

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
item = {"id": 1, "title": "처음", "done": True}

class TaskPut(BaseModel):
    title: str = Field(min_length=1)
    done: bool

class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    done: bool = False

@app.put("/tasks/1")
def replace_task(payload: TaskPut):
    item.update(payload.model_dump())
    return item

@app.patch("/tasks/1")
def patch_task(payload: TaskPatch):
    item.update(payload.model_dump(exclude_unset=True))
    return item
```

## 검증 코드 전체 (`check.py`)

```python
import importlib
import sys
from fastapi.testclient import TestClient

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
client = TestClient(importlib.import_module(name).app)
put = client.put("/tasks/1", json={"title": "완전교체", "done": True})
print("PUT:", put.status_code, put.json())
assert put.status_code == 200 and put.json()["done"] is True
invalid = client.put("/tasks/1", json={"title": "누락"})
print("PUT invalid:", invalid.status_code)
assert invalid.status_code == 422
patch = client.patch("/tasks/1", json={"title": "제목만"})
print("PATCH:", patch.status_code, patch.json())
assert patch.status_code == 200 and patch.json()["title"] == "제목만"
assert patch.json()["done"] is True, "PATCH가 지정하지 않은 done을 변경했습니다"
print("PASS")
```

## 코드 흐름과 역할

`main.py`와 `solution.py`는 **둘 다 동시에 실행하는 파일이 아닙니다.** `check.py` 인자를 통해 하나만 로딩합니다. `check.py`는 입력을 공급하고 출력/상태를 확인합니다. `assert`는 기대가 다를 때 `AssertionError`를 발생시킵니다.

- **오류 원인:** PATCH에서 전달되지 않은 done 필드까지 기본값 False로 덮어쓴다.
- **최소 수정:** model_dump(exclude_unset=True)로 요청에 포함된 필드만 반영한다.
- **핵심 관찰:** PUT 완전교체 200, 잘못된 PUT 422, PATCH 제목만 변경했을 때 done=True 유지
- **비유:** 식당 주문표에 없는 번호는 존재하지 않는 주문으로 처리하고, 주문번호와 줄 번호는 구별합니다.

## 자주 막히는 지점

- `ModuleNotFoundError` → `lesson_03`에서 가상환경 및 패키지 설치를 확인합니다.
- `AssertionError` → 오류 재현 단계에서 학생 코드 실패는 정상적인 관찰입니다.
- 포트 8000 사용 중 → 서버 Ctrl+C 후 재시작; `check.py`는 서버 실행 없이 동작합니다.
- AI가 검사 코드를 통과시키기 위해 `assert`를 삭제하자고 하면 거부합니다. 코드를 최소 변경하고 의미 있는 검증을 유지합니다.
