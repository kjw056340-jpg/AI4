"""쇼핑몰 상품 조회로 배우는 이벤트 루프와 동시성."""

import asyncio
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="동시성 마켓", description="동기·비동기 상품 조회 실험실")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

PRODUCTS = [
    {"id": 1, "name": "데일리 헤드폰", "category": "AUDIO", "price": 89000, "stock": 24, "icon": "🎧"},
    {"id": 2, "name": "포켓 카메라", "category": "CAMERA", "price": 159000, "stock": 8, "icon": "📷"},
    {"id": 3, "name": "워크 키보드", "category": "DESK", "price": 69000, "stock": 16, "icon": "⌨️"},
    {"id": 4, "name": "위켄드 스니커즈", "category": "LIFESTYLE", "price": 79000, "stock": 12, "icon": "👟"},
]


def legacy_lookup(product: dict, delay: float) -> dict:
    """외부 재고 서버에 연결하는 기존 동기 SDK를 흉내 냅니다."""
    time.sleep(delay)
    return {**product, "delivery": "내일 도착 · 무료배송"}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/catalog")
async def catalog():
    return PRODUCTS


@app.get("/api/health")
async def health():
    """상품 조회 중에도 즉시 응답할 수 있는지 확인하는 가벼운 요청."""
    return {"status": "ok"}


@app.get("/api/products/{product_id}")
async def product_detail(
    product_id: int,
    mode: Literal["blocking", "async", "thread"] = "async",
    delay: float = Query(default=2.0, ge=0.5, le=3.0),
):
    product = next((item for item in PRODUCTS if item["id"] == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    start = time.perf_counter()
    if mode == "blocking":
        # 비교를 위한 의도된 문제: async def 안에서도 동기 호출은 루프를 막습니다.
        result = legacy_lookup(product, delay)
    elif mode == "async":
        # 실제 서비스에서는 비동기 HTTP/DB 클라이언트의 I/O를 await 합니다.
        await asyncio.sleep(delay)
        result = {**product, "delivery": "내일 도착 · 무료배송"}
    else:
        # 기존 동기 라이브러리를 유지하면서 대기를 별도 스레드에 맡깁니다.
        result = await asyncio.to_thread(legacy_lookup, product, delay)

    return {"product": result, "mode": mode, "server_seconds": time.perf_counter() - start}
