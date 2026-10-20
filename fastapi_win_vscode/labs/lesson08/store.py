from fastapi import HTTPException

# In-memory teaching store: use one worker; restart resets all data.
tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}
next_id = 2

def require_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

def create_task(data: dict):
    global next_id
    task = {"id": next_id, **data}
    tasks[next_id] = task
    next_id += 1
    return task
