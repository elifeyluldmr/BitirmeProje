"""
Anomali Tespiti — Isolation Forest
Normal e-postalardan öğrenir; kalıptan sapan e-postaları şüpheli işaretler.
Model train_model.py çalıştırılınca otomatik eğitilir ve kaydedilir.
"""
from __future__ import annotations

import re
import pickle
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

_anomaly_cache: dict = {}


def extract_features(text: str) -> list[float]:
    """E-postadan 9 sayısal özellik çıkarır — TF-IDF bağımsız, yorumlanabilir."""
    try:
        from src.text_utils import find_suspicious_keywords
    except ModuleNotFoundError:
        from text_utils import find_suspicious_keywords

    words       = text.split()
    total_words = max(len(words), 1)
    total_chars = max(len(text), 1)

    url_count       = len(re.findall(r"https?://\S+|www\.\S+", text))
    exclaim_count   = text.count("!")
    caps_ratio      = sum(1 for w in words if w.isupper() and len(w) > 1) / total_words
    digit_ratio     = sum(c.isdigit() for c in text) / total_chars
    special_density = sum(c in "!?$@#%" for c in text) / total_chars
    avg_word_len    = sum(len(w) for w in words) / total_words
    keyword_count   = len(find_suspicious_keywords(text))
    char_count_norm = min(len(text) / 1000, 10)
    link_keyword    = 1 if re.search(r"click|tikla|tıkla|buraya|link", text.lower()) else 0

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
    """Normal e-postalar üzerinde Isolation Forest eğitir."""
    print(f"   Anomali modeli eğitiliyor ({len(normal_texts):,} normal e-posta)...")
    features = np.array([extract_features(t) for t in normal_texts])

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(features)
    return model


def load_anomaly_model() -> object | None:
    """Kaydedilmiş anomali modelini önbellekli yükler."""
    project_root = Path(__file__).resolve().parents[1]
    model_path   = project_root / "models" / "anomaly_model.pkl"

    if not model_path.exists():
        return None

    mtime = model_path.stat().st_mtime
    if "model" in _anomaly_cache and _anomaly_cache.get("mtime") == mtime:
        return _anomaly_cache["model"]

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    _anomaly_cache["model"]  = model
    _anomaly_cache["mtime"]  = mtime
    return model


def get_anomaly_score(text: str) -> dict:
    """E-posta için anomali skoru döndürür.

    score      : 0-100, yüksek = daha anormal
    is_anomaly : True ise model 'normal kalıp dışı' dedi
    available  : Anomali modeli yüklendiyse True
    """
    model = load_anomaly_model()
    if model is None:
        return {"score": 0, "is_anomaly": False, "available": False}

    features  = np.array(extract_features(text)).reshape(1, -1)
    pred      = model.predict(features)[0]          # -1=anomaly, 1=normal
    raw_score = model.decision_function(features)[0]

    # Negatif raw_score → daha anormal; 0-100 aralığına normalize et
    anomaly_score = max(0.0, min(100.0, (-raw_score + 0.3) * 120))

    return {
        "score":      round(float(anomaly_score), 1),
        "is_anomaly": bool(pred == -1),
        "available":  True,
    }
