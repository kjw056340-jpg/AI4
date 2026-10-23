from typing import Annotated
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field

app = FastAPI(title="작업 상태 API")
app.state.tasks = {}


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=20)


@app.post("/tasks", status_code=201)
def create_task(body: TaskIn):
    task_id = max(app.state.tasks, default=0) + 1
    task = {"id": task_id, "title": body.title}
    app.state.tasks[task_id] = task
    return task


@app.get("/tasks/{task_id}", responses={404: {"description": "작업 없음"}})
def read_task(task_id: Annotated[int, Path(ge=1)]):
    if task_id not in app.state.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return app.state.tasks[task_id]
