from typing import Annotated
from fastapi import FastAPI, HTTPException, Path

app = FastAPI(title="Lesson 03")
tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}

# Fixed paths must be declared before the variable route.
@app.get("/tasks/stats")
def task_stats():
    return {"total": len(tasks)}

@app.get("/tasks/{task_id}")
def read_task(task_id: Annotated[int, Path(ge=1)]):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]
