"""
Dataset Temizleme Scripti
Çalıştır: python src/prepare_dataset.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

DATA_PATH   = Path(__file__).resolve().parents[1] / "data" / "emails_clean.csv"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "emails_clean.csv"


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    print("\n🧹 Temizleme başlıyor...")
    original_len = len(df)

    if "subject" in df.columns:
        if df["subject"].isnull().mean() > 0.9:
            df = df.drop(columns=["subject"])
            print("   ✓ Subject kolonu kaldırıldı (büyük çoğunluğu boş)")

    df = df[df["body"].notna()]
    df = df[df["body"].astype(str).str.strip() != ""]
    df = df[df["body"].astype(str).str.strip().str.lower() != "nan"]
    df = df[df["body"].astype(str).str.len() >= 20]
    print("   ✓ Çok kısa satırlar kaldırıldı (< 20 karakter)")
    df = df[df["body"].astype(str).str.len() <= 100_000]
    print("   ✓ Anormal uzun satırlar kaldırıldı (> 100,000 karakter)")

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["body"])
    print(f"   ✓ {before_dedup - len(df):,} tekrar eden satır kaldırıldı")

    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df[df["label"].isin([0, 1])]
    df["label"] = df["label"].astype(int)

    print(f"   ✓ Temizleme tamamlandı: {original_len:,} → {len(df):,} satır")
    return df.reset_index(drop=True)


def print_summary(df: pd.DataFrame) -> None:
    print("\n📊 Dataset Özeti:")
    print(f"   Toplam satır : {len(df):,}")
    for label, count in df["label"].value_counts().sort_index().items():
        name = "Phishing" if label == 1 else "Normal"
        pct = count / len(df) * 100
        print(f"   {name} ({label}) : {count:,} (%{pct:.1f})")


def main() -> None:
    print("=" * 55)
    print("  DATASET TEMİZLEME")
    print("=" * 55)

    if not DATA_PATH.exists():
        print(f"❌ {DATA_PATH} bulunamadı.")
        print("   Önce çalıştırın: python src/download_datasets.py")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"📦 Orijinal satır sayısı: {len(df):,}")

    df = clean_dataframe(df)
    print_summary(df)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\n✅ Temizlenmiş dataset kaydedildi: {OUTPUT_PATH}")
    print("=" * 55)
    print("Şimdi modeli yeniden eğit:")
    print("   python src/train_model.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
