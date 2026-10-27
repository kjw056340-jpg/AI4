# 8차시 | 충돌 해결과 최종 병합: 양쪽 변경을 잃지 않기

**오늘의 질문:** main과 기능 브랜치에서 각각 추가된 Task를 어떻게 안전하게 통합할까?

**학습 목표:** 현재 차시의 결함을 재현·설명·최소 수정하고, 관련 협업 산출물을 기록한다. **선수 지식:** Python 함수·리스트·딕셔너리, `git status/add/commit`, 브랜치와 GitHub PR 기본 개념.

**실습 산출물:** 실패/성공 검사 로그, 변경 코드 diff, Codex 검토 기록, GitHub PR/리뷰 URL(계정 있는 경우).

## 시간표 (설치/심화는 수업 시간 제외)

| 구간 | 실제 활동 |
|---|---|
| 0–5분 | 동료 개발자의 변경 기록 비유와 오류 예측 |
| 5–15분 | 주요 함수와 흐름, 기대 결과 읽기 |
| 15–28분 | `python check.py main` 실행, 실패 재현 |
| 28–40분 | Codex 분석→최소 수정 및 Git 변경내역 확인 |
| 40–47분 | 정답 검사, 결과 비교, 정상 회귀 확인 |
| 47–50분 | 퀴즈·작업 결과 제출 |

## 환경 준비 (별도 시간, Windows CMD)

`lesson_08` 폴더로 이동 후 터미널 A:

```bat
py -m venv .venv
.venv\Scripts\activate
REM Python 표준 라이브러리만 사용. Git 설치 확인: git --version
```

이 차시는 HTTP 서버를 구동하지 않습니다. GitHub 원격 연결은 계정·네트워크가 있을 때 추가 진행하며 로컬 핵심 실습에는 필요하지 않습니다.

터미널 B에서 독립적으로 실행:

```bat
python check.py main
python check.py solution
```

`main`은 의도한 결함 때문에 실패하고 `solution`은 통과해야 합니다. 학생이 `main.py`를 직접 고친 뒤 첫 명령도 통과시키는 것이 과제입니다. macOS/Linux는 `python3 -m venv .venv; source .venv/bin/activate`를 사용합니다.

## 호출 관계

- 웹 API 없음: `check.py`가 `main.py` 또는 `solution.py`의 함수에 직접 입력을 전달.

`check.py` → `importlib.import_module('main' 또는 'solution')` → 해당 차시 도우미 함수 호출 → `assert`로 기대값 검증. 단순 데코레이터 등록은 HTTP 요청 실행과 다릅니다.

**오류:** 서로 다른 변경 목록을 병합하면서 한쪽만 반환해 상대 수정이 소실된다.  **수정:** ID별로 병합해 양쪽의 다른 ID를 유지하고 충돌되는 ID 정책을 명시한다.

**예상 관찰:** 서로 다른 변경 목록을 병합하면서 한쪽만 반환해 상대 수정이 소실된다. 정답에서 ID별로 병합해 양쪽의 다른 ID를 유지하고 충돌되는 ID 정책을 명시한다.

## 학생 활동과 평가

1. 실패 출력의 실제/기대 차이를 기록합니다.
2. Codex에 먼저 원인을 분석하게 하고, 근거를 코드 줄과 연결합니다.
3. `main.py`만 최소 수정해 재검증하고 `solution.py`와 비교합니다.
4. 실패 로그·통과 로그·diff·원인 설명을 제출합니다.

**평가(10점):** 재현 2, 원인 설명 3, 최소 수정 2, 통과 검사 2, 코드/AI 검토 1. **선택 심화**는 별도 제공하지 않음. 본 차시 완료 후 PR 병합 기록과 회고를 제출합니다.

## 파일 설명

- `main.py`: 실패를 재현하는 학생 시작 코드. `python check.py main`에서 로딩.
- `solution.py`: 최소 수정 기준 코드. `python check.py solution`에서 로딩.
- `check.py`: 학습 목표를 정상 입력과 오류 입력으로 확인. 별도 명령으로 직접 실행.
- Python 단일 파일 직접 실행: `python main.py` 또는 `python solution.py`로 도우미 함수의 관찰용 입력을 출력할 수 있습니다.
- `CODE_GUIDE.md`: 코드 전체, 함수·검사 입력/출력, 수정 연결 설명.
- `CODEX_PROMPTS.md`: 분석/수정/검토 3단계 프롬프트.
- `TEACHER.md`: 강사용 풀이, 질문 답, 평가.
- `VERIFICATION.md`: 실제 실행/범위 감사 로그.
- `lesson_scope.json`: 강사용 코드 범위 감사 메타데이터이며 학생 실행 코드가 아닙니다.

## Git 로컬 실습 명령 (Git Bash 또는 CMD)

중요: 신규 빈 실습 폴더 또는 실습 전용 저장소에서 사용하세요. 기존 프로젝트의 파일을 임의 초기화하거나 덮어쓰지 않습니다. 아래의 REM 주석은 Windows CMD 전용입니다. `git init`이 필요한 차시는 새 폴더에서 수행하세요.

```bat
git init -b main
git config user.name "KDT Student"
git config user.email "student@example.invalid"
git add main.py check.py
git commit -m "chore: base"
git switch -c feature/merge-demo
REM feature에서 main.py를 수정한 뒤 git add/commit
git switch main
REM main에서도 같은 줄을 다르게 수정한 뒤 git add/commit
git merge feature/merge-demo
REM 충돌이 발생하면 <<<<<<<, =======, >>>>>>> 표시를 읽고 양쪽 의도를 반영
git add main.py
git commit -m "merge: reconcile both changes"
python check.py main
```

**GitHub 실습:** 실제 GitHub PR에서 필수 검사가 통과하고 리뷰 정책이 충족됐는지 확인 후 Merge pull request를 클릭한다. main 최신 버전을 받아 재검증한다. 실제 리포지토리, 토큰, 조직 정책은 학습자가 직접 정하며 공개하지 않습니다. GitHub 웹 PR은 오프라인 로컬 검사로 실제 생성 여부를 확인할 수 없습니다.

동일 파일의 동일 줄을 양쪽 브랜치에서 다르게 수정하면 Git이 자동으로 선택하지 못할 수 있습니다. 충돌 마커 제거 후 양쪽 의도를 검증하고 `git status`로 unresolved paths가 없는지 확인합니다. 강제 push 대신 리뷰어와 정책을 합의합니다.
