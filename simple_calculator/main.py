"""HTML/CSS 화면과 FastAPI로 구성한 사칙연산 계산기."""

from decimal import Decimal, localcontext
from pathlib import Path
import re

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="두 숫자 계산기")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
NUMBER_PATTERN = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")


def parse_number(value: str, label: str) -> Decimal:
    """공백을 제거하고 일반적인 십진수 입력만 허용한다."""
    value = value.strip()
    if not value:
        raise ValueError(f"{label}를 입력해 주세요.")
    if len(value) > 30:
        raise ValueError(f"{label}는 부호와 소수점을 포함해 30자 이내로 입력해 주세요.")
    if not NUMBER_PATTERN.fullmatch(value):
        raise ValueError(f"{label}에 올바른 숫자를 입력해 주세요. 예: -3, 0.5")
    return Decimal(value)


def format_number(value: Decimal) -> str:
    if value == 0:
        return "0"
    result = format(value, "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


def calculate(first: Decimal, second: Decimal) -> list[dict[str, str]]:
    # 입력은 최대 30자이므로 유한한 세 연산은 64자리 정밀도로 보존된다.
    # 순환소수인 나눗셈은 유효숫자 64자리까지 계산한다.
    with localcontext() as context:
        context.prec = 64
        return [
            {"label": "덧셈", "symbol": "+", "value": format_number(first + second)},
            {"label": "뺄셈", "symbol": "−", "value": format_number(first - second)},
            {"label": "곱셈", "symbol": "×", "value": format_number(first * second)},
            {
                "label": "나눗셈",
                "symbol": "÷",
                "value": "0으로 나눌 수 없습니다." if second == 0 else format_number(first / second),
            },
        ]


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"first": "", "second": "", "results": [], "error": None},
    )


@app.get("/calculate", response_class=HTMLResponse)
def calculate_page(request: Request, first: str = "", second: str = ""):
    results = []
    error = None
    try:
        results = calculate(parse_number(first, "첫 번째 숫자"), parse_number(second, "두 번째 숫자"))
    except ValueError as exc:
        error = str(exc)
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"first": first, "second": second, "results": results, "error": error},
        status_code=400 if error else 200,
    )
