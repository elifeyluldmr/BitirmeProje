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

# Phishing kararı için minimum eşik — 60 ve üzeri phishing kabul edilir.
PHISHING_THRESHOLD = 60.0

# Keyword skorunun nihai risk skoru üzerindeki maksimum etkisi.
KEYWORD_WEIGHT = 0.35
MODEL_WEIGHT = 1.0 - KEYWORD_WEIGHT

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
    label_text = str(label).strip().lower()
    return label_text in {"1", "yes", "true", "phishing", "spam"}


def load_model_objects() -> tuple[object, object]:
    """Kaydedilen model ve TF-IDF vectorizer nesnelerini yükler; sonucu önbellekte tutar."""
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
        saved_objects = pickle.load(file)

    _model_cache["model"] = saved_objects["model"]
    _model_cache["vectorizer"] = saved_objects["vectorizer"]
    _model_cache["mtime"] = mtime
    return _model_cache["model"], _model_cache["vectorizer"]


def classify_phishing_type(text: str) -> str:
    """Phishing e-postasının saldırı türünü tespit eder."""
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
    """Risk durumuna ve phishing türüne göre aksiyon önerileri üretir."""
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


def predict_details(text: str) -> dict:
    """Metni işler ve modelden detaylı tahmin bilgilerini döndürür."""
    model, vectorizer = load_model_objects()

    clean_text = advanced_preprocessing(text)
    text_vector = vectorizer.transform([clean_text])

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(text_vector)[0]
        phishing_probability = float(probabilities[1] * 100)
        normal_probability = float(probabilities[0] * 100)
    else:
        raw_pred = model.predict(text_vector)[0]
        phishing_probability = 100.0 if is_phishing_label(raw_pred) else 0.0
        normal_probability = 100.0 - phishing_probability

    matched_keywords = find_suspicious_keywords(text)
    keyword_score = get_keyword_score(matched_keywords)

    risk_score = (MODEL_WEIGHT * phishing_probability) + (KEYWORD_WEIGHT * keyword_score)
    phishing_result = "YES" if risk_score >= PHISHING_THRESHOLD else "NO"

    raw_distance = abs(risk_score - PHISHING_THRESHOLD)
    confidence = min(100.0, raw_distance * (100.0 / PHISHING_THRESHOLD))

    phishing_type = classify_phishing_type(text) if phishing_result == "YES" else ""
    url_analysis  = analyze_urls_in_text(text)
    anomaly       = get_anomaly_score(text)
    actions       = get_action_recommendations(phishing_result, phishing_type, risk_score)

    return {
        "label":               phishing_result,
        "confidence":          confidence,
        "risk_score":          risk_score,
        "phishing_probability": phishing_probability,
        "normal_probability":  normal_probability,
        "keyword_score":       keyword_score,
        "matched_keywords":    matched_keywords,
        "phishing_type":       phishing_type,
        "url_analysis":        url_analysis,
        "anomaly":             anomaly,
        "actions":             actions,
    }


def predict_details_with_headers(
    text: str,
    from_addr: str = "",
    reply_to: str  = "",
    subject: str   = "",
) -> dict:
    """predict_details'e ek olarak e-posta başlık analizini de döndürür."""
    result         = predict_details(text)
    header_result  = analyze_headers(from_addr, reply_to, subject)
    result["header_analysis"] = header_result
    return result


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

    result_1 = predict_details(full_text_1)
    result_2 = predict_details(full_text_2)

    print("Test 1")
    print(f"  Phishing : {result_1['label']}")
    print(f"  Risk     : {result_1['risk_score']:.1f}")
    print(f"  Tür      : {result_1['phishing_type']}")
    print(f"  URL sayısı: {result_1['url_analysis']['total_count']}")
    print(f"  Aksiyonlar: {result_1['actions']}")
    print()

    print("Test 2")
    print(f"  Phishing : {result_2['label']}")
    print(f"  Risk     : {result_2['risk_score']:.1f}")


if __name__ == "__main__":
    main()
