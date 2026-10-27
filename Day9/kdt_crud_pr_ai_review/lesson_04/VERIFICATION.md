# 실제 실행 검증과 범위 감사

실행 환경: Python 3.13.5; `python check.py main|solution`을 각 lesson 폴더에서 실행.

## main: 종료 코드 1

```text
DELETE /tasks/3: 500
Traceback (most recent call last):
  File "/mnt/data/kdt_crud_pr_ai_review/lesson_04/check.py", line 16, in <module>
    assert removed.status_code == 204, "Task ID를 리스트 인덱스로 잘못 사용했을 수 있습니다"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Task ID를 리스트 인덱스로 잘못 사용했을 수 있습니다

```

## solution: 종료 코드 0

```text
DELETE /tasks/3: 204
remaining IDs: [1, 4]
PASS

```

## 스킬 범위 감사 스크립트

```text
PASS: 파일·API 명세 일치 및 정적 후보 검사 통과
필수 수동 확인: 근거가 실제 호출인지, 동적 경로·미사용 지역변수·의존성·차시간 혼입 여부.
이 검사는 실행 검증이나 의미적 사용 여부의 완전한 증명이 아닙니다.
```

수동 감사: 현재 차시와 직접 관련된 코드만 포함하며 파일 목적과 호출 근거를 대조. GitHub 원격 push/PR/리뷰/병합은 계정·인증이 없어 실제 수행하지 않음. 독립 단일 프로세스 메모리 실습만 검증.
