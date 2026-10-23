# 7차시 코드 전체와 실행 관계

실제 배포 파일과 동일한 코드입니다. 정답은 TEACHER.md에 분리했습니다.

## main.py — 학생 시작 코드 전체

```python
from typing import Annotated
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field

app = FastAPI(title="작업 상태 API")
app.state.tasks = {}


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=20)


@app.post("/tasks", status_code=201)
def create_task(body: TaskIn):
    task_id = 1
    task = {"id": task_id, "title": body.title}
    app.state.tasks[task_id] = task
    return task


@app.get("/tasks/{task_id}", responses={404: {"description": "작업 없음"}})
def read_task(task_id: Annotated[int, Path(ge=1)]):
    if task_id not in app.state.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return app.state.tasks[task_id]
```

## 역할과 이유

| 코드·심볼 | 무엇을 하고 왜 필요한가 |
| --- | --- |
| app.state.tasks | 현재 앱 프로세스 안에만 있는 메모리 장부입니다. 재시작하면 사라집니다. |
| create_task | 입력을 검증한 뒤 ID를 부여하고 사전에 저장합니다. |
| read_task | GET 경로에 전달된 ID로 같은 앱 장부에서 찾습니다. |
| clean_tasks fixture | pytest가 각 테스트 시작 전에 실행하고 yield 뒤 정리를 합니다. 명시적으로 pytest.fixture로 등록했습니다. |
| test_two_tasks | 생성 두 번과 조회 두 번을 같은 테스트 안에서 실행합니다. 테스트 사이의 공유와 시나리오 안의 공유를 구분합니다. |


## 호출 흐름

브라우저 Swagger Execute 또는 curl → Uvicorn 127.0.0.1:8000 → FastAPI 입력 검증 → 위 경로 함수 → JSON HTTP 응답입니다. 자동 검사는 `python -m pytest -q test_api.py` → pytest가 테스트 함수 호출 → TestClient → 같은 앱의 경로 함수 → assert 비교입니다. TestClient는 외부 네트워크를 통과하지 않습니다.

모델 클래스는 선언이고 요청마다 모델 검증이 일어납니다. 데코레이터는 경로 등록이며 요청 전송이 아닙니다. pytest의 parametrize는 입력 행별 테스트를 등록하고 pytest 실행 시 각 함수를 호출합니다. 테스트 파일의 import 시 TestClient를 준비하지만 실제 API 함수는 client.get/post에서 실행됩니다.

## test_api.py — 준비된 검사 코드 전체

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tasks():
    app.state.tasks.clear()
    yield
    app.state.tasks.clear()


@pytest.mark.parametrize("titles", [("read", "write"), ("same", "same")])
def test_two_tasks(titles):
    first = client.post("/tasks", json={"title": titles[0]})
    second = client.post("/tasks", json={"title": titles[1]})
    assert first.status_code == second.status_code == 201
    first_id = first.json()["id"]
    second_id = second.json()["id"]
    first_read = client.get(f"/tasks/{first_id}")
    second_read = client.get(f"/tasks/{second_id}")
    assert first_read.status_code == second_read.status_code == 200
    assert first_read.json() == first.json()
    assert second_read.json() == second.json()
    assert first_id > 0 and second_id > 0
    assert first_id != second_id


@pytest.mark.parametrize("body", [{"title": "one"}, {"title": "two"}])
def test_single_task(body):
    response = client.post("/tasks", json=body)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": body["title"]}


@pytest.mark.parametrize("task_id, status", [(99, 404), (0, 422)])
def test_missing_task(task_id, status):
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status
    if status == 404:
        assert response.json() == {"detail": "Task not found"}
    else:
        assert response.json()["detail"][0]["loc"] == ["path", "task_id"]


@pytest.mark.parametrize("body", [{}, {"title": ""}, {"title": "x" * 21}])
def test_invalid_task(body):
    response = client.post("/tasks", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]
    assert app.state.tasks == {}
```

assert는 기대 조건이 참인지 확인하고 거짓이면 해당 테스트를 실패시킵니다. status_code는 HTTP 처리 결과, json()은 응답 JSON을 Python dict/list로 변환한 결과입니다. JSON 본문을 보내는 json=와 받는 json()을 구분하세요. 테스트 함수 이름이 test_로 시작하여 pytest가 수집합니다. parametrize의 각 입력 조합은 독립된 검사로 계산됩니다.

## 파일의 실행 주체·입력·출력

| 파일 | 실행 주체 | 입력 | 출력·용도 |
| --- | --- | --- | --- |
| main.py | Uvicorn / TestClient | HTTP 경로·쿼리·본문 | 계약에 따른 응답 또는 의도한 결함 |
| solution.py | main.py로 복사 후 같은 명령 | 동일한 요청 | 수정 후 정상·오류 응답 |
| test_api.py | pytest | 각 테스트 입력과 main.app | 성공 개수 또는 assertion 실패 |
| requirements.txt | pip install -r | 직접 의존성 버전 목록 | 실습 실행 환경 |
| lesson_scope.json | 강사 범위 감사 | 파일 목적·경로 호출 근거 | 배포 범위 대조 자료 |


README·TEST_CASES·CODEX_PROMPTS는 학생이 활동 순서대로 읽습니다. TEACHER는 강사가 정답과 질문 해설에 사용합니다. REPORT_TEMPLATE은 학생이 실제 결과를 채웁니다. VERIFICATION은 제작자의 실행 근거이고 SOURCES는 공식 동작 확인 근거입니다. CHECKLIST는 제출 전 점검입니다. 이들 문서는 서버가 import하지 않습니다.
