# 8차시 코드 전체와 실행 관계

실제 배포 파일과 동일한 코드입니다. 정답은 TEACHER.md에 분리했습니다.

## main.py — 학생 시작 코드 전체

```python
from typing import Annotated
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="예약 종합 검증 API")
app.state.remaining = 4
app.state.reservations = {}


class ReservationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=20)
    seats: int = Field(ge=1, le=4, strict=True)


@app.post("/reservations", status_code=201, responses={409: {"description": "좌석 부족"}})
def create_reservation(body: ReservationIn):
    app.state.remaining -= body.seats
    if app.state.remaining < 0:
        raise HTTPException(status_code=409, detail="Not enough seats")
    reservation_id = max(app.state.reservations, default=0) + 1
    record = {"id": reservation_id, "name": body.name, "seats": body.seats}
    app.state.reservations[reservation_id] = record
    return {**record, "remaining": app.state.remaining}


@app.get("/reservations/{reservation_id}", responses={404: {"description": "예약 없음"}})
def read_reservation(reservation_id: Annotated[int, Path(ge=1)]):
    if reservation_id not in app.state.reservations:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return app.state.reservations[reservation_id]
```

## 역할과 이유

| 코드·심볼 | 무엇을 하고 왜 필요한가 |
| --- | --- |
| ReservationIn | 허용 범위와 필수 칸, 추가 필드 금지를 선언합니다. |
| remaining / reservations | 잔여 좌석과 승인된 예약 장부입니다. 둘 다 같은 프로세스에서 유지됩니다. |
| create_reservation | 검증 → 잔여 확인 → 차감 → 저장 순서여야 합니다. 시작 코드에서는 확인과 차감이 뒤바뀌었습니다. |
| read_reservation | 거절된 요청을 저장하지 않았는지와 승인된 내용 보존을 조회로 확인합니다. |
| reset_reservations | 테스트마다 4석·빈 장부로 준비합니다. 일반 HTTP 요청으로 노출되는 리셋 API는 만들지 않습니다. |


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
def reset_reservations():
    app.state.remaining = 4
    app.state.reservations.clear()
    yield
    app.state.remaining = 4
    app.state.reservations.clear()


@pytest.mark.parametrize("seats", [1, 4])
def test_create_and_read(seats):
    response = client.post("/reservations", json={"name": "Min", "seats": seats})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Min", "seats": seats, "remaining": 4 - seats}
    read = client.get("/reservations/1")
    assert read.status_code == 200
    assert read.json() == {"id": 1, "name": "Min", "seats": seats}


@pytest.mark.parametrize("first_seats, rejected_seats, final_seats", [(3, 2, 1), (2, 3, 2)])
def test_reject_then_success(first_seats, rejected_seats, final_seats):
    first = client.post("/reservations", json={"name": "A", "seats": first_seats})
    rejected = client.post("/reservations", json={"name": "B", "seats": rejected_seats})
    final = client.post("/reservations", json={"name": "C", "seats": final_seats})
    first_read = client.get("/reservations/1")
    second_read = client.get("/reservations/2")
    assert first.status_code == 201
    assert rejected.status_code == 409
    assert rejected.json() == {"detail": "Not enough seats"}
    assert final.status_code == 201
    assert final.json() == {"id": 2, "name": "C", "seats": final_seats, "remaining": 0}
    assert first_read.json() == {"id": 1, "name": "A", "seats": first_seats}
    assert second_read.status_code == 200
    assert second_read.json() == {"id": 2, "name": "C", "seats": final_seats}


@pytest.mark.parametrize("body, field", [
    ({"name": "A", "seats": 0}, "seats"),
    ({"name": "A", "seats": 5}, "seats"),
    ({"name": "A", "seats": "1"}, "seats"),
    ({"name": "A", "seats": True}, "seats"),
    ({"name": "A"}, "seats"),
    ({"name": "", "seats": 1}, "name"),
    ({"name": "A", "seats": 1, "vip": True}, "vip"),
])
def test_invalid_keeps_state(body, field):
    response = client.post("/reservations", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]
    assert app.state.remaining == 4
    assert app.state.reservations == {}


@pytest.mark.parametrize("reservation_id, status", [(99, 404), (0, 422)])
def test_read_error(reservation_id, status):
    response = client.get(f"/reservations/{reservation_id}")
    assert response.status_code == status
    if status == 404:
        assert response.json() == {"detail": "Reservation not found"}
    else:
        assert response.json()["detail"][0]["loc"] == ["path", "reservation_id"]


@pytest.mark.parametrize("path, method, status", [
    ("/reservations", "post", "409"),
    ("/reservations/{reservation_id}", "get", "404"),
])
def test_final_document(path, method, status):
    schema = client.get("/openapi.json").json()
    assert status in schema["paths"][path][method]["responses"]
    model = schema["components"]["schemas"]["ReservationIn"]
    assert model["properties"]["seats"]["minimum"] == 1
    assert model["properties"]["seats"]["maximum"] == 4
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
