from typing import Annotated
from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class TaskInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=80)
    done: bool = Field(default=False, strict=True)

class TaskOut(TaskInput):
    id: int

app = FastAPI(title="Lesson 07")
tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}
next_id = 2

def require_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/tasks", response_model=list[TaskOut])
def list_tasks():
    return list(tasks.values())

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: Annotated[int, Path(ge=1)]):
    return require_task(task_id)

@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskInput):
    global next_id
    task = {"id": next_id, **payload.model_dump()}
    tasks[next_id] = task
    next_id += 1
    return task

class TaskPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=80)
    done: bool | None = Field(default=None, strict=True)

    @field_validator("title", "done", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Explicit null is not allowed")
        return value

    @model_validator(mode="after")
    def require_field(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field")
        return self

@app.put("/tasks/{task_id}", response_model=TaskOut)
def replace_task(task_id: Annotated[int, Path(ge=1)], payload: TaskInput):
    require_task(task_id)
    tasks[task_id] = {"id": task_id, **payload.model_dump()}
    return tasks[task_id]

@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: Annotated[int, Path(ge=1)], payload: TaskPatch):
    task = require_task(task_id)
    task.update(payload.model_dump(exclude_unset=True))
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: Annotated[int, Path(ge=1)]):
    require_task(task_id)
    del tasks[task_id]
    return Response(status_code=204)
