# 5차시 강사용 해설

## 수업 의도와 진행

목표: 정상·없는 자원·입력 오류를 분리하고 넓은 예외 처리가 숨긴 결함을 회귀 테스트로 고친다. 학생이 처음에는 결과를 예상하고, 실제 실패를 보고, 원인을 코드로 설명한 뒤 수정하게 합니다. 정답을 먼저 복사하면 재현·분석 학습이 사라집니다. 설치가 끝난 환경을 사전에 준비하고 README의 50분 배분을 사용합니다. AI 도구가 없으면 제공 프롬프트를 동료 검토 질문으로 바꾸어 진행합니다.

교사의 시연은 정상 입력 1개와 핵심 실패 1개로 제한합니다. 나머지는 짝 활동으로 분담하고 전체 제공 검사를 마지막에 실행합니다. 코드 전체는 CODE_GUIDE에 있어 수업 시간에 전부 타이핑할 필요가 없습니다. 학생 질문에서는 상태·본문·문서·상태 변화 중 무엇을 확인했는지 되묻습니다.

## 원인과 최소 수정

- 실제 증상: GET /products/99가 404 대신 200과 {id:99,name:unknown}을 반환합니다.
- 원인: find_product가 올바른 HTTPException(404)을 raise하지만 경로 함수의 except Exception이 이를 잡고 가짜 정상 상품을 반환합니다.
- 최소 수정: 경로 함수의 넓은 try/except를 없애 find_product의 HTTPException이 FastAPI에 도달하게 합니다.

```diff
--- main.py (시작)
+++ main.py (수정)
@@ -13,7 +13,4 @@
 
 @app.get("/products/{product_id}", responses={404: {"description": "상품 없음"}})
 def read_product(product_id: Annotated[int, Path(ge=1)]):
-    try:
-        return find_product(product_id)
-    except Exception:
-        return {"id": product_id, "name": "unknown"}
+    return find_product(product_id)
```

## solution.py — 수정 정답 전체

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
    return find_product(product_id)
```

적용: README의 백업·복사 명령으로 solution.py를 main.py에 적용한 뒤 `python -m pytest -q test_api.py`를 실행합니다. Swagger용 Uvicorn도 재시작합니다. 모든 제공 검사 통과가 기대 결과이며 실제 제작 실행 숫자는 VERIFICATION.md를 봅니다.

## 이해도 질문 답

1. **404 선언만 넣으면 실제 404가 반환되나요?**

   아닙니다. 실제 경로 코드에서 raise가 필요합니다.

2. **왜 abc는 except까지 오지 않나요?**

   경로 입력 검증에서 실패해 함수 본문 전에 422가 됩니다.

3. **except를 없애면 1번 상품도 실패하나요?**

   정상 사전 조회는 그대로 동작하며 테스트로 확인합니다.


## 정상 보존과 실패 처리

TEST_CASES의 정상 입력과 오류 입력을 같은 테스트 묶음으로 재실행합니다. 정상 상태만 확인하지 말고 반환 데이터도 확인합니다. AI 테스트의 품질은 사례 개수보다 핵심 결함을 탐지하고 정책과 일치하는지로 봅니다. 1~3차시에서는 pytest 문법 암기보다 출력 비교가 목표입니다.

## 채점·피드백

README의 100점 기준으로 채점하되, 제공 검사를 지우거나 기대값을 실제 결함에 맞춘 경우 완료 처리하지 않습니다. 재현 명령·실제 실패·수정 이유가 있는지 확인합니다. 보고서의 실행 결과는 학생 환경에서 직접 얻은 값이어야 합니다. 미검증 항목을 솔직하게 구분한 것은 감점 사유가 아니라 검증 태도의 일부입니다.

## 범위와 운영 한계

이 차시는 README의 직접 선언 API만 제공합니다. 별도 mock 서버·health·미래 차시 코드가 없습니다. 메모리 상태가 있는 차시는 단일 worker와 순차 요청만 다루며 영속 저장·동시성·성능 검증은 하지 않습니다. response_model과 입력 제약만으로 인증·보안 전체가 해결되는 것은 아닙니다. 학생이 요청하지 않은 심화 구현을 추가하지 않습니다.
