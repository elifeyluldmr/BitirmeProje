import sys
# UTF-8 çıktı, Windows'ta Türkçe karakter sorununu önlüyor
sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from src.predict import predict_details, predict_details_with_headers, predict_email

# API dokümantasyonu /docs adresinde otomatik açılıyor
app = FastAPI(
    title="Phishing Email Detection API",
    description="E-posta phishing tespiti, açıklanabilirlik ve önceliklendirme servisi.",
    version="2.0.0",
)


# Sadece metin alan basit istek modeli
class EmailRequest(BaseModel):
    text: str


# Başlık bilgilerini de kabul eden tam analiz istek modeli
class EmailFullRequest(BaseModel):
    text: str
    from_addr: str = ""
    reply_to: str  = ""
    subject: str   = ""


# Toplu analiz için e-posta listesi alıyoruz
class BatchRequest(BaseModel):
    emails: list[str]


@app.get("/")
def root() -> RedirectResponse:
    # Ana sayfayı Swagger dokümantasyonuna yönlendiriyoruz
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict:
    # Load balancer ve monitoring araçları bu endpoint'i kontrol ediyor
    return {"status": "ok"}


@app.post("/predict", summary="Hızlı karar (YES/NO)")
def predict(payload: EmailRequest) -> dict:
    # Sadece karar lazımsa bu endpoint daha hızlı, detay istemiyoruz
    label = predict_email(payload.text)
    return {"label": label}


@app.post("/predict/details", summary="Tam analiz (risk, URL, anomali, aksiyonlar)")
def predict_full(payload: EmailFullRequest) -> dict:
    # İç result dict'inden sadece API'ye uygun alanları dışarıya açıyoruz
    result = predict_details_with_headers(
        payload.text, payload.from_addr, payload.reply_to, payload.subject
    )
    return {
        "label":                result["label"],
        "risk_score":           round(result["risk_score"], 2),
        "confidence":           round(result["confidence"], 2),
        "phishing_probability": round(result["phishing_probability"], 2),
        "keyword_score":        round(result["keyword_score"], 2),
        "matched_keywords":     result["matched_keywords"],
        "phishing_type":        result["phishing_type"],
        "anomaly":              result.get("anomaly", {}),
        "url_analysis":         result["url_analysis"],
        "header_analysis":      result.get("header_analysis", {}),
        "actions":              result["actions"],
    }


@app.post("/predict/batch", summary="Toplu analiz — risk skoruna göre önceliklendirilmiş liste")
def predict_batch(payload: BatchRequest) -> dict:
    # 500'den fazla e-posta gelirse reddediyoruz, bellek ve zaman koruma amaçlı
    if len(payload.emails) > 500:
        return {"error": "Maksimum 500 e-posta gönderilebilir."}

    results = []
    for i, text in enumerate(payload.emails):
        try:
            res = predict_details(text)
            results.append({
                "index":          i,
                "label":          res["label"],
                "risk_score":     round(res["risk_score"], 2),
                "phishing_type":  res.get("phishing_type", ""),
                "url_suspicious": res["url_analysis"]["suspicious_count"],
                # Önizlemede ilk 80 karakter yeterli
                "preview":        text[:80],
            })
        except Exception as e:
            results.append({"index": i, "error": str(e)})

    # En riskli e-postalar listenin başına geliyor
    results.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
    phishing_count = sum(1 for r in results if r.get("label") == "YES")

    return {
        "total":    len(results),
        "phishing": phishing_count,
        "safe":     len(results) - phishing_count,
        "results":  results,
    }
