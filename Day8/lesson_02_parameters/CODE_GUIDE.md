# 2차시 코드 전체와 실행 관계

실제 배포 파일과 동일한 코드입니다. 정답은 TEACHER.md에 분리했습니다.

## main.py — 학생 시작 코드 전체

```python
from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI(title="상품 수량 API")


@app.get("/items/{item_id}", summary="상품 수량 계산")
def read_item(
    item_id: Annotated[int, Path(ge=1)],
    qty: Annotated[int, Query(ge=1, le=5)] = 2,
):
    return {"item_id": item_id, "qty": qty, "total": qty * 1000}
```

## 역할과 이유

| 코드·심볼 | 무엇을 하고 왜 필요한가 |
| --- | --- |
| Annotated / Path / Query | int 타입에 위치·범위 조건을 붙입니다. item_id는 경로, qty는 쿼리입니다. |
| = 2 | 현재 의도한 오류입니다. 생략 시 2가 들어가며 문서에도 2가 표시됩니다. |
| ge / le | 각각 이상·이하입니다. 양 끝값도 포함합니다. |
| read_item | 검증 성공 후만 실행됩니다. 곱셈 결과를 JSON으로 반환합니다. |
| detail.loc | 실패한 입력 위치입니다. 긴 영문 메시지 전체 대신 필드 위치를 검증합니다. |


## 호출 흐름

브라우저 Swagger Execute 또는 curl → Uvicorn 127.0.0.1:8000 → FastAPI 입력 검증 → 위 경로 함수 → JSON HTTP 응답입니다. 자동 검사는 `python -m pytest -q test_api.py` → pytest가 테스트 함수 호출 → TestClient → 같은 앱의 경로 함수 → assert 비교입니다. TestClient는 외부 네트워크를 통과하지 않습니다.

모델 클래스는 선언이고 요청마다 모델 검증이 일어납니다. 데코레이터는 경로 등록이며 요청 전송이 아닙니다. pytest의 parametrize는 입력 행별 테스트를 등록하고 pytest 실행 시 각 함수를 호출합니다. 테스트 파일의 import 시 TestClient를 준비하지만 실제 API 함수는 client.get/post에서 실행됩니다.

## test_api.py — 준비된 검사 코드 전체

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("params, qty", [({}, 1), ({"qty": 1}, 1), ({"qty": 5}, 5)])
def test_valid_quantity(params, qty):
    response = client.get("/items/1", params=params)
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "qty": qty, "total": qty * 1000}


@pytest.mark.parametrize("url, field", [
    ("/items/0", "item_id"), ("/items/abc", "item_id"),
    ("/items/1?qty=0", "qty"), ("/items/1?qty=6", "qty"),
    ("/items/1?qty=abc", "qty"),
])
def test_invalid_quantity(url, field):
    response = client.get(url)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == field


@pytest.mark.parametrize("field, default", [("qty", 1)])
def test_document_default(field, default):
    schema = client.get("/openapi.json").json()
    parameters = schema["paths"]["/items/{item_id}"]["get"]["parameters"]
    parameter = next(p for p in parameters if p["name"] == field)
    assert parameter["in"] == "query"
    assert parameter["required"] is False
    assert parameter["schema"]["default"] == default
    assert parameter["schema"]["minimum"] == 1
    assert parameter["schema"]["maximum"] == 5
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
