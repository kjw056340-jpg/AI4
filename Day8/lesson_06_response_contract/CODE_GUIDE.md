# 6차시 코드 전체와 실행 관계

실제 배포 파일과 동일한 코드입니다. 정답은 TEACHER.md에 분리했습니다.

## main.py — 학생 시작 코드 전체

```python
from typing import Annotated
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

app = FastAPI(title="프로필 응답 API")


class ProfileOut(BaseModel):
    id: int
    name: str
    internal_note: str


profiles = {1: {"id": 1, "name": "Min", "internal_note": "staff only"}}


@app.get("/profiles/{profile_id}", response_model=ProfileOut, responses={404: {"description": "프로필 없음"}})
def read_profile(profile_id: Annotated[int, Path(ge=1)]):
    record = profiles.get(profile_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return record
```

## 역할과 이유

| 코드·심볼 | 무엇을 하고 왜 필요한가 |
| --- | --- |
| ProfileOut | 외부 응답 모델입니다. 시작 코드에는 id/name 외에 내부 메모도 잘못 선언되어 있습니다. 수정 후 id/name만 남깁니다. |
| profiles | 직원용 메모까지 담긴 내부 가상 데이터입니다. 조회에서 실제 사용합니다. |
| response_model | ProfileOut에 선언된 필드를 공개 응답으로 검증·직렬화합니다. 모델에 내부 필드를 선언하면 그 필드도 응답과 문서에 포함됩니다. |
| read_profile | 내부 데이터를 찾고 없으면 404를 발생시킵니다. |
| set / not in 검사 | 필드가 맞는지뿐 아니라 공개하면 안 되는 필드가 없는지도 검사합니다. |


## 호출 흐름

브라우저 Swagger Execute 또는 curl → Uvicorn 127.0.0.1:8000 → FastAPI 입력 검증 → 위 경로 함수 → JSON HTTP 응답입니다. 자동 검사는 `python -m pytest -q test_api.py` → pytest가 테스트 함수 호출 → TestClient → 같은 앱의 경로 함수 → assert 비교입니다. TestClient는 외부 네트워크를 통과하지 않습니다.

모델 클래스는 선언이고 요청마다 모델 검증이 일어납니다. 데코레이터는 경로 등록이며 요청 전송이 아닙니다. pytest의 parametrize는 입력 행별 테스트를 등록하고 pytest 실행 시 각 함수를 호출합니다. 테스트 파일의 import 시 TestClient를 준비하지만 실제 API 함수는 client.get/post에서 실행됩니다.

## test_api.py — 준비된 검사 코드 전체

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("profile_id, status", [(1, 200), (99, 404), (0, 422)])
def test_profile(profile_id, status):
    response = client.get(f"/profiles/{profile_id}")
    assert response.status_code == status
    if status == 200:
        assert response.json() == {"id": 1, "name": "Min"}
        assert "internal_note" not in response.json()
    elif status == 404:
        assert response.json() == {"detail": "Profile not found"}
    else:
        assert response.json()["detail"][0]["loc"] == ["path", "profile_id"]


@pytest.mark.parametrize("path", ["/profiles/{profile_id}"])
def test_response_schema(path):
    schema = client.get("/openapi.json").json()
    response = schema["paths"][path]["get"]["responses"]["200"]
    assert response["content"]["application/json"]["schema"].get("$ref") == "#/components/schemas/ProfileOut"
    model = schema["components"]["schemas"]["ProfileOut"]
    assert set(model["properties"]) == {"id", "name"}
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
