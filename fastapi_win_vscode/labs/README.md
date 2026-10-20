# Lesson 01: 입력 → 서버 처리 → 화면 표시

이름을 입력하면 FastAPI 서버가 인사말을 만들어 같은 화면에 표시하는 초보자용 예제입니다.

예: 홍길동 입력 → 인사말 만들기 클릭 → “홍길동님, 안녕하세요! 서버에서 만든 인사말입니다.” 표시.

백엔드는 Python/FastAPI, 프론트엔드는 HTML/CSS입니다. JavaScript 없이 HTML 폼으로 데이터를 전송합니다. 데이터베이스나 파일 저장은 하지 않습니다.

## 1. 실행하기

현재 PC에서는 앞서 계산기에 준비한 정상 가상환경으로 실행할 수 있습니다. 이 환경에는 Jinja2도 설치되어 있습니다.

```powershell
cd C:\Users\Playdata\dev\fastapi_win_vscode
..\simple_calculator\.venv\Scripts\python.exe -m uvicorn labs.lesson01:app --reload
```

브라우저에서 http://127.0.0.1:8000 에 접속하여 이름을 입력하고 **인사말 만들기**를 누르세요. **처음으로**를 누르면 입력을 초기화합니다. 종료는 터미널에서 Ctrl+C입니다.

8000 포트가 사용 중이라면 기존 서버를 종료하거나 실행 명령에 `--port 8001`을 붙이고 http://127.0.0.1:8001 로 접속하세요.

프로젝트 자체 가상환경이 정상인 PC에서는 다음과 같이 실행합니다. 현재 PC의 기존 프로젝트 가상환경은 이전 검증에서 실행되지 않아 계산기 환경을 사용했습니다.

```powershell
cd C:\Users\Playdata\dev\fastapi_win_vscode
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn labs.lesson01:app --reload
```

## 2. 파일 역할

- `labs/lesson01.py`: 입력값 검사와 인사말 생성.
- `labs/templates/lesson01.html`: 이름 입력창, 버튼, 결과 표시와 CSS.
- `requirements.txt`: Jinja2를 포함한 필요한 패키지.
- `tests/test_lessons.py`: 첫 화면, 인사말, 오류 처리 검사.

## 3. 전체 동작 순서

1. 브라우저가 `/`에 접속하면 `root()`가 빈 입력 화면을 반환합니다.
2. 사용자가 이름을 입력하고 버튼을 누릅니다.
3. HTML 폼이 이름을 `/greet` 주소로 보냅니다.
4. FastAPI가 `greet()` 함수의 `name` 매개변수에 이름을 넣습니다.
5. 서버가 앞뒤 공백을 제거하고 이름을 검사한 뒤 인사말을 만듭니다.
6. `TemplateResponse`가 이름과 인사말을 HTML에 넣어 반환합니다.
7. 브라우저가 결과를 포함한 화면으로 갱신됩니다.

입력한 이름도 HTML에 다시 넣어 주므로 결과 화면의 입력창에 남습니다.

## 4. HTML이 데이터를 보내는 방법

```html
<form action="/greet" method="get">
  <label for="name">이름</label>
  <input id="name" name="name" type="text" required>
  <button type="submit">인사말 만들기</button>
</form>
```

- `action="/greet"`: 데이터를 보낼 주소입니다.
- `method="get"`: 주소의 쿼리 문자열로 데이터를 보내는 방식입니다.
- `name="name"`: 서버에 전달할 항목 이름입니다. 파이썬 매개변수 `name`과 맞춥니다.
- `id="name"`: label과 입력창을 연결하는 용도입니다. 서버 전송 항목은 name 속성이 결정합니다.
- `type="submit"`: 클릭하면 폼을 전송합니다.

이름이 홍길동이면 개념적으로 `/greet?name=홍길동` 주소로 요청합니다. 실제 주소창에서는 한글이 URL 인코딩된 형태로 보일 수 있습니다. GET 방식은 입력값이 주소에 나타납니다.

## 5. 파이썬에서 처리하는 방법

`lesson01.py`의 핵심 함수입니다.

```python
@app.get("/greet", response_class=HTMLResponse)
def greet(request: Request, name: str = ""):
    name = name.strip()

    message = ""
    error = ""
    if not name:
        error = "이름을 입력해 주세요."
    elif len(name) > 30:
        error = "이름은 30자 이내로 입력해 주세요."
    else:
        message = f"{name}님, 안녕하세요! 서버에서 만든 인사말입니다."

    return templates.TemplateResponse(
        request=request,
        name="lesson01.html",
        context={"name": name, "message": message, "error": error},
        status_code=400 if error else 200,
    )
```

- `name: str = ""`: 요청에서 이름을 문자열로 받습니다. 없으면 빈 문자열을 받습니다.
- `strip()`: 앞뒤 공백을 제거합니다.
- `if not name`: 빈 이름과 공백만 있는 입력을 검사합니다.
- `len(name) > 30`: 30자를 넘는 이름을 검사합니다.
- `f"{name}님, ..."`: 이름을 넣은 새 인사말을 서버에서 만듭니다.
- `context`: HTML에 전달할 변수 이름과 값을 담은 딕셔너리입니다.
- `request`: 현재 HTTP 요청 정보이며 템플릿 응답을 만들 때 전달합니다.
- `status_code`: 정상 입력은 200, 입력 오류는 400입니다. 오류일 때도 안내 HTML 화면을 반환합니다.

실제 파일 위쪽의 `Jinja2Templates`가 템플릿 도구를 준비합니다. `Path(__file__).resolve().parent`로 파이썬 파일 기준의 HTML 폴더 경로를 만들어 실행 폴더가 달라도 파일을 찾습니다.

## 6. HTML이 결과를 표시하는 방법

```html
<input name="name" value="{{ name }}">

{% if message %}
<p>{{ message }}</p>
{% endif %}

{% if error %}
<p role="alert">{{ error }}</p>
{% endif %}
```

- `{{ name }}`: 서버가 받은 이름을 입력창에 다시 표시합니다.
- `{{ message }}`: 서버가 만든 인사말을 표시합니다.
- `{% if message %}`: 인사말이 있을 때만 해당 부분을 표시합니다.
- `{% if error %}`: 오류가 있을 때만 안내를 표시합니다.

이것은 Jinja2 템플릿 문법입니다. 서버에서 값을 채워 완성된 HTML을 브라우저로 보냅니다. HTML 파일만 직접 열면 서버 처리는 실행되지 않으므로 반드시 FastAPI 주소로 접속하세요.

이전 FileResponse는 파일을 그대로 보냈지만, 이제는 Jinja2Templates와 TemplateResponse가 HTML에 값을 넣어 보냅니다. 이를 위해 requirements.txt에 `jinja2==3.1.6`을 추가했습니다. HTML 자동 이스케이프 기능으로 입력한 `<script>` 같은 문자열도 텍스트로 표시합니다.

## 7. 직접 바꿔 보기

파이썬에서 다음 줄을 바꾸면 다른 메시지를 만들 수 있습니다.

```python
message = f"{name}님, 오늘도 좋은 하루 보내세요!"
```

화면 문구와 색상은 lesson01.html에서 바꾸세요. HTML 저장 후 브라우저를 새로고침하면 됩니다. 파이썬 수정은 --reload 옵션이 서버를 자동으로 다시 시작합니다.

## 8. 검증

정상 실행되는 계산기 가상환경에서 FastAPI TestClient로 검증했습니다. 첫 화면, 정상 이름, 앞뒤 공백, 30자 이름, 빈 이름, 공백만 있는 이름, 31자 이름, 입력 누락, HTML 이스케이프, 다른 작업 폴더에서의 템플릿 경로, API 문서 응답을 확인했습니다.

입력창의 required와 maxlength 외에도 서버에서 입력을 검사합니다.

기존 pytest 파일에도 인사말과 입력 오류 검사를 추가했습니다. 프로젝트 가상환경이 정상이고 requirements.txt의 패키지가 설치되었다면 다음 명령으로 실행할 수 있습니다.

```powershell
cd C:\Users\Playdata\dev\fastapi_win_vscode
.\.venv\Scripts\python.exe -m pytest tests/test_lessons.py -k "hello or greeting or docs_and_schema"
```
