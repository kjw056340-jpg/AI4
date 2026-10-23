# 7차시 강사용 해설

## 수업 의도와 진행

목표: POST 후 GET을 잇는 시나리오로 ID 덮어쓰기를 재현하고 테스트 간 공유 상태를 초기화한다. 학생이 처음에는 결과를 예상하고, 실제 실패를 보고, 원인을 코드로 설명한 뒤 수정하게 합니다. 정답을 먼저 복사하면 재현·분석 학습이 사라집니다. 설치가 끝난 환경을 사전에 준비하고 README의 50분 배분을 사용합니다. AI 도구가 없으면 제공 프롬프트를 동료 검토 질문으로 바꾸어 진행합니다.

교사의 시연은 정상 입력 1개와 핵심 실패 1개로 제한합니다. 나머지는 짝 활동으로 분담하고 전체 제공 검사를 마지막에 실행합니다. 코드 전체는 CODE_GUIDE에 있어 수업 시간에 전부 타이핑할 필요가 없습니다. 학생 질문에서는 상태·본문·문서·상태 변화 중 무엇을 확인했는지 되묻습니다.

## 원인과 최소 수정

- 실제 증상: 작업 A 생성 후 작업 B를 생성하면 둘 다 id=1이고 GET /tasks/1은 B를 반환합니다.
- 원인: create_task가 항상 task_id=1을 사용해 같은 dict 키를 덮어씁니다. 한 번 생성 테스트만으로는 발견할 수 없습니다.
- 최소 수정: ID를 max(app.state.tasks, default=0)+1로 계산합니다. 테스트 fixture의 초기화는 그대로 유지합니다.

```diff
--- main.py (시작)
+++ main.py (수정)
@@ -12,7 +12,7 @@
 
 @app.post("/tasks", status_code=201)
 def create_task(body: TaskIn):
-    task_id = 1
+    task_id = max(app.state.tasks, default=0) + 1
     task = {"id": task_id, "title": body.title}
     app.state.tasks[task_id] = task
     return task
```

## solution.py — 수정 정답 전체

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
    task_id = max(app.state.tasks, default=0) + 1
    task = {"id": task_id, "title": body.title}
    app.state.tasks[task_id] = task
    return task


@app.get("/tasks/{task_id}", responses={404: {"description": "작업 없음"}})
def read_task(task_id: Annotated[int, Path(ge=1)]):
    if task_id not in app.state.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return app.state.tasks[task_id]
```

적용: README의 백업·복사 명령으로 solution.py를 main.py에 적용한 뒤 `python -m pytest -q test_api.py`를 실행합니다. Swagger용 Uvicorn도 재시작합니다. 모든 제공 검사 통과가 기대 결과이며 실제 제작 실행 숫자는 VERIFICATION.md를 봅니다.

## 이해도 질문 답

1. **매 테스트 전에 비우면 같은 시나리오 안의 두 생성 사이에도 비우나요?**

   아닙니다. 테스트 함수 한 번의 시작과 끝에만 비웁니다.

2. **두 제목이 같아도 ID가 같아야 하나요?**

   아닙니다. 이 계약에서는 매번 새로운 작업입니다.

3. **이 ID 계산을 다중 서버의 운영 DB에도 그대로 써도 되나요?**

   아닙니다. 이번 실습은 단일 worker·순차 요청이며 원자적 DB ID 발급은 다루지 않습니다.


## 정상 보존과 실패 처리

TEST_CASES의 정상 입력과 오류 입력을 같은 테스트 묶음으로 재실행합니다. 정상 상태만 확인하지 말고 반환 데이터도 확인합니다. AI 테스트의 품질은 사례 개수보다 핵심 결함을 탐지하고 정책과 일치하는지로 봅니다. 1~3차시에서는 pytest 문법 암기보다 출력 비교가 목표입니다.

## 채점·피드백

README의 100점 기준으로 채점하되, 제공 검사를 지우거나 기대값을 실제 결함에 맞춘 경우 완료 처리하지 않습니다. 재현 명령·실제 실패·수정 이유가 있는지 확인합니다. 보고서의 실행 결과는 학생 환경에서 직접 얻은 값이어야 합니다. 미검증 항목을 솔직하게 구분한 것은 감점 사유가 아니라 검증 태도의 일부입니다.

## 범위와 운영 한계

이 차시는 README의 직접 선언 API만 제공합니다. 별도 mock 서버·health·미래 차시 코드가 없습니다. 메모리 상태가 있는 차시는 단일 worker와 순차 요청만 다루며 영속 저장·동시성·성능 검증은 하지 않습니다. response_model과 입력 제약만으로 인증·보안 전체가 해결되는 것은 아닙니다. 학생이 요청하지 않은 심화 구현을 추가하지 않습니다.
