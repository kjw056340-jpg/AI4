"""1차시 학생 시작 코드: 조회 + 등록 통합, 의도된 ID 중복 오류."""
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Task API - Lesson 01")
tasks = [{"id": 1, "title": "API 확인"}, {"id": 3, "title": "테스트 작성"}]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)


def next_id() -> int:
    return len(tasks) + 1  # 의도된 오류: ID의 최대값과 목록 길이는 다를 수 있음


@app.get("/tasks")
def list_tasks():
    return tasks


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    task = {"id": next_id(), "title": payload.title}
    tasks.append(task)
    return task
