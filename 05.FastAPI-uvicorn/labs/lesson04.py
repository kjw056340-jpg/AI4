from typing import Annotated
from fastapi import FastAPI, Query

app = FastAPI(title="Lesson 04")
tasks = [
    {"id": 1, "title": "FastAPI basics", "done": False},
    {"id": 2, "title": "HTTP methods", "done": True},
    {"id": 3, "title": "Python review", "done": False},
]

@app.get("/tasks")
def list_tasks(
    q: str | None = None,
    done: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    rows = tasks
    if q is not None:
        rows = [t for t in rows if q.casefold() in t["title"].casefold()]
    if done is not None:
        rows = [t for t in rows if t["done"] == done]
    total = len(rows)
    return {"items": rows[skip:skip + limit], "total": total}