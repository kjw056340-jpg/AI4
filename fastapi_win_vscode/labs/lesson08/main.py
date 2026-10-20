from fastapi import FastAPI
from .router import router

app = FastAPI(title="AI Camp Task API", version="1.0.0")
app.include_router(router)

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
