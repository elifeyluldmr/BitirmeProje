from pathlib import Path
import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

try:
    from src.text_utils import build_email_text, preprocessing
except ModuleNotFoundError:
    from text_utils import build_email_text, preprocessing


def main() -> None:
    # Proje içindeki temel klasörleri ve dosya yollarını hazırla.
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "emails.csv"
    model_path = project_root / "models" / "phishing_model.pkl"

    # Model klasörü yoksa oluştur.
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # CSV dosyasını oku.
    df = pd.read_csv(data_path)

    # Gerekli kolonların varlığını kontrol et.
    required_columns = {"subject", "body", "label"}
    if not required_columns.issubset(df.columns):
        raise ValueError("CSV dosyasında 'subject', 'body' ve 'label' kolonları bulunmalıdır.")

    # Subject ve body alanlarını birleştirerek tek metin kolonu oluştur.
    df["text"] = df.apply(
        lambda row: build_email_text(row["subject"], row["body"]), axis=1
    )

    # Preprocessing fonksiyonunu çağırıp temizlenmiş metni yeni kolona yaz.
    df["clean_text"] = df["text"].apply(preprocessing)

    # Özellikler (X) ve etiketler (y) ayrılır.
    X = df["clean_text"]
    y = df["label"]

    # Veriyi %80 eğitim, %20 test olacak şekilde böl.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # TF-IDF ile metni sayısal forma dönüştür.
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=30000, min_df=2)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Logistic Regression modeli oluştur ve eğit.
    model = LogisticRegression(max_iter=500, solver="liblinear", class_weight="balanced")
    model.fit(X_train_tfidf, y_train)

    # Test verisi üzerinde tahmin yap.
    y_pred = model.predict(X_test_tfidf)

    # Değerlendirme metriklerini hesapla.
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="binary", zero_division=0)
    recall = recall_score(y_test, y_pred, average="binary", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="binary", zero_division=0)

    # Sonuçları ekrana yazdır.
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    # Model ve vectorizer'ı pickle ile kaydet.
    with open(model_path, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "model": model}, f)

    print(f"Model kaydedildi: {model_path}")


if __name__ == "__main__":
    main()
