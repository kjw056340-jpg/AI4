from fastapi import FastAPI

app = FastAPI(title="인사 API", version="1.0.0")


@app.get("/greet", summary="이름으로 인사", include_in_schema=True)
def greet(name: str = "guest"):
    return {"message": f"Hello, {name}!"}
