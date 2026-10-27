# 5차시 코드 해설

## 전체 학생 코드 (`main.py`)

```python
def is_ready(value: str) -> bool:
    return bool(value)
```

## 강사용 최소 수정 코드 (`solution.py`)

```python
def is_ready(value: str) -> bool:
    return value.lower() == "true"
```

## 검증 코드 전체 (`check.py`)

```python
import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
ready = importlib.import_module(name).is_ready
print('true:', ready('true'))
print('false:', ready('false'))
assert ready('true') is True
assert ready('false') is False
print('PASS')
```

## 코드 흐름과 역할

`main.py`와 `solution.py`는 **둘 다 동시에 실행하는 파일이 아닙니다.** `check.py` 인자를 통해 하나만 로딩합니다. `check.py`는 입력을 공급하고 출력/상태를 확인합니다. `assert`는 기대가 다를 때 `AssertionError`를 발생시킵니다.

- **오류 원인:** 상태를 문자열 "false"로 보관하고 bool(value)로 검사하여 준비 완료라고 오판한다.
- **최소 수정:** 문자열을 lower() == "true"로 명시적으로 비교한다.
- **핵심 관찰:** 상태를 문자열 "false"로 보관하고 bool(value)로 검사하여 준비 완료라고 오판한다. 정답에서 문자열을 lower() == "true"로 명시적으로 비교한다.
- **비유:** 동료에게 보내는 변경 내역에는 실제로 수정한 내용과 삭제한 내용이 모두 보이도록 하고, 승인 전 검증을 끝냅니다.

## 자주 막히는 지점

- `ModuleNotFoundError` → `lesson_05`에서 가상환경 및 패키지 설치를 확인합니다.
- `AssertionError` → 오류 재현 단계에서 학생 코드 실패는 정상적인 관찰입니다.
- GitHub 접근 실패 → 로컬 Python과 Git 단계까지 수행하고 원격 관련 증빙은 별도 수집합니다.
- AI가 검사 코드를 통과시키기 위해 `assert`를 삭제하자고 하면 거부합니다. 코드를 최소 변경하고 의미 있는 검증을 유지합니다.
