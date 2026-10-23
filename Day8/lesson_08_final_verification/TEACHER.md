# 8차시 강사용 해설

## 수업 의도와 진행

목표: 명세와 업무 규칙을 바탕으로 AI 테스트를 검토하고 실패 후 상태 보존까지 검증 보고서를 완성한다. 학생이 처음에는 결과를 예상하고, 실제 실패를 보고, 원인을 코드로 설명한 뒤 수정하게 합니다. 정답을 먼저 복사하면 재현·분석 학습이 사라집니다. 설치가 끝난 환경을 사전에 준비하고 README의 50분 배분을 사용합니다. AI 도구가 없으면 제공 프롬프트를 동료 검토 질문으로 바꾸어 진행합니다.

교사의 시연은 정상 입력 1개와 핵심 실패 1개로 제한합니다. 나머지는 짝 활동으로 분담하고 전체 제공 검사를 마지막에 실행합니다. 코드 전체는 CODE_GUIDE에 있어 수업 시간에 전부 타이핑할 필요가 없습니다. 학생 질문에서는 상태·본문·문서·상태 변화 중 무엇을 확인했는지 되묻습니다.

## 원인과 최소 수정

- 실제 증상: 3석 예약 뒤 2석 요청은 409이지만 남은 좌석을 -1로 바꿉니다. 이어 1석 정상 요청도 409가 됩니다.
- 원인: 잔여 좌석을 먼저 차감하고 부족 여부를 확인합니다. HTTPException은 이미 바뀐 Python 상태를 자동으로 되돌리지 않습니다.
- 최소 수정: body.seats > app.state.remaining 검사를 차감 전에 수행하고 승인된 경우만 차감·저장합니다.

```diff
--- main.py (시작)
+++ main.py (수정)
@@ -15,9 +15,9 @@
 
 @app.post("/reservations", status_code=201, responses={409: {"description": "좌석 부족"}})
 def create_reservation(body: ReservationIn):
+    if body.seats > app.state.remaining:
+        raise HTTPException(status_code=409, detail="Not enough seats")
     app.state.remaining -= body.seats
-    if app.state.remaining < 0:
-        raise HTTPException(status_code=409, detail="Not enough seats")
     reservation_id = max(app.state.reservations, default=0) + 1
     record = {"id": reservation_id, "name": body.name, "seats": body.seats}
     app.state.reservations[reservation_id] = record
```

## solution.py — 수정 정답 전체

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
    if body.seats > app.state.remaining:
        raise HTTPException(status_code=409, detail="Not enough seats")
    app.state.remaining -= body.seats
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

적용: README의 백업·복사 명령으로 solution.py를 main.py에 적용한 뒤 `python -m pytest -q test_api.py`를 실행합니다. Swagger용 Uvicorn도 재시작합니다. 모든 제공 검사 통과가 기대 결과이며 실제 제작 실행 숫자는 VERIFICATION.md를 봅니다.

## 이해도 질문 답

1. **409를 raise하면 앞에서 바꾼 dict나 숫자도 되돌아가나요?**

   아닙니다. Python 상태 롤백은 자동이 아닙니다.

2. **왜 실패 다음에 정상 요청을 보내나요?**

   오류 응답만 맞고 내부 상태는 손상되는 결함을 찾기 위해서입니다.

3. **이 실습이 운영 예약 시스템을 보장하나요?**

   아닙니다. 순차·단일 worker 메모리 실습이며 DB 트랜잭션과 동시 예약은 별도 검증이 필요합니다.


## 정상 보존과 실패 처리

TEST_CASES의 정상 입력과 오류 입력을 같은 테스트 묶음으로 재실행합니다. 정상 상태만 확인하지 말고 반환 데이터도 확인합니다. AI 테스트의 품질은 사례 개수보다 핵심 결함을 탐지하고 정책과 일치하는지로 봅니다. 1~3차시에서는 pytest 문법 암기보다 출력 비교가 목표입니다.

## 채점·피드백

README의 100점 기준으로 채점하되, 제공 검사를 지우거나 기대값을 실제 결함에 맞춘 경우 완료 처리하지 않습니다. 재현 명령·실제 실패·수정 이유가 있는지 확인합니다. 보고서의 실행 결과는 학생 환경에서 직접 얻은 값이어야 합니다. 미검증 항목을 솔직하게 구분한 것은 감점 사유가 아니라 검증 태도의 일부입니다.

## 범위와 운영 한계

이 차시는 README의 직접 선언 API만 제공합니다. 별도 mock 서버·health·미래 차시 코드가 없습니다. 메모리 상태가 있는 차시는 단일 worker와 순차 요청만 다루며 영속 저장·동시성·성능 검증은 하지 않습니다. response_model과 입력 제약만으로 인증·보안 전체가 해결되는 것은 아닙니다. 학생이 요청하지 않은 심화 구현을 추가하지 않습니다.
