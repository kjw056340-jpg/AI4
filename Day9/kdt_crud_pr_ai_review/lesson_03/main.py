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
