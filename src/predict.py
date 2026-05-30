from __future__ import annotations
from pathlib import Path
import pickle

try:
    from src.text_utils import (
        advanced_preprocessing,
        build_email_text,
        find_suspicious_keywords,
        get_keyword_score,
    )
    from src.url_utils import analyze_urls_in_text
    from src.anomaly_detector import get_anomaly_score
    from src.header_utils import analyze_headers
    import src.transformer_predictor as _transformer
except ModuleNotFoundError:
    from text_utils import (
        advanced_preprocessing,
        build_email_text,
        find_suspicious_keywords,
        get_keyword_score,
    )
    from url_utils import analyze_urls_in_text
    from anomaly_detector import get_anomaly_score
    from header_utils import analyze_headers
    import transformer_predictor as _transformer

# Phishing kararı için minimum risk skoru eşiği.
PHISHING_THRESHOLD = 60.0

# ── Katman ağırlıkları ────────────────────────────────────────────────────────
# Header ve anomali yoksa bu ağırlıklar 0'a çekilerek kalan ağırlıklar
# normalize edilir — böylece risk skoru her zaman 0-100 aralığında kalır.
_W_MODEL   = 0.40   # TF-IDF LR + transformer blend
_W_KEYWORD = 0.20   # Anahtar kelime eşleşmesi
_W_URL     = 0.20   # URL risk analizi
_W_HEADER  = 0.12   # Başlık analizi (From/Reply-To)
_W_ANOMALY = 0.08   # Anomali tespiti (Isolation Forest)

# Transformer blend — model yüklüyse LR olasılığıyla bu oranlarda karıştırılır.
_TRANSFORMER_W = 0.60
_LR_W          = 0.40

_model_cache: dict = {}

_PHISHING_TYPE_KEYWORDS: dict[str, list[str]] = {
    "Finansal Dolandırıcılık": [
        "bank", "payment", "invoice", "tax", "refund", "credit", "wire",
        "banka", "ödeme", "fatura", "vergi", "iade", "kredi", "transfer", "borç",
    ],
    "Kimlik Hırsızlığı": [
        "login", "password", "verify", "account", "username", "credential",
        "giriş", "şifre", "doğrula", "hesap", "parola", "kimlik",
    ],
    "Kötü Amaçlı Link": [
        "click", "link", "download", "install", "attachment",
        "tıkla", "bağlantı", "indir", "yükle", "ek",
    ],
    "Sahte Ödül/Çekiliş": [
        "winner", "prize", "congratulations", "selected", "reward", "lottery",
        "kazandınız", "ödül", "tebrikler", "seçildiniz", "çekiliş", "hediye",
    ],
    "Sahte Kargo/Teslimat": [
        "package", "shipment", "delivery", "courier", "tracking",
        "kargo", "paket", "teslim", "teslimat", "adres",
    ],
    "Marka Taklidi": [
        "paypal", "amazon", "apple", "microsoft", "google", "netflix",
        "facebook", "instagram", "twitter", "linkedin", "dhl", "fedex",
    ],
}


def is_phishing_label(label: object) -> bool:
    return str(label).strip().lower() in {"1", "yes", "true", "phishing", "spam"}


def load_model_objects() -> tuple[object, object]:
    """Kaydedilen TF-IDF + LR modelini önbellekli yükler."""
    project_root = Path(__file__).resolve().parents[1]
    model_path = project_root / "models" / "phishing_model.pkl"

    mtime = model_path.stat().st_mtime if model_path.exists() else 0
    if "model" in _model_cache and _model_cache.get("mtime") == mtime:
        return _model_cache["model"], _model_cache["vectorizer"]

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model bulunamadi: {model_path}. Once src/train_model.py dosyasini calistirin."
        )

    with open(model_path, "rb") as file:
        saved = pickle.load(file)

    _model_cache["model"]      = saved["model"]
    _model_cache["vectorizer"] = saved["vectorizer"]
    _model_cache["mtime"]      = mtime
    return _model_cache["model"], _model_cache["vectorizer"]


def classify_phishing_type(text: str) -> str:
    text_lower = text.lower()
    type_scores: dict[str, int] = {}
    for ptype, keywords in _PHISHING_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            type_scores[ptype] = score
    if not type_scores:
        return "Genel Phishing"
    return max(type_scores, key=lambda k: type_scores[k])


def get_action_recommendations(label: str, phishing_type: str, risk_score: float) -> list[str]:
    if label != "YES":
        actions = ["E-posta güvenli görünüyor."]
        if risk_score > 40:
            actions.append("Risk skoru orta seviyede — bağlantılardan kaçınmanız önerilir.")
        return actions

    base = [
        "Bu e-postayı açmayın, linklere tıklamayın.",
        "E-postayı spam/phishing olarak işaretleyip silin.",
        "Gönderici adresini dikkatlice kontrol edin.",
    ]
    extra: dict[str, list[str]] = {
        "Finansal Dolandırıcılık": [
            "Bankanızı/finans kurumunuzu resmi numaradan arayın.",
            "Hiçbir finansal bilgi (kart no, şifre) paylaşmayın.",
        ],
        "Kimlik Hırsızlığı": [
            "Şifrelerinizi hemen değiştirin.",
            "İki faktörlü doğrulamayı (2FA) aktif edin.",
        ],
        "Kötü Amaçlı Link": [
            "Linkleri kesinlikle açmayın, eki indirmeyin.",
            "Cihazınızı güncel antivirüs yazılımıyla tarayın.",
        ],
        "Sahte Ödül/Çekiliş": [
            "Katılmadığınız çekilişlere inanmayın.",
            "Kişisel ya da finansal bilgi paylaşmayın.",
        ],
        "Sahte Kargo/Teslimat": [
            "Kargo şirketini resmi sitesinden takip edin.",
            "E-postadaki linklere değil, resmi siteye girin.",
        ],
        "Marka Taklidi": [
            "Resmi web sitesine doğrudan tarayıcıdan giriş yapın.",
            "Şirketin resmi müşteri hizmetlerini arayın.",
        ],
    }
    return base + extra.get(phishing_type, [])


def _blend_model_probability(text: str, lr_prob: float) -> tuple[float, float | None]:
    """LR olasılığını transformer ile blend eder.

    Dönüş: (blended_prob, transformer_prob_or_None)
    Transformer yoksa LR olasılığı olduğu gibi döner.
    """
    tr_prob = _transformer.predict(text)
    if tr_prob is None:
        return lr_prob, None
    blended = _TRANSFORMER_W * tr_prob + _LR_W * lr_prob
    return blended, tr_prob


def _compute_risk_score(
    model_prob: float,
    keyword_score: float,
    url_score: float,
    header_score: float,
    anomaly_score: float,
    header_provided: bool,
    anomaly_available: bool,
) -> tuple[float, dict]:
    """5 sinyali normalize ağırlıklarla birleştirir.

    Eksik sinyallerin ağırlığı diğer sinyallere orantılı dağıtılır.
    Dönüş: (risk_score 0-100, breakdown dict)
    """
    w_hdr = _W_HEADER if header_provided else 0.0
    w_ano = _W_ANOMALY if anomaly_available else 0.0
    total = _W_MODEL + _W_KEYWORD + _W_URL + w_hdr + w_ano

    contributions = {
        "model":   _W_MODEL   * model_prob    / total,
        "keyword": _W_KEYWORD * keyword_score / total,
        "url":     _W_URL     * url_score     / total,
        "header":  w_hdr      * header_score  / total,
        "anomaly": w_ano      * anomaly_score / total,
    }

    risk_score = min(100.0, sum(contributions.values()))

    breakdown = {
        "signals": {
            "model":   {
                "score": round(model_prob, 1),
                "contribution": round(contributions["model"], 1),
                "weight_pct": round(_W_MODEL / total * 100, 1),
            },
            "keyword": {
                "score": round(keyword_score, 1),
                "contribution": round(contributions["keyword"], 1),
                "weight_pct": round(_W_KEYWORD / total * 100, 1),
            },
            "url": {
                "score": round(url_score, 1),
                "contribution": round(contributions["url"], 1),
                "weight_pct": round(_W_URL / total * 100, 1),
            },
            "header": {
                "score": round(header_score, 1),
                "contribution": round(contributions["header"], 1),
                "weight_pct": round(w_hdr / total * 100, 1),
                "available": header_provided,
            },
            "anomaly": {
                "score": round(anomaly_score, 1),
                "contribution": round(contributions["anomaly"], 1),
                "weight_pct": round(w_ano / total * 100, 1),
                "available": anomaly_available,
            },
        },
    }

    return risk_score, breakdown


def predict_details(
    text: str,
    from_addr: str = "",
    reply_to: str  = "",
    subject: str   = "",
) -> dict:
    """Metni 5 katmanlı hibrit modelle analiz eder ve detaylı sonuç döndürür."""
    model, vectorizer = load_model_objects()

    clean_text = advanced_preprocessing(text)
    text_vector = vectorizer.transform([clean_text])

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(text_vector)[0]
        lr_probability = float(probs[1] * 100)
    else:
        raw = model.predict(text_vector)[0]
        lr_probability = 100.0 if is_phishing_label(raw) else 0.0

    # Transformer blend
    model_probability, transformer_probability = _blend_model_probability(text, lr_probability)

    # Keyword
    matched_keywords = find_suspicious_keywords(text)
    keyword_score    = get_keyword_score(matched_keywords)

    # URL
    url_analysis = analyze_urls_in_text(text)
    url_score    = float(url_analysis["max_score"])

    # Anomali
    anomaly       = get_anomaly_score(text)
    anomaly_score = float(anomaly["score"])

    # Header
    header_provided = bool(from_addr.strip() or reply_to.strip())
    header_analysis = analyze_headers(from_addr, reply_to, subject)
    header_score    = float(header_analysis["score"])

    # 5 katmanlı risk skoru
    risk_score, breakdown = _compute_risk_score(
        model_probability,
        keyword_score,
        url_score,
        header_score,
        anomaly_score,
        header_provided,
        anomaly["available"],
    )

    breakdown["transformer_probability"] = (
        round(transformer_probability, 1) if transformer_probability is not None else None
    )
    breakdown["lr_probability"] = round(lr_probability, 1)
    breakdown["transformer_used"] = transformer_probability is not None

    phishing_result = "YES" if risk_score >= PHISHING_THRESHOLD else "NO"
    raw_distance    = abs(risk_score - PHISHING_THRESHOLD)
    confidence      = min(100.0, raw_distance * (100.0 / PHISHING_THRESHOLD))

    phishing_type = classify_phishing_type(text) if phishing_result == "YES" else ""
    actions       = get_action_recommendations(phishing_result, phishing_type, risk_score)

    return {
        "label":                phishing_result,
        "confidence":           confidence,
        "risk_score":           risk_score,
        "phishing_probability": model_probability,
        "lr_probability":       lr_probability,
        "normal_probability":   100.0 - model_probability,
        "keyword_score":        keyword_score,
        "matched_keywords":     matched_keywords,
        "phishing_type":        phishing_type,
        "url_analysis":         url_analysis,
        "anomaly":              anomaly,
        "header_analysis":      header_analysis,
        "score_breakdown":      breakdown,
        "actions":              actions,
    }


def predict_details_with_headers(
    text: str,
    from_addr: str = "",
    reply_to: str  = "",
    subject: str   = "",
) -> dict:
    """predict_details ile aynıdır; geriye dönük uyumluluk için korunmuştur."""
    return predict_details(text, from_addr, reply_to, subject)


def predict_with_confidence(text: str) -> tuple[str, float]:
    result = predict_details(text)
    return result["label"], float(result["confidence"])


def predict_email(text: str) -> str:
    return str(predict_details(text)["label"])


def main() -> None:
    test_email_1 = {
        "subject": "Verify Your Bank Account",
        "body": "Your account has been suspended. Click here to verify immediately. http://login.fake-bank.tk/verify",
    }
    test_email_2 = {
        "subject": "Meeting Reminder",
        "body": "We have a meeting tomorrow at 10 AM.",
    }

    full_text_1 = build_email_text(test_email_1["subject"], test_email_1["body"])
    full_text_2 = build_email_text(test_email_2["subject"], test_email_2["body"])

    result_1 = predict_details(full_text_1, subject=test_email_1["subject"])
    result_2 = predict_details(full_text_2, subject=test_email_2["subject"])

    for label, r in [("Test 1 (Phishing)", result_1), ("Test 2 (Normal)", result_2)]:
        bd = r["score_breakdown"]
        print(f"\n{label}")
        print(f"  Karar      : {r['label']}  (Risk: {r['risk_score']:.1f})")
        print(f"  Transformer: {'✅ ' + str(bd['transformer_probability']) if bd['transformer_used'] else '⚠️  Kullanılmıyor'}")
        print("  Sinyal Dağılımı:")
        for name, sig in bd["signals"].items():
            avail = sig.get("available", True)
            tag = "" if avail else " (mevcut değil)"
            print(f"    {name:8}: {sig['score']:5.1f}/100  →  +{sig['contribution']:.1f} pt  (ağırlık %{sig['weight_pct']:.0f}){tag}")


if __name__ == "__main__":
    main()
