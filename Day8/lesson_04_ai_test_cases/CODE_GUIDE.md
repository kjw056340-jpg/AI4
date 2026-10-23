# 4차시 코드 전체와 실행 관계

실제 배포 파일과 동일한 코드입니다. 정답은 TEACHER.md에 분리했습니다.

## main.py — 학생 시작 코드 전체

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="할인 견적 API")


class QuoteIn(BaseModel):
    amount: int = Field(ge=1, le=100000, strict=True)


def calculate_discount(amount: int):
    return 1000 if amount > 10000 else 0


@app.post("/quotes", summary="할인 견적")
def quote(body: QuoteIn):
    discount = calculate_discount(body.amount)
    return {"amount": body.amount, "discount": discount, "payable": body.amount - discount}
```

## 역할과 이유

| 코드·심볼 | 무엇을 하고 왜 필요한가 |
| --- | --- |
| calculate_discount | API가 호출하는 보조 함수입니다. 실제 결함 위치를 찾으려면 호출을 한 단계 더 따라가야 합니다. |
| quote → calculate_discount | 요청 검증 후 보조 함수로 할인액을 계산하고 payable을 만듭니다. |
| pytest.mark.parametrize | 한 테스트 함수를 여러 입력·기대값 행으로 실행합니다. 7개 행은 7개 검사입니다. |
| assert response.json() | 상태 200 외에 계산 결과까지 확인합니다. 잘못된 할인도 200일 수 있습니다. |
| test_seed.py | 의도적으로 불충분한 2개 정상 검사입니다. 비교 실습에 실제 실행하며 최종 완료 기준은 test_api.py입니다. |


## 호출 흐름

브라우저 Swagger Execute 또는 curl → Uvicorn 127.0.0.1:8000 → FastAPI 입력 검증 → 위 경로 함수 → JSON HTTP 응답입니다. 자동 검사는 `python -m pytest -q test_api.py` → pytest가 테스트 함수 호출 → TestClient → 같은 앱의 경로 함수 → assert 비교입니다. TestClient는 외부 네트워크를 통과하지 않습니다.

모델 클래스는 선언이고 요청마다 모델 검증이 일어납니다. 데코레이터는 경로 등록이며 요청 전송이 아닙니다. pytest의 parametrize는 입력 행별 테스트를 등록하고 pytest 실행 시 각 함수를 호출합니다. 테스트 파일의 import 시 TestClient를 준비하지만 실제 API 함수는 client.get/post에서 실행됩니다.

## test_api.py — 준비된 검사 코드 전체

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("amount, discount, payable", [
    (1, 0, 1), (5000, 0, 5000), (9999, 0, 9999),
    (10000, 1000, 9000), (10001, 1000, 9001),
    (20000, 1000, 19000), (100000, 1000, 99000),
])
def test_quote(amount, discount, payable):
    response = client.post("/quotes", json={"amount": amount})
    assert response.status_code == 200
    assert response.json() == {"amount": amount, "discount": discount, "payable": payable}


@pytest.mark.parametrize("body", [{"amount": 0}, {"amount": 100001}, {"amount": "10000"}, {}])
def test_quote_invalid(body):
    response = client.post("/quotes", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "amount"]
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

## test_seed.py — 실행하여 한계를 확인하는 초안

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("amount, payable", [(5000, 5000), (20000, 19000)])
def test_seed_quote(amount, payable):
    response = client.post("/quotes", json={"amount": amount})
    assert response.status_code == 200
    assert response.json()["payable"] == payable
```
