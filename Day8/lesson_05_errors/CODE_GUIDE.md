# 5차시 코드 전체와 실행 관계

실제 배포 파일과 동일한 코드입니다. 정답은 TEACHER.md에 분리했습니다.

## main.py — 학생 시작 코드 전체

```python
from typing import Annotated
from fastapi import FastAPI, HTTPException, Path

app = FastAPI(title="상품 오류 API")
products = {1: {"id": 1, "name": "tea"}}


def find_product(product_id: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]


@app.get("/products/{product_id}", responses={404: {"description": "상품 없음"}})
def read_product(product_id: Annotated[int, Path(ge=1)]):
    try:
        return find_product(product_id)
    except Exception:
        return {"id": product_id, "name": "unknown"}
```

## 역할과 이유

| 코드·심볼 | 무엇을 하고 왜 필요한가 |
| --- | --- |
| products | 이번 차시의 읽기 전용 작은 상품 사전입니다. 서버·DB는 추가하지 않습니다. |
| find_product | 사전에 없는 양수 ID라면 HTTPException을 발생시킵니다. |
| raise HTTPException | return과 다릅니다. 요청 처리를 중단하고 FastAPI가 지정한 HTTP 응답을 만듭니다. |
| except Exception | HTTPException도 잡는 의도한 결함입니다. 예외를 정상 응답으로 바꾸지 않아야 합니다. |
| responses={404: ...} | 문서에 설명을 추가합니다. 이 설정 자체가 404를 발생시키지는 않습니다. |


## 호출 흐름

브라우저 Swagger Execute 또는 curl → Uvicorn 127.0.0.1:8000 → FastAPI 입력 검증 → 위 경로 함수 → JSON HTTP 응답입니다. 자동 검사는 `python -m pytest -q test_api.py` → pytest가 테스트 함수 호출 → TestClient → 같은 앱의 경로 함수 → assert 비교입니다. TestClient는 외부 네트워크를 통과하지 않습니다.

모델 클래스는 선언이고 요청마다 모델 검증이 일어납니다. 데코레이터는 경로 등록이며 요청 전송이 아닙니다. pytest의 parametrize는 입력 행별 테스트를 등록하고 pytest 실행 시 각 함수를 호출합니다. 테스트 파일의 import 시 TestClient를 준비하지만 실제 API 함수는 client.get/post에서 실행됩니다.

## test_api.py — 준비된 검사 코드 전체

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("product_id, status, expected", [
    (1, 200, {"id": 1, "name": "tea"}),
    (99, 404, {"detail": "Product not found"}),
])
def test_product(product_id, status, expected):
    response = client.get(f"/products/{product_id}")
    assert response.status_code == status
    assert response.json() == expected


@pytest.mark.parametrize("product_id", ["0", "abc"])
def test_product_invalid(product_id):
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "product_id"]


@pytest.mark.parametrize("status", ["200", "404", "422"])
def test_error_document(status):
    schema = client.get("/openapi.json").json()
    assert status in schema["paths"]["/products/{product_id}"]["get"]["responses"]
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
