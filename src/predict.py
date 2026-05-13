from pathlib import Path
import pickle

try:
    from src.text_utils import (
        build_email_text,
        find_suspicious_keywords,
        get_keyword_score,
        preprocessing,
    )
except ModuleNotFoundError:
    from text_utils import (
        build_email_text,
        find_suspicious_keywords,
        get_keyword_score,
        preprocessing,
    )

# Phishing kararı için minimum eşik — 60 ve üzeri phishing kabul edilir.
PHISHING_THRESHOLD = 60.0

# Keyword skorunun nihai risk skoru üzerindeki maksimum etkisi.
# Model olasılığı %65, keyword skoru %35 ağırlıkla birleştirilir.
KEYWORD_WEIGHT = 0.35
MODEL_WEIGHT = 1.0 - KEYWORD_WEIGHT


def is_phishing_label(label: object) -> bool:
    """Model çıktısını YES veya NO olarak yorumlamak için etiketi kontrol eder."""
    label_text = str(label).strip().lower()
    return label_text in {"1", "yes", "true", "phishing", "spam"}


def load_model_objects() -> tuple[object, object]:
    """Kaydedilen model ve TF-IDF vectorizer nesnelerini yükler."""
    project_root = Path(__file__).resolve().parents[1]
    model_path = project_root / "models" / "phishing_model.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model bulunamadi: {model_path}. Once src/train_model.py dosyasini calistirin."
        )

    with open(model_path, "rb") as file:
        saved_objects = pickle.load(file)

    return saved_objects["model"], saved_objects["vectorizer"]


def predict_details(text: str) -> dict:
    """Metni işler ve modelden detaylı tahmin bilgilerini döndürür."""
    model, vectorizer = load_model_objects()

    clean_text = preprocessing(text)
    text_vector = vectorizer.transform([clean_text])

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(text_vector)[0]
        phishing_probability = float(probabilities[1] * 100)
        normal_probability = float(probabilities[0] * 100)
    else:
        # predict_proba yoksa ham tahmine göre basit atama yap.
        raw_pred = model.predict(text_vector)[0]
        phishing_probability = 100.0 if is_phishing_label(raw_pred) else 0.0
        normal_probability = 100.0 - phishing_probability

    matched_keywords = find_suspicious_keywords(text)
    keyword_score = get_keyword_score(matched_keywords)

    # Risk skoru: model olasılığı baskın, keyword skoru destekleyici rol oynar.
    # Keyword skoru yalnızca model zaten şüpheleniyorsa etkisini artırır;
    # model güvenliyse keyword skoru kararı tersine çeviremez.
    risk_score = (MODEL_WEIGHT * phishing_probability) + (KEYWORD_WEIGHT * keyword_score)

    phishing_result = "YES" if risk_score >= PHISHING_THRESHOLD else "NO"

    # Confidence: eşikten ne kadar uzakta olduğumuzu 0–100 aralığına normalize et.
    raw_distance = abs(risk_score - PHISHING_THRESHOLD)
    confidence = min(100.0, raw_distance * (100.0 / PHISHING_THRESHOLD))

    return {
        "label": phishing_result,
        "confidence": confidence,
        "risk_score": risk_score,
        "phishing_probability": phishing_probability,
        "normal_probability": normal_probability,
        "keyword_score": keyword_score,
        "matched_keywords": matched_keywords,
    }


def predict_with_confidence(text: str) -> tuple[str, float]:
    """Metni işler, modeli kullanır ve YES/NO ile güven oranını döndürür."""
    result = predict_details(text)
    return result["label"], float(result["confidence"])


def predict_email(text: str) -> str:
    """Sadece YES veya NO sonucunu döndürür."""
    return str(predict_details(text)["label"])


def main() -> None:
    """İki farklı test e-postası için tahmin yapar ve sonuçları ekrana yazdırır."""
    test_email_1 = {
        "subject": "Verify Your Bank Account",
        "body": "Your account has been suspended. Click here to verify immediately.",
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
    print(f"Subject: {test_email_1['subject']}")
    print(f"Body   : {test_email_1['body']}")
    print(f"Phishing : {result_1['label']}")
    print(f"Confidence: %{result_1['confidence']:.2f}")
    print(f"Risk Score: {result_1['risk_score']:.2f}")
    print()

    print("Test 2")
    print(f"Subject: {test_email_2['subject']}")
    print(f"Body   : {test_email_2['body']}")
    print(f"Phishing : {result_2['label']}")
    print(f"Confidence: %{result_2['confidence']:.2f}")
    print(f"Risk Score: {result_2['risk_score']:.2f}")


if __name__ == "__main__":
    main()