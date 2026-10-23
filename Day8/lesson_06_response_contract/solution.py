from typing import Annotated
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

app = FastAPI(title="프로필 응답 API")


class ProfileOut(BaseModel):
    id: int
    name: str


profiles = {1: {"id": 1, "name": "Min", "internal_note": "staff only"}}


@app.get("/profiles/{profile_id}", response_model=ProfileOut, responses={404: {"description": "프로필 없음"}})
def read_profile(profile_id: Annotated[int, Path(ge=1)]):
    record = profiles.get(profile_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return record
