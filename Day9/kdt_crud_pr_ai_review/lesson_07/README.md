# 7차시 | AI 코드 리뷰와 댓글 반영: 재현 가능한 지적만 수용

**오늘의 질문:** AI가 관리자 검사 문제를 지적하면 증거로 확인할 수 있을까?

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

`lesson_07` 폴더로 이동 후 터미널 A:

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

**오류:** "admin" in role 때문에 "not-admin"을 관리자로 잘못 허용한다.  **수정:** role == "admin"으로 정확히 일치하는지 확인한다.

**예상 관찰:** "admin" in role 때문에 "not-admin"을 관리자로 잘못 허용한다. 정답에서 role == "admin"으로 정확히 일치하는지 확인한다.

## 학생 활동과 평가

1. 실패 출력의 실제/기대 차이를 기록합니다.
2. Codex에 먼저 원인을 분석하게 하고, 근거를 코드 줄과 연결합니다.
3. `main.py`만 최소 수정해 재검증하고 `solution.py`와 비교합니다.
4. 실패 로그·통과 로그·diff·원인 설명을 제출합니다.

**평가(10점):** 재현 2, 원인 설명 3, 최소 수정 2, 통과 검사 2, 코드/AI 검토 1. **선택 심화**는 별도 제공하지 않음. 다음 차시: 8차시 개념으로 이동하며 해당 코드는 이 ZIP에 넣지 않았습니다.

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
git commit -m "chore: initial demo"
git switch -c feature/review-permission
python check.py main
REM 분석 및 수정 후:
python check.py main
git add main.py
git commit -m "fix: exact admin role comparison"
git show --stat --oneline HEAD
```

**GitHub 실습:** 열려 있는 PR의 Files changed에서 변경 줄에 리뷰 댓글을 남기고, 수정 커밋을 같은 브랜치에 push하면 PR에 자동으로 추가됨. 리뷰의 승인 여부는 저장소 설정에 따라 다름. 실제 리포지토리, 토큰, 조직 정책은 학습자가 직접 정하며 공개하지 않습니다. GitHub 웹 PR은 오프라인 로컬 검사로 실제 생성 여부를 확인할 수 없습니다.

리뷰 댓글 예: `not-admin 역할이 True가 되는 테스트를 재현했습니다. 정확 비교로 수정했고 정상 admin과 거부 케이스가 통과했습니다.` AI 의견은 근거가 없으면 보류하고 실행 결과로 확인합니다.
