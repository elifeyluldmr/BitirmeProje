"""
Dataset Analiz Scripti
Çalıştır: python src/analyze_dataset.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "emails.csv"


def main() -> None:
    print("=" * 55)
    print("  DATASET ANALİZİ")
    print("=" * 55)

    df = pd.read_csv(DATA_PATH)

    # ── Temel bilgiler ──────────────────────────────────────
    print(f"\n📦 Toplam satır   : {len(df):,}")
    print(f"📋 Kolonlar       : {list(df.columns)}")

    # ── Label dağılımı ──────────────────────────────────────
    print("\n📊 Label Dağılımı:")
    dist = df["label"].value_counts()
    for label, count in dist.items():
        pct = count / len(df) * 100
        print(f"   {label} → {count:,} satır  (%{pct:.1f})")

    # ── Boş değerler ────────────────────────────────────────
    print("\n🕳️  Boş Değerler:")
    for col in df.columns:
        null_count = df[col].isnull().sum()
        empty_count = (df[col].astype(str).str.strip() == "").sum()
        total_missing = null_count + empty_count
        if total_missing > 0:
            print(f"   {col}: {total_missing:,} eksik")
        else:
            print(f"   {col}: ✓ temiz")

    # ── Metin uzunluğu istatistikleri ───────────────────────
    print("\n📏 Metin Uzunluğu (karakter):")
    for col in ["subject", "body"]:
        if col in df.columns:
            lengths = df[col].astype(str).str.len()
            print(f"   {col}:")
            print(f"      Ortalama : {lengths.mean():.0f}")
            print(f"      Minimum  : {lengths.min()}")
            print(f"      Maksimum : {lengths.max()}")

    # ── Tekrar eden satırlar ─────────────────────────────────
    dup_count = df.duplicated().sum()
    print(f"\n🔁 Tekrar Eden Satır: {dup_count:,}")

    # ── Örnek satırlar ───────────────────────────────────────
    print("\n📌 Phishing Örnekler (ilk 3):")
    phishing_df = df[df["label"].isin([1, "1", "phishing", "spam"])].head(3)
    for _, row in phishing_df.iterrows():
        subj = str(row.get("subject", ""))[:60]
        body = str(row.get("body", ""))[:80]
        print(f"   Subject: {subj}")
        print(f"   Body   : {body}")
        print()

    print("📌 Normal Örnekler (ilk 3):")
    normal_df = df[df["label"].isin([0, "0", "legitimate", "ham"])].head(3)
    for _, row in normal_df.iterrows():
        subj = str(row.get("subject", ""))[:60]
        body = str(row.get("body", ""))[:80]
        print(f"   Subject: {subj}")
        print(f"   Body   : {body}")
        print()

    print("=" * 55)
    print("  Analiz tamamlandı.")
    print("=" * 55)


if __name__ == "__main__":
    main()