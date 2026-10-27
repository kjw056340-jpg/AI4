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
