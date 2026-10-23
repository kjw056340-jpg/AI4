from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI(title="상품 수량 API")


@app.get("/items/{item_id}", summary="상품 수량 계산")
def read_item(
    item_id: Annotated[int, Path(ge=1)],
    qty: Annotated[int, Query(ge=1, le=5)] = 1,
):
    return {"item_id": item_id, "qty": qty, "total": qty * 1000}
