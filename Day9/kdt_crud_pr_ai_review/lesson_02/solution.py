from fastapi import FastAPI, HTTPException

app = FastAPI()
tasks = {1: {"id": 1, "title": "Git 준비"}}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
