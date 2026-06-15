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


def merge_extra_csvs(base_df: pd.DataFrame) -> pd.DataFrame:
    """data/ klasöründeki ek CSV dosyalarını base_df ile birleştirir.

    Geçerli ek CSV: emails_clean.csv ve emails.csv dışındaki,
    'body' ve 'label' kolonlarına sahip dosyalar.
    Ayrıca 'text'+'label' veya 'message'+'label' kolonları da kabul edilir.
    """
    data_dir = Path(DATA_PATH).parent
    skip = {"emails_clean.csv", "emails.csv", "emails.sample.csv"}
    extra_files = [
        p for p in data_dir.glob("*.csv")
        if p.name not in skip and p.stat().st_size > 100
    ]

    if not extra_files:
        return base_df

    frames = [base_df]
    for path in extra_files:
        try:
            extra = pd.read_csv(path)
            extra.columns = [c.strip().lower() for c in extra.columns]

            # body kolonu bul
            body_col = next(
                (c for c in extra.columns if c in ("body", "text", "message", "email", "content")),
                None,
            )
            # label kolonu bul
            label_col = next(
                (c for c in extra.columns if c in ("label", "labels", "spam", "type", "class")),
                None,
            )

            if body_col is None or label_col is None:
                print(f"   ⚠️  {path.name} atlandı — body/label kolonu bulunamadı")
                continue

            extra = extra[[body_col, label_col]].rename(columns={body_col: "body", label_col: "label"})
            extra["body"]  = extra["body"].astype(str).str.strip()
            extra["label"] = pd.to_numeric(extra["label"], errors="coerce")
            extra = extra[extra["label"].isin([0, 1])].dropna(subset=["body"])
            extra["label"] = extra["label"].astype(int)
            extra = extra[extra["body"].str.len() >= 20]

            frames.append(extra)
            print(f"   ✅ {path.name}: {len(extra):,} satır eklendi")
        except Exception as exc:
            print(f"   ⚠️  {path.name} atlandı — {exc}")

    if len(frames) == 1:
        return base_df

    combined = pd.concat(frames, ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates(subset=["body"]).reset_index(drop=True)
    print(f"   ✓ Birleştirme sonrası: {before:,} → {len(combined):,} (dedup)")
    return combined


def main() -> None:
    print("=" * 55)
    print("  DATASET TEMİZLEME & BİRLEŞTİRME")
    print("=" * 55)

    if not DATA_PATH.exists():
        print(f"❌ {DATA_PATH} bulunamadı.")
        print("   Önce çalıştırın: python src/download_datasets.py")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"📦 Temel dataset: {len(df):,} satır")

    df = clean_dataframe(df)

    print("\n📂 Ek CSV dosyaları birleştiriliyor...")
    df = merge_extra_csvs(df)

    print_summary(df)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\n✅ Güncellenmiş dataset kaydedildi: {OUTPUT_PATH}")
    print("=" * 55)
    print("Şimdi modeli yeniden eğit:")
    print("   python src/train_model.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
