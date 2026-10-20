from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Lesson 01")

# HTML에 파이썬 값을 넣어 주는 템플릿 도구입니다.
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    # 처음에는 빈 입력 화면을 보여 줍니다.
    return templates.TemplateResponse(
        request=request,
        name="lesson01.html",
        context={"name": "", "message": "", "error": ""},
    )


@app.get("/greet", response_class=HTMLResponse)
def greet(request: Request, name: str = ""):
    # 1. 입력한 이름 앞뒤의 공백을 제거합니다.
    name = name.strip()

    # 2. 이름을 검사한 뒤 서버에서 인사말을 만듭니다.
    message = ""
    error = ""
    if not name:
        error = "이름을 입력해 주세요."
    elif len(name) > 30:
        error = "이름은 30자 이내로 입력해 주세요."
    else:
        message = f"{name}님, 안녕하세요! 서버에서 만든 인사말입니다."

    # 3. 처리 결과를 HTML에 전달합니다.
    return templates.TemplateResponse(
        request=request,
        name="lesson01.html",
        context={"name": name, "message": message, "error": error},
        status_code=400 if error else 200,
    )
