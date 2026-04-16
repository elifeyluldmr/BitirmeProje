from fastapi import FastAPI
from pydantic import BaseModel

from src.predict import predict_email


app = FastAPI(title="Phishing Email Detection API")


class EmailRequest(BaseModel):
    text: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: EmailRequest) -> dict:
    label = predict_email(payload.text)
    return {"label": label}
