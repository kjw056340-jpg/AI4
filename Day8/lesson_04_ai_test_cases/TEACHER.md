# 4차시 강사용 해설

## 수업 의도와 진행

목표: 업무 규칙에서 테스트 기대값을 계산하고 AI 초안의 누락을 찾아 매개변수화 테스트로 검증한다. 학생이 처음에는 결과를 예상하고, 실제 실패를 보고, 원인을 코드로 설명한 뒤 수정하게 합니다. 정답을 먼저 복사하면 재현·분석 학습이 사라집니다. 설치가 끝난 환경을 사전에 준비하고 README의 50분 배분을 사용합니다. AI 도구가 없으면 제공 프롬프트를 동료 검토 질문으로 바꾸어 진행합니다.

교사의 시연은 정상 입력 1개와 핵심 실패 1개로 제한합니다. 나머지는 짝 활동으로 분담하고 전체 제공 검사를 마지막에 실행합니다. 코드 전체는 CODE_GUIDE에 있어 수업 시간에 전부 타이핑할 필요가 없습니다. 학생 질문에서는 상태·본문·문서·상태 변화 중 무엇을 확인했는지 되묻습니다.

## 원인과 최소 수정

- 실제 증상: amount=10000일 때 discount=0, payable=10000으로 반환되어 약속한 1000원 할인이 누락됩니다.
- 원인: calculate_discount 보조 함수가 > 10000으로 비교합니다. 5000과 20000만 검사하면 결함이 드러나지 않습니다.
- 최소 수정: 보조 함수의 >를 >=로 바꿉니다. 기대값이나 테스트 개수를 줄이는 편법은 금지합니다.

```diff
--- main.py (시작)
+++ main.py (수정)
@@ -9,7 +9,7 @@
 
 
 def calculate_discount(amount: int):
-    return 1000 if amount > 10000 else 0
+    return 1000 if amount >= 10000 else 0
 
 
 @app.post("/quotes", summary="할인 견적")
```

## solution.py — 수정 정답 전체

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="할인 견적 API")


class QuoteIn(BaseModel):
    amount: int = Field(ge=1, le=100000, strict=True)


def calculate_discount(amount: int):
    return 1000 if amount >= 10000 else 0


@app.post("/quotes", summary="할인 견적")
def quote(body: QuoteIn):
    discount = calculate_discount(body.amount)
    return {"amount": body.amount, "discount": discount, "payable": body.amount - discount}
```

적용: README의 백업·복사 명령으로 solution.py를 main.py에 적용한 뒤 `python -m pytest -q test_api.py`를 실행합니다. Swagger용 Uvicorn도 재시작합니다. 모든 제공 검사 통과가 기대 결과이며 실제 제작 실행 숫자는 VERIFICATION.md를 봅니다.

## 이해도 질문 답

1. **왜 10000만 틀리고 20000은 맞나요?**

   >와 >=의 차이는 정확한 경계에서 나타납니다.

2. **명세만 AI에게 주면 할인 규칙을 알 수 있나요?**

   완전히 알 수 없습니다. 업무 계약과 기대값 근거를 같이 주어야 합니다.

3. **모든 테스트가 통과하면 버그가 없나요?**

   검사한 범위만 뒷받침합니다. 누락 사례와 한계도 검토해야 합니다.


## 정상 보존과 실패 처리

TEST_CASES의 정상 입력과 오류 입력을 같은 테스트 묶음으로 재실행합니다. 정상 상태만 확인하지 말고 반환 데이터도 확인합니다. AI 테스트의 품질은 사례 개수보다 핵심 결함을 탐지하고 정책과 일치하는지로 봅니다. 1~3차시에서는 pytest 문법 암기보다 출력 비교가 목표입니다.

## 채점·피드백

README의 100점 기준으로 채점하되, 제공 검사를 지우거나 기대값을 실제 결함에 맞춘 경우 완료 처리하지 않습니다. 재현 명령·실제 실패·수정 이유가 있는지 확인합니다. 보고서의 실행 결과는 학생 환경에서 직접 얻은 값이어야 합니다. 미검증 항목을 솔직하게 구분한 것은 감점 사유가 아니라 검증 태도의 일부입니다.

## 범위와 운영 한계

이 차시는 README의 직접 선언 API만 제공합니다. 별도 mock 서버·health·미래 차시 코드가 없습니다. 메모리 상태가 있는 차시는 단일 worker와 순차 요청만 다루며 영속 저장·동시성·성능 검증은 하지 않습니다. response_model과 입력 제약만으로 인증·보안 전체가 해결되는 것은 아닙니다. 학생이 요청하지 않은 심화 구현을 추가하지 않습니다.
