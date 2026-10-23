from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="할인 견적 API")


class QuoteIn(BaseModel):
    amount: int = Field(ge=1, le=100000, strict=True)


def calculate_discount(amount: int):
    return 1000 if amount > 10000 else 0


@app.post("/quotes", summary="할인 견적")
def quote(body: QuoteIn):
    discount = calculate_discount(body.amount)
    return {"amount": body.amount, "discount": discount, "payable": body.amount - discount}
