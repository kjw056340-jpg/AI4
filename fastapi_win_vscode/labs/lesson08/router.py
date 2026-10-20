from typing import Annotated
from fastapi import APIRouter, Path, Query, Response
from . import store
from .schemas import TaskInput, TaskOut, TaskPage, TaskPatch

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("", response_model=TaskPage)
def list_tasks(
    q: str | None = None,
    done: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    rows = list(store.tasks.values())
    if q is not None:
        rows = [t for t in rows if q.casefold() in t["title"].casefold()]
    if done is not None:
        rows = [t for t in rows if t["done"] == done]
    return {"items": rows[skip:skip + limit], "total": len(rows)}

@router.get("/{task_id}", response_model=TaskOut)
def read_task(task_id: Annotated[int, Path(ge=1)]):
    return store.require_task(task_id)

@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskInput):
    return store.create_task(payload.model_dump())

@router.put("/{task_id}", response_model=TaskOut)
def replace_task(task_id: Annotated[int, Path(ge=1)], payload: TaskInput):
    store.require_task(task_id)
    store.tasks[task_id] = {"id": task_id, **payload.model_dump()}
    return store.tasks[task_id]

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: Annotated[int, Path(ge=1)], payload: TaskPatch):
    task = store.require_task(task_id)
    task.update(payload.model_dump(exclude_unset=True))
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: Annotated[int, Path(ge=1)]):
    store.require_task(task_id)
    del store.tasks[task_id]
    return Response(status_code=204)
