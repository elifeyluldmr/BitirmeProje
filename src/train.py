from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "emails.csv"
    model_dir = project_root / "models"
    report_dir = project_root / "reports"

    model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. Expected columns: text,label"
        )

    df = pd.read_csv(data_path)
    required_cols = {"text", "label"}
    if not required_cols.issubset(df.columns):
        raise ValueError("Dataset must contain columns: text,label")

    x_train, x_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=30000)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )

    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    report = classification_report(y_test, y_pred)
    (report_dir / "classification_report.txt").write_text(report, encoding="utf-8")

    joblib.dump(model, model_dir / "phishing_model.joblib")
    print("Training complete. Model saved to models/phishing_model.joblib")


if __name__ == "__main__":
    main()
