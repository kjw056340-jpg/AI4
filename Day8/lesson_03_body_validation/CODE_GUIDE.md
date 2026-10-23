# 3차시 코드 전체와 실행 관계

실제 배포 파일과 동일한 코드입니다. 정답은 TEACHER.md에 분리했습니다.

## main.py — 학생 시작 코드 전체

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="주문 검증 API")


class OrderIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=20)
    quantity: int = Field(ge=0, le=5, strict=True)


@app.post("/orders", status_code=201, summary="주문 금액 계산")
def create_order(order: OrderIn):
    return {"name": order.name, "quantity": order.quantity, "total": order.quantity * 3000}
```

## 역할과 이유

| 코드·심볼 | 무엇을 하고 왜 필요한가 |
| --- | --- |
| OrderIn(BaseModel) | 식당 주문서의 모양을 선언합니다. 요청이 들어올 때 FastAPI가 검증에 사용합니다. |
| ConfigDict(extra="forbid") | 선언하지 않은 admin 같은 칸을 입력 오류로 거부합니다. |
| Field / strict=True | 허용 범위와 타입 변환 정책을 지정합니다. bool도 엄격한 정수가 아니므로 거부합니다. |
| create_order(order: OrderIn) | 검증된 객체만 받습니다. 유효하지 않은 요청은 함수 본문 전에 422가 됩니다. |
| json=body | TestClient가 dict를 JSON 요청 본문으로 전송합니다. 문자열을 dict로 가장하지 않습니다. |


## 호출 흐름

브라우저 Swagger Execute 또는 curl → Uvicorn 127.0.0.1:8000 → FastAPI 입력 검증 → 위 경로 함수 → JSON HTTP 응답입니다. 자동 검사는 `python -m pytest -q test_api.py` → pytest가 테스트 함수 호출 → TestClient → 같은 앱의 경로 함수 → assert 비교입니다. TestClient는 외부 네트워크를 통과하지 않습니다.

모델 클래스는 선언이고 요청마다 모델 검증이 일어납니다. 데코레이터는 경로 등록이며 요청 전송이 아닙니다. pytest의 parametrize는 입력 행별 테스트를 등록하고 pytest 실행 시 각 함수를 호출합니다. 테스트 파일의 import 시 TestClient를 준비하지만 실제 API 함수는 client.get/post에서 실행됩니다.

## test_api.py — 준비된 검사 코드 전체

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("quantity", [1, 5])
def test_order_valid(quantity):
    response = client.post("/orders", json={"name": "tea", "quantity": quantity})
    assert response.status_code == 201
    assert response.json() == {"name": "tea", "quantity": quantity, "total": quantity * 3000}


@pytest.mark.parametrize("body, field", [
    ({"name": "tea", "quantity": 0}, "quantity"),
    ({"name": "tea", "quantity": 6}, "quantity"),
    ({"name": "tea", "quantity": "2"}, "quantity"),
    ({"name": "tea", "quantity": True}, "quantity"),
    ({"name": "tea", "quantity": None}, "quantity"),
    ({"name": "tea"}, "quantity"),
    ({"quantity": 1}, "name"),
    ({"name": "", "quantity": 1}, "name"),
    ({"name": "x" * 21, "quantity": 1}, "name"),
    ({"name": "tea", "quantity": 1, "admin": True}, "admin"),
])
def test_order_invalid(body, field):
    response = client.post("/orders", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]


@pytest.mark.parametrize("field, minimum", [("quantity", 1)])
def test_order_schema(field, minimum):
    schema = client.get("/openapi.json").json()
    model = schema["components"]["schemas"]["OrderIn"]
    assert model["properties"][field]["minimum"] == minimum
    assert set(model["required"]) == {"name", "quantity"}
    assert model["additionalProperties"] is False
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
