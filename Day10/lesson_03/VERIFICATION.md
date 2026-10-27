# 실제 실행 검증·범위 감사

검증일: 2026-10-27 (한국 기준).
실제 환경: Linux, Python 3.12.14, SQLite 3.53.1.
외부 패키지 없이 실제 임시 DB 파일에서 실행했다.

## 수집한 출력

### python check.py main

```text
PASS normal_commit
  expected=[(1, '민지', 90), (2, '준호', 95)]
  actual=[(1, '민지', 90), (2, '준호', 95)]; error=None; counts=(1, 1)
FAIL missing_delete_rolls_back_update
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 90), (2, '준호', 95), (3, '수아', 70)]; error=<class 'ValueError'>; counts=None
PASS missing_update_preserves_all
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'ValueError'>; counts=None
PASS null_points_rejected
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'sqlite3.IntegrityError'>; counts=None
PASS zero_points_is_valid
  expected=[(1, '민지', 0), (2, '준호', 95)]
  actual=[(1, '민지', 0), (2, '준호', 95)]; error=None; counts=(1, 1)
PASS different_delete_target
  expected=[(1, '민지', 90), (3, '수아', 70)]
  actual=[(1, '민지', 90), (3, '수아', 70)]; error=None; counts=(1, 1)
RESULT failures=1
EXIT=1
```

### python check.py solution

```text
PASS normal_commit
  expected=[(1, '민지', 90), (2, '준호', 95)]
  actual=[(1, '민지', 90), (2, '준호', 95)]; error=None; counts=(1, 1)
PASS missing_delete_rolls_back_update
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'ValueError'>; counts=None
PASS missing_update_preserves_all
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'ValueError'>; counts=None
PASS null_points_rejected
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'sqlite3.IntegrityError'>; counts=None
PASS zero_points_is_valid
  expected=[(1, '민지', 0), (2, '준호', 95)]
  actual=[(1, '민지', 0), (2, '준호', 95)]; error=None; counts=(1, 1)
PASS different_delete_target
  expected=[(1, '민지', 90), (3, '수아', 70)]
  actual=[(1, '민지', 90), (3, '수아', 70)]; error=None; counts=(1, 1)
RESULT failures=0
EXIT=0
```

### python main.py

```text
변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
수정·삭제 행 수: (1, 1)
재연결 결과: [(1, '민지', 90), (2, '준호', 95)]
EXIT=0
```

### python main.py --delete-id 999

```text
변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
오류: 삭제 대상은 정확히 1명이어야 합니다.
재연결 결과: [(1, '민지', 90), (2, '준호', 95), (3, '수아', 70)]
EXIT=1
```

### python reproduce.py

```text
SQL: UPDATE users SET points = 0
변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
영향 행 수: 3
확정 전: [(1, '민지', 0), (2, '준호', 0), (3, '수아', 0)]
되돌린 뒤: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
SQL: DELETE FROM users
변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
영향 행 수: 3
확정 전: []
되돌린 뒤: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
EXIT=0
```

### python check.py main — 한 줄 제거 후

```text
PASS normal_commit
  expected=[(1, '민지', 90), (2, '준호', 95)]
  actual=[(1, '민지', 90), (2, '준호', 95)]; error=None; counts=(1, 1)
PASS missing_delete_rolls_back_update
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'ValueError'>; counts=None
PASS missing_update_preserves_all
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'ValueError'>; counts=None
PASS null_points_rejected
  expected=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
  actual=[(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]; error=<class 'sqlite3.IntegrityError'>; counts=None
PASS zero_points_is_valid
  expected=[(1, '민지', 0), (2, '준호', 95)]
  actual=[(1, '민지', 0), (2, '준호', 95)]; error=None; counts=(1, 1)
PASS different_delete_target
  expected=[(1, '민지', 90), (3, '수아', 70)]
  actual=[(1, '민지', 90), (3, '수아', 70)]; error=None; counts=(1, 1)
RESULT failures=0
EXIT=0
```

### python main.py --delete-id 999 — 한 줄 제거 후

```text
변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
오류: 삭제 대상은 정확히 1명이어야 합니다.
재연결 결과: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
EXIT=1
```

### python main.py — 한 줄 제거 후

```text
변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
수정·삭제 행 수: (1, 1)
재연결 결과: [(1, '민지', 90), (2, '준호', 95)]
EXIT=0
```

## 확인 결과

- 시작 main은 정상 수정·삭제를 통과하지만 삭제 대상 누락 시 수정 점수 90이 남는 오류를 재현했다.
- 중간 commit 한 줄 제거 후 main과 solution 모두 정상·대상 누락·NULL·0점·다른 삭제 대상 여섯 검사를 통과했다.
- CLI로 정상 결과는 유지되고 실패 결과는 원본 세 행으로 되돌아오는지 확인했다.
- WHERE 없는 UPDATE·DELETE는 각각 3행에 영향을 주며 rollback 뒤 원본 전체가 복원됐다.
- 매 사례에서 작업 종료 후 별도 연결의 전체 행과 정상 반환 (1, 1) 또는 예외 타입을 비교했다.
- main.py는 수정 재검사 후 의도한 버그가 있는 시작 코드로 복원했다.

## 범위 감사

스킬의 audit_lesson_scope.py lesson_03을 실행해 종료 코드 0을 확인했다.

수동 의미 검토:

- prepare_database·read_users·apply_changes는 CLI·검사에서 실제 호출된다.
- reproduce.py는 main의 준비·조회 함수를 실제 사용하고 WHERE 누락 두 문장을 각 임시 DB에서 실행한다.
- 표와 세 원본 행은 수정 대상·변경하지 않을 행·삭제 대상으로 모두 사용한다.
- UPDATE·DELETE의 WHERE와 ? 값 순서, rowcount 검사, 정상·ValueError·IntegrityError 분기를 실행했다.
- 준비 commit·업무 commit·rollback·finally close·임시 폴더 정리를 현재 실습 흐름과 연결했다.
- 정상 출력 counts와 검사 반환 tuple, 새 연결 SELECT 네트워크 없는 파일 동작을 대조했다.
- 모든 import·지역 변수는 현재 실행·오류 재현·검증에 사용된다.
- 직접 선언 HTTP 경로가 없으므로 routes는 빈 배열이다. 외부 의존성·통합 모의 서버는 없다.
- 앞 차시 파일에 의존하지 않고 다음 차시 제약·관계·로그인 기능을 섞지 않았다.
- README의 전체 Python 코드와 배포 파일을 대조했다.
- 실행 명령은 python으로 통일했고 대상·기본 구성·제작 상태 소개 문구를 제외했다.

정적 통과가 모든 코드 사용 의미의 완전한 증명은 아니다. 실제 실행과 위 수동 검토를 함께 수행했다.

## 검증 한계

Windows CMD 자체에서는 실행하지 않았다. 문서의 경로·명령·인자는 실제 파일과 대조했다.
독립된 Codex 세션 응답 품질을 별도 측정하지 않았다. 프롬프트는 분석·수정·검토 활동 안내다.
여러 프로세스의 동시 쓰기, 파일 접근 권한, 인증·외래키 관계는 검증하지 않았다.

## 압축 확인

내부 파일 목록·경로·압축 무결성과 캐시·가상환경·실제 DB·스킬 소스 제외 여부를 확인했다.
