from __future__ import annotations

import re
import pickle
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

try:
    from src.config import (
        ANOMALY_N_ESTIMATORS, ANOMALY_CONTAMINATION, ANOMALY_RANDOM_STATE,
        ANOMALY_SCORE_OFFSET, ANOMALY_SCORE_SCALE,
    )
except ModuleNotFoundError:
    from config import (
        ANOMALY_N_ESTIMATORS, ANOMALY_CONTAMINATION, ANOMALY_RANDOM_STATE,
        ANOMALY_SCORE_OFFSET, ANOMALY_SCORE_SCALE,
    )

# Yüklenen model burada tutuluyor, her tahmin için diskten okumak yavaş olur
_anomaly_cache: dict = {}


def extract_features(text: str) -> list[float]:
    # TF-IDF yerine elle tasarlanmış 9 özellik kullanıyoruz, yorumlanması daha kolay
    try:
        from src.text_utils import find_suspicious_keywords  # modül olarak çalıştırılınca
    except ModuleNotFoundError:
        from text_utils import find_suspicious_keywords      # script olarak çalıştırılınca

    words       = text.split()
    total_words = max(len(words), 1)
    total_chars = max(len(text), 1)

    # Her özellik ayrı bir phishing belirtisini ölçüyor
    url_count       = len(re.findall(r"https?://\S+|www\.\S+", text))
    exclaim_count   = text.count("!")
    caps_ratio      = sum(1 for w in words if w.isupper() and len(w) > 1) / total_words
    digit_ratio     = sum(c.isdigit() for c in text) / total_chars
    special_density = sum(c in "!?$@#%" for c in text) / total_chars
    avg_word_len    = sum(len(w) for w in words) / total_words
    keyword_count   = len(find_suspicious_keywords(text))
    char_count_norm = min(len(text) / 1000, 10)
    link_keyword    = 1 if re.search(r"click|link", text.lower()) else 0

    # Aşırı büyük değerlerin modeli bozmaması için üst sınır koyuyoruz
    return [
        char_count_norm,
        min(url_count, 10),
        min(exclaim_count, 10),
        caps_ratio,
        digit_ratio,
        min(special_density * 100, 1),
        avg_word_len,
        min(keyword_count, 15),
        float(link_keyword),
    ]


def train_anomaly_model(normal_texts: list[str]) -> IsolationForest:
    # Sadece normal e-postalar üzerinde eğitiyoruz, model "normal"i öğreniyor
    print(f"   Anomali modeli eğitiliyor ({len(normal_texts):,} normal e-posta)...")
    features = np.array([extract_features(t) for t in normal_texts])

    # n_jobs=-1 ile tüm CPU çekirdeklerini kullanıyoruz, eğitim daha hızlı bitiyor
    model = IsolationForest(
        n_estimators=ANOMALY_N_ESTIMATORS,
        contamination=ANOMALY_CONTAMINATION,
        random_state=ANOMALY_RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(features)
    return model


def load_anomaly_model() -> object | None:
    # Dosya değişmediyse cache'den dön
    project_root = Path(__file__).resolve().parents[1]
    model_path   = project_root / "models" / "anomaly_model.pkl"

    if not model_path.exists():
        return None

    # Dosya değiştiyse yeniden yükle, değişmediyse cache yeterli
    mtime = model_path.stat().st_mtime
    if "model" in _anomaly_cache and _anomaly_cache.get("mtime") == mtime:
        return _anomaly_cache["model"]

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    _anomaly_cache["model"] = model
    _anomaly_cache["mtime"] = mtime
    return model


def get_anomaly_score(text: str) -> dict:
    # Model yoksa skor üretemeyiz, available=False ile bunu bildiriyoruz
    model = load_anomaly_model()
    if model is None:
        return {"score": 0, "is_anomaly": False, "available": False}

    features = np.array(extract_features(text)).reshape(1, -1)

    # -1 anormal, 1 normal demek; ham skor ne kadar negatifse o kadar anormal
    pred      = model.predict(features)[0]
    raw_score = model.decision_function(features)[0]

    # Ham skoru 0-100 aralığına çekiyoruz, yüksek = daha anormal
    anomaly_score = max(0.0, min(100.0, (-raw_score + ANOMALY_SCORE_OFFSET) * ANOMALY_SCORE_SCALE))

    return {
        "score":      round(float(anomaly_score), 1),
        "is_anomaly": bool(pred == -1),
        "available":  True,
    }
