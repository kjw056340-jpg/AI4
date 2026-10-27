# FastAPI CRUD: 데이터를 메모리의 리스트에 저장합니다.
from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, Field

app = FastAPI()


class TaskIn(BaseModel):
    name: str = Field(min_length=1)
    message: str = Field(min_length=1)


class TaskOut(TaskIn):
    id: int = Field(ge=1)


class TaskPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    message: str | None = Field(default=None, min_length=1)


# id는 서버에서 자동으로 생성합니다.
tasks: list[dict] = []
next_id = 1


def find_task(task_id: int) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", status_code=201, response_model=TaskOut)
def create_task(payload: TaskIn):
    global next_id
    task = {"id": next_id, **payload.model_dump()}
    tasks.append(task)
    next_id += 1
    return task


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks():
    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int = Path(ge=1)):
    return find_task(task_id)


# PUT: name과 message를 모두 전달하여 수정합니다.
@app.put("/tasks/{task_id}", response_model=TaskOut)
def replace_task(payload: TaskIn, task_id: int = Path(ge=1)):
    task = find_task(task_id)
    task.update(payload.model_dump())
    return task


# PATCH: 전달한 필드만 수정합니다. null은 허용하지 않습니다.
@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(payload: TaskPatch, task_id: int = Path(ge=1)):
    changes = payload.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Fields cannot be null")
    task = find_task(task_id)
    task.update(changes)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int = Path(ge=1)):
    task = find_task(task_id)
    tasks.remove(task)
    return Response(status_code=204)

