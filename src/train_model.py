"""
Model Eğitim Scripti
Çalıştır: python src/train_model.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import train_test_split

# ── Stopword listesi (İngilizce + Türkçe) ────────────────────────────────────
STOPWORDS = {
    # İngilizce yaygın kelimeler
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "this", "that", "these", "those", "it", "its", "i", "you",
    "he", "she", "we", "they", "my", "your", "his", "her", "our", "their",
    "from", "not", "no", "so", "if", "as", "by", "up", "out", "about",
    "than", "then", "there", "here", "when", "where", "who", "which", "what",
    "all", "each", "any", "some", "more", "also", "just", "can", "us",
    # Türkçe yaygın kelimeler
    "bir", "ve", "bu", "da", "de", "ile", "için", "mi", "mı", "mu", "mü",
    "ya", "ki", "ne", "ben", "sen", "biz", "siz", "o", "onlar", "benden",
    "senden", "bizden", "sizden", "ama", "fakat", "ancak", "çünkü", "eğer",
    "gibi", "kadar", "daha", "en", "çok", "az", "hiç", "her", "bazı",
    "şu", "şey", "olan", "olan", "olarak", "olan", "var", "yok", "olan",
}

# URL pattern
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
# Sadece rakam olan token'lar
NUMBER_PATTERN = re.compile(r"^\d+$")
# Noktalama
PUNCT_PATTERN = re.compile(r"[^\w\s]")


def advanced_preprocessing(text: str) -> str:
    """
    Gelişmiş metin temizleme:
    - URL'leri <url> token'ına dönüştür (tamamen silme — varlığı önemli bir sinyal)
    - Küçük harfe çevir
    - Noktalama kaldır
    - Çok kısa token'ları at (1-2 karakter)
    - Stopword'leri kaldır
    - Fazla boşlukları temizle
    """
    if not isinstance(text, str):
        return ""

    # URL'leri token'a dönüştür
    text = URL_PATTERN.sub(" urltoken ", text)

    # Küçük harfe çevir
    text = text.lower().strip()

    # Noktalama kaldır
    text = PUNCT_PATTERN.sub(" ", text)

    # Token'lara böl, kısa ve stopword olanları çıkar
    tokens = [
        token for token in text.split()
        if len(token) > 2
        and token not in STOPWORDS
        and not NUMBER_PATTERN.match(token)
    ]

    return " ".join(tokens)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    # Temizlenmiş dataset varsa onu kullan, yoksa orijinale dön
    clean_path    = project_root / "data" / "emails_clean.csv"
    original_path = project_root / "data" / "emails.csv"

    if clean_path.exists():
        data_path = clean_path
        print(f"✅ Temizlenmiş dataset kullanılıyor: {clean_path.name}")
    else:
        data_path = original_path
        print(f"⚠️  emails_clean.csv bulunamadı, orijinal dataset kullanılıyor.")
        print(f"   Önce çalıştır: python src/prepare_dataset.py")

    model_path  = project_root / "models" / "phishing_model.pkl"
    report_path = project_root / "reports" / "train_metrics.txt"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Dataset yükle
    df = pd.read_csv(data_path)
    print(f"📦 Toplam satır: {len(df):,}")

    # Kolon kontrolü
    required = {"body", "label"}
    if not required.issubset(df.columns):
        raise ValueError(f"Dataset'te şu kolonlar eksik: {required - set(df.columns)}")

    # Preprocessing uygula
    print("⚙️  Preprocessing uygulanıyor...")
    df["clean_text"] = df["body"].apply(advanced_preprocessing)

    # Boş çıkan satırları temizle
    df = df[df["clean_text"].str.strip() != ""]

    X = df["clean_text"]
    y = df["label"].astype(int)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")

    # TF-IDF — unigram + bigram, en fazla 30,000 özellik
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=30_000,
        min_df=2,
        sublinear_tf=True,   # TF değerlerini log-scale'e çek — sık kelimelerin baskısını azaltır
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf  = vectorizer.transform(X_test)

    # Model
    model = LogisticRegression(
        max_iter=500,
        solver="liblinear",
        class_weight="balanced",
        C=1.0,
    )
    model.fit(X_train_tfidf, y_train)

    # Değerlendirme
    y_pred = model.predict(X_test_tfidf)
    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall    = recall_score(y_test, y_pred, zero_division=0)
    f1        = f1_score(y_test, y_pred, zero_division=0)

    print("\n📊 Model Performansı:")
    print(f"   Accuracy : {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall   : {recall:.4f}")
    print(f"   F1 Score : {f1:.4f}")

    # Raporu kaydet
    report = classification_report(y_test, y_pred, target_names=["Normal", "Phishing"])
    report_path.write_text(
        f"Accuracy : {accuracy:.4f}\n"
        f"Precision: {precision:.4f}\n"
        f"Recall   : {recall:.4f}\n"
        f"F1 Score : {f1:.4f}\n\n"
        f"{report}",
        encoding="utf-8",
    )
    print(f"   Rapor kaydedildi: {report_path}")

    # Model kaydet
    with open(model_path, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "model": model}, f)
    print(f"✅ Model kaydedildi: {model_path}")


if __name__ == "__main__":
    main()