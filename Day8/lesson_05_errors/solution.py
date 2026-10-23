from typing import Annotated
from fastapi import FastAPI, HTTPException, Path

app = FastAPI(title="상품 오류 API")
products = {1: {"id": 1, "name": "tea"}}


def find_product(product_id: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]


@app.get("/products/{product_id}", responses={404: {"description": "상품 없음"}})
def read_product(product_id: Annotated[int, Path(ge=1)]):
    return find_product(product_id)
