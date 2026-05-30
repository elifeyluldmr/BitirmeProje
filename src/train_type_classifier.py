"""
Phishing Tür Sınıflandırıcısı — Eğitim Scripti

Mevcut emails_clean.csv üzerindeki phishing e-postalarını kural tabanlı olarak
tür etiketiyle işaretler, ardından TF-IDF + Logistic Regression ile çok sınıflı
bir model eğitir.

Çalıştır: python src/train_type_classifier.py
"""

from __future__ import annotations

import sys
import pickle
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

from src.text_utils import advanced_preprocessing

# ── Tür etiket sözlüğü (kural bazlı ön etiketleme için) ─────────────────────
_TYPE_RULES: dict[str, list[str]] = {
    "Finansal Dolandırıcılık": [
        "bank", "payment", "invoice", "tax", "refund", "credit", "wire transfer",
        "banka", "ödeme", "fatura", "vergi", "iade", "kredi", "transfer", "borç",
        "account number", "routing", "western union", "moneygram", "bitcoin",
        "cryptocurrency", "wallet", "fund", "lottery", "prize money",
    ],
    "Kimlik Hırsızlığı": [
        "login", "password", "verify", "account", "username", "credential",
        "giriş", "şifre", "doğrula", "hesap", "parola", "kimlik",
        "social security", "ssn", "date of birth", "mother maiden",
        "security question", "pin", "passcode", "two factor", "authentication",
    ],
    "Kötü Amaçlı Link": [
        "click here", "click the link", "download", "install", "attachment",
        "tıkla", "bağlantı", "indir", "yükle", "ek dosya",
        "open attachment", "view document", "access file", "free software",
        "update required", "virus", "malware", "ransomware",
    ],
    "Sahte Ödül/Çekiliş": [
        "winner", "prize", "congratulations", "selected", "reward", "lottery",
        "kazandınız", "ödül", "tebrikler", "seçildiniz", "çekiliş",
        "you have been chosen", "claim your prize", "free gift", "giveaway",
        "sweepstakes", "jackpot", "million dollar",
    ],
    "Sahte Kargo/Teslimat": [
        "delivery", "package", "shipment", "tracking", "fedex", "ups", "dhl",
        "teslimat", "kargo", "takip", "paket", "gönderim",
        "order confirmation", "your order", "shipping label", "customs",
        "parcel", "courier",
    ],
    "Marka Taklidi": [
        "paypal", "amazon", "microsoft", "apple", "google", "netflix", "facebook",
        "instagram", "twitter", "linkedin", "ebay", "walmart",
        "your account has been", "unusual activity", "suspicious login",
        "verify your identity", "confirm your email", "update your information",
    ],
}

TYPE_LABELS = list(_TYPE_RULES.keys()) + ["Genel Phishing"]
TYPE_TO_INT = {t: i for i, t in enumerate(TYPE_LABELS)}
INT_TO_TYPE = {i: t for t, i in TYPE_TO_INT.items()}


def _auto_label(text: str) -> str:
    """Metin içeriğine göre kural tabanlı tür etiketi döndürür."""
    text_lower = text.lower()
    scores: dict[str, int] = {t: 0 for t in _TYPE_RULES}
    for type_name, keywords in _TYPE_RULES.items():
        for kw in keywords:
            if kw in text_lower:
                scores[type_name] += 1
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "Genel Phishing"


def build_labeled_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Phishing e-postalarına tür etiketi ekler."""
    phishing_df = df[df["label"] == 1].copy()
    phishing_df["phishing_type"] = phishing_df["body"].apply(_auto_label)
    phishing_df["type_int"] = phishing_df["phishing_type"].map(TYPE_TO_INT)
    return phishing_df.reset_index(drop=True)


def train(data_path: Path, model_dir: Path) -> None:
    print("📦 Dataset yükleniyor...")
    df = pd.read_csv(data_path)
    labeled = build_labeled_dataset(df)

    print(f"   Toplam phishing e-posta: {len(labeled):,}")
    print("\n📊 Tür dağılımı:")
    for t, cnt in labeled["phishing_type"].value_counts().items():
        pct = cnt / len(labeled) * 100
        print(f"   {t:<30}: {cnt:,}  (%{pct:.1f})")

    print("\n⚙️  Preprocessing uygulanıyor...")
    labeled["clean_text"] = labeled["body"].apply(advanced_preprocessing)
    labeled = labeled[labeled["clean_text"].str.strip() != ""]

    X = labeled["clean_text"]
    y = labeled["type_int"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=20_000,
        min_df=2,
        sublinear_tf=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    model = LogisticRegression(
        max_iter=500,
        solver="lbfgs",
        class_weight="balanced",
        C=1.0,
    )
    model.fit(X_train_tfidf, y_train)

    y_pred = model.predict(X_test_tfidf)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n📊 Tür Sınıflandırıcı Performansı:")
    print(f"   Accuracy: {acc:.4f}")
    print(classification_report(
        y_test, y_pred,
        target_names=[INT_TO_TYPE[i] for i in sorted(INT_TO_TYPE)],
        zero_division=0,
    ))

    model_dir.mkdir(parents=True, exist_ok=True)
    out_path = model_dir / "type_classifier.pkl"
    with open(out_path, "wb") as f:
        pickle.dump({
            "model": model,
            "vectorizer": vectorizer,
            "int_to_type": INT_TO_TYPE,
            "type_to_int": TYPE_TO_INT,
        }, f)
    print(f"✅ Tür sınıflandırıcı kaydedildi: {out_path}")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    clean_path = project_root / "data" / "emails_clean.csv"
    original_path = project_root / "data" / "emails.csv"
    data_path = clean_path if clean_path.exists() else original_path

    if not data_path.exists():
        print(f"❌ Dataset bulunamadı: {data_path}")
        return

    train(data_path, project_root / "models")


if __name__ == "__main__":
    main()
