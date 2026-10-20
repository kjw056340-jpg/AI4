# 두 숫자 계산기

두 숫자를 입력하면 덧셈, 뺄셈, 곱셈, 나눗셈 결과를 한 번에 보여주는 웹 계산기입니다.

- 백엔드: Python, FastAPI
- 프론트엔드: HTML, CSS (JavaScript 없이 동작)
- 화면 생성: Jinja2 템플릿
- 실행 서버: Uvicorn
- 숫자 계산: Python 표준 라이브러리 `decimal.Decimal`

## 1. 현재 PC에서 바로 실행하기

이 프로젝트에는 필요한 패키지를 설치한 `.venv` 가상환경이 준비되어 있습니다. PowerShell에서 다음 명령을 실행하세요.

```powershell
cd C:\Users\Playdata\dev\simple_calculator
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

브라우저에서 **http://127.0.0.1:8000** 에 접속합니다.

1. 첫 번째 숫자와 두 번째 숫자를 입력합니다.
2. **계산하기** 버튼을 누르거나 입력창에서 Enter를 누릅니다.
3. 네 가지 연산 결과를 확인합니다.
4. **초기화**를 누르면 처음 화면으로 돌아갑니다.

서버 종료: 터미널에서 `Ctrl+C`.

가상환경을 활성화하지 않고 직접 실행하므로 PowerShell의 스크립트 실행 정책을 변경할 필요가 없습니다.

## 2. 다른 PC에서 처음 설치하기

Python 3.10 이상을 설치하고 이 프로젝트 폴더를 복사하세요. `.venv`는 PC마다 새로 만들어야 하므로 복사하지 않습니다. 검증에는 Python 3.12.14를 사용했습니다.

Windows PowerShell:

```powershell
cd C:\프로젝트를_복사한_경로\simple_calculator
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

`py`가 없고 `python` 명령이 등록되어 있다면 첫 설치 명령을 `python -m venv .venv`로 바꾸세요. 둘 다 인식되지 않으면 Python 설치 및 PATH 설정을 확인하거나 Python 실행 파일의 전체 경로를 사용하세요.

macOS / Linux:

```bash
cd /프로젝트를_복사한_경로/simple_calculator
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m uvicorn main:app --reload
```

`requirements-lock.txt`는 검증한 전체 패키지 버전을 기록합니다. 실행에 필요한 패키지만 버전 범위로 설치하려면 `requirements.txt`, 테스트 도구까지 설치하려면 `requirements-dev.txt`를 사용할 수 있습니다.

## 3. 프로젝트 파일

```text
simple_calculator/
├── main.py                 # FastAPI 경로, 입력 검사, 사칙연산
├── templates/
│   └── index.html          # 숫자 입력 폼과 결과 화면
├── static/
│   └── style.css           # 화면 디자인과 모바일 레이아웃
├── test_main.py            # 자동 검증 11개
├── requirements.txt        # 실행용 패키지 범위
├── requirements-dev.txt    # 실행용 패키지 + 테스트 도구
├── requirements-lock.txt   # 검증에 사용한 정확한 패키지 버전
├── .gitignore              # 가상환경 및 캐시 제외
└── README.md               # 요약, 동작 설명, 실행 및 검증 방법
```

## 4. 동작 설명

1. `GET /` 요청으로 숫자 입력 화면을 엽니다.
2. HTML 폼이 `GET /calculate?first=12&second=4`와 같이 두 값을 서버로 전달합니다.
3. `parse_number()`가 빈 값, 숫자 형식, 길이를 검사하고 `Decimal`로 변환합니다.
4. `calculate()`가 네 가지 연산을 수행합니다.
5. `format_number()`가 불필요한 소수점 뒤 0을 정리합니다.
6. Jinja2가 계산 결과를 HTML에 채워 반환합니다. CSS는 `/static/style.css`에서 제공합니다.

계산 순서는 **첫 번째 숫자 연산 두 번째 숫자**입니다. 예를 들어 12와 4를 입력하면 다음 결과가 나옵니다.

| 연산 | 수식 | 결과 |
| --- | --- | --- |
| 덧셈 | 12 + 4 | 16 |
| 뺄셈 | 12 − 4 | 8 |
| 곱셈 | 12 × 4 | 48 |
| 나눗셈 | 12 ÷ 4 | 3 |

## 5. 입력과 예외 처리

- 정수, 음수, 소수를 지원합니다. 예: `12`, `-3`, `0.5`, `.5`.
- 앞뒤 공백은 계산 전에 제거합니다.
- 숫자는 부호와 소수점을 포함하여 각각 30자까지 입력할 수 있습니다.
- 천 단위 쉼표와 지수 표기법은 지원하지 않습니다. `1,000` 대신 `1000`, `1e3` 대신 `1000`을 입력하세요.
- 빈 값과 문자는 서버에서도 검사하며, 오류 안내 화면을 HTTP 400으로 반환합니다.
- 두 번째 숫자가 0이면 나눗셈에만 **0으로 나눌 수 없습니다.**를 표시하고 나머지 세 연산 결과는 정상적으로 표시합니다.
- `Decimal`로 계산하여 `0.1 + 0.2`를 `0.3`으로 표시합니다.
- 계산 정밀도는 유효숫자 64자리입니다. 나눗셈 결과가 이를 초과하면 기본 반올림 방식인 `ROUND_HALF_EVEN`으로 반올림합니다.
- HTML 템플릿은 입력 내용을 자동 이스케이프합니다.
- 화면은 작은 화면에서 입력창과 결과 카드를 한 열로 배치합니다.

## 6. 검증 결과와 재실행 방법

2026-10-20 검증 결과:

- 자동 테스트 **11개 모두 통과**.
- 입력 검사의 여러 경우는 각 테스트 내부에서 추가로 확인했습니다.
- 실제 Uvicorn 서버를 실행하여 첫 화면, 계산 결과, CSS의 HTTP 응답을 확인했습니다.
- `pip check`에서 패키지 의존성 충돌이 없음을 확인했습니다.
- 실제 브라우저에서의 육안 확인은 수행하지 않았습니다.

검증한 내용: 사칙연산, 소수 정확도, 음수, 공백, 순환소수, 0으로 나누기, 잘못된 입력, 누락된 입력, 최대 길이 숫자, HTML 이스케이프, 첫 화면 및 CSS 응답.

PowerShell에서 테스트 재실행:

```powershell
cd C:\Users\Playdata\dev\simple_calculator
.\.venv\Scripts\python.exe -m unittest -v
.\.venv\Scripts\python.exe -m pip check
```

실행용 `requirements.txt`만 설치한 환경이라면 테스트 전에 다음 명령도 실행하세요.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

검증된 Starlette 버전에서는 테스트 도구의 httpx 사용에 관한 향후 지원 변경 경고가 나올 수 있습니다. 현재 테스트는 정상 통과하며 계산기 실행에는 영향을 주지 않습니다.

## 7. 자주 겪는 문제

- **8000 포트가 이미 사용 중인 경우**: `--port 8001`을 붙여 실행하고 http://127.0.0.1:8001 로 접속하세요.
- **main 모듈을 찾을 수 없는 경우**: `main.py`가 있는 `simple_calculator` 폴더로 이동한 뒤 실행하세요.
- **fastapi 모듈이 없는 경우**: `.venv`의 Python으로 설치와 실행을 모두 진행했는지 확인하세요.

`--reload`는 개발 중 코드를 수정하면 서버를 자동으로 다시 시작하는 옵션입니다. 이 안내의 서버는 현재 PC의 `127.0.0.1`에서 실행됩니다.
