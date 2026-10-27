# 4차시 코드 해설

## 전체 학생 코드 (`main.py`)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
tasks = [{"id": 1, "title": "첫째"}, {"id": 3, "title": "셋째"}]

class TaskIn(BaseModel):
    title: str = Field(min_length=1)

@app.get("/tasks")
def list_tasks():
    return tasks

@app.post("/tasks", status_code=201)
def create_task(payload: TaskIn):
    task = {"id": max(task["id"] for task in tasks) + 1, "title": payload.title}
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskIn):
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = payload.title
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    tasks.pop(task_id)
```

## 강사용 최소 수정 코드 (`solution.py`)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
tasks = [{"id": 1, "title": "첫째"}, {"id": 3, "title": "셋째"}]

class TaskIn(BaseModel):
    title: str = Field(min_length=1)

@app.get("/tasks")
def list_tasks():
    return tasks

@app.post("/tasks", status_code=201)
def create_task(payload: TaskIn):
    task = {"id": max(task["id"] for task in tasks) + 1, "title": payload.title}
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskIn):
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = payload.title
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return
    raise HTTPException(status_code=404, detail="Task not found")
```

## 검증 코드 전체 (`check.py`)

```python
import importlib
import sys
from fastapi.testclient import TestClient

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
client = TestClient(importlib.import_module(name).app, raise_server_exceptions=False)
assert [t["id"] for t in client.get("/tasks").json()] == [1, 3]
created = client.post("/tasks", json={"title": "넷째"})
assert created.status_code == 201 and created.json()["id"] == 4
changed = client.put("/tasks/3", json={"title": "수정"})
assert changed.status_code == 200 and changed.json()["title"] == "수정"
removed = client.delete("/tasks/3")
print("DELETE /tasks/3:", removed.status_code)
assert removed.status_code == 204, "Task ID를 리스트 인덱스로 잘못 사용했을 수 있습니다"
ids = [t["id"] for t in client.get("/tasks").json()]
print("remaining IDs:", ids)
assert ids == [1, 4]
assert client.delete("/tasks/999").status_code == 404
print("PASS")
```

## 코드 흐름과 역할

`main.py`와 `solution.py`는 **둘 다 동시에 실행하는 파일이 아닙니다.** `check.py` 인자를 통해 하나만 로딩합니다. `check.py`는 입력을 공급하고 출력/상태를 확인합니다. `assert`는 기대가 다를 때 `AssertionError`를 발생시킵니다.

- **오류 원인:** 삭제 시 Task ID를 리스트 인덱스로 간주해 500이 발생한다.
- **최소 수정:** ID가 같은 항목의 인덱스를 찾아 삭제하고 없으면 404로 반환한다.
- **핵심 관찰:** GET [1,3] → POST 4 → PUT 3 → DELETE 3 → GET [1,4]; 없는 ID 404
- **비유:** 식당 주문표에 없는 번호는 존재하지 않는 주문으로 처리하고, 주문번호와 줄 번호는 구별합니다.

## 자주 막히는 지점

- `ModuleNotFoundError` → `lesson_04`에서 가상환경 및 패키지 설치를 확인합니다.
- `AssertionError` → 오류 재현 단계에서 학생 코드 실패는 정상적인 관찰입니다.
- 포트 8000 사용 중 → 서버 Ctrl+C 후 재시작; `check.py`는 서버 실행 없이 동작합니다.
- AI가 검사 코드를 통과시키기 위해 `assert`를 삭제하자고 하면 거부합니다. 코드를 최소 변경하고 의미 있는 검증을 유지합니다.
