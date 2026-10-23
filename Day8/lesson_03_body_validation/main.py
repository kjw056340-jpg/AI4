from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="주문 검증 API")


class OrderIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=20)
    quantity: int = Field(ge=1, le=5, strict=True)


@app.post("/orders", status_code=201, summary="주문 금액 계산")
def create_order(order: OrderIn):
    return {"name": order.name, "quantity": order.quantity, "total": order.quantity * 3000}
