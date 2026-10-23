from typing import Annotated
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="예약 종합 검증 API")
app.state.remaining = 4
app.state.reservations = {}


class ReservationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=20)
    seats: int = Field(ge=1, le=4, strict=True)


@app.post("/reservations", status_code=201, responses={409: {"description": "좌석 부족"}})
def create_reservation(body: ReservationIn):
    app.state.remaining -= body.seats
    if app.state.remaining < 0:
        raise HTTPException(status_code=409, detail="Not enough seats")
    reservation_id = max(app.state.reservations, default=0) + 1
    record = {"id": reservation_id, "name": body.name, "seats": body.seats}
    app.state.reservations[reservation_id] = record
    return {**record, "remaining": app.state.remaining}


@app.get("/reservations/{reservation_id}", responses={404: {"description": "예약 없음"}})
def read_reservation(reservation_id: Annotated[int, Path(ge=1)]):
    if reservation_id not in app.state.reservations:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return app.state.reservations[reservation_id]
