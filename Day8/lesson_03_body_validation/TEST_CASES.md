# 3차시 테스트 설계표

기대값 근거: POST /orders: name은 1~20글자, quantity는 엄격한 정수 1~5이며 둘 다 필수입니다. 추가 필드는 금지합니다. 성공은 201과 name, quantity, total(단가 3000원), 입력 오류는 422입니다. 공백만 있는 이름 정규화는 이번 차시 범위 밖입니다.

| ID | 분류 | 입력·순서 | 기대 결과 | 검사 이유 |
| --- | --- | --- | --- | --- |
| L3-N1 | 정상·경계 | quantity=1 / 5 | 201; total=3000 / 15000 | 정상 계산 |
| L3-E1 | 범위 | quantity=0 / 6 | 422; body.quantity | 하한·상한 밖 |
| L3-E2 | 타입 | quantity="2" / true / null | 422; body.quantity | 엄격한 정수 정책 |
| L3-E3 | 누락 | quantity 누락 / name 누락 | 422; 해당 필드 | 필수값 |
| L3-E4 | 문자열 | name 빈 문자열 / 21글자 | 422; body.name | 길이 |
| L3-E5 | 추가 필드 | admin=true 추가 | 422; body.admin | 추가 필드 금지 |
| L3-D1 | 문서 | OrderIn schema | quantity.minimum=1; required; additionalProperties=false | 문서와 정책 |


이 표는 제작 시 작성·검토한 기준 예시입니다. 학생이 외부 AI를 실제 실행한 대화 기록이 아닙니다. 여러 입력을 /로 표시한 행은 test_api.py에서 각각 별도 입력으로 실행합니다. 상태뿐 아니라 계약에서 중요한 본문·필드·문서·상태 변화를 확인합니다.

## AI 초안 검토 활동

1. CODEX_PROMPTS.md의 생성 프롬프트로 새 표를 요청합니다.
2. 계약에서 기대값을 손으로 계산하고 누락·중복·실행 가능성을 표시합니다.
3. 제공 표와 비교하여 1개 이상 보강 이유를 설명합니다.
4. AI가 만든 test_generated.py를 직접 실행하고 제공 test_api.py도 유지합니다.
5. 통과한 테스트 수만으로 전체 품질을 단정하지 말고 미검증 범위를 적습니다.

