from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from src.predict import predict_email


app = FastAPI(title="Phishing Email Detection API")


class EmailRequest(BaseModel):
    text: str


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: EmailRequest) -> dict:
    label = predict_email(payload.text)
    return {"label": label}
