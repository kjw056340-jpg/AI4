from fastapi import FastAPI

app = FastAPI(title="Lesson 02")

@app.get("/method")
def read_method():
    return {"method": "GET", "purpose": "read"}

@app.post("/method", status_code=201)
def create_method():
    return {"method": "POST", "purpose": "create"}
