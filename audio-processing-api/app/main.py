from fastapi import FastAPI, Request
from . import api

app = FastAPI()

app.include_router(api.router)

@app.get("/")
async def home(request: Request):
    return {"status": "WhisperX API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}