"""
Halka açık phishing/spam datasetlerini indirir ve emails_clean.csv ile birleştirir.
Çalıştır: python src/download_datasets.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from datasets import load_dataset


def load_enron_spam() -> pd.DataFrame:
    """SetFit/enron_spam — 33k gerçek Enron e-postası (spam/ham)."""
    rows = []
    for split in ("train", "test"):
        d = load_dataset("SetFit/enron_spam", split=split)
        for item in d:
            body = str(item.get("text") or item.get("message") or "").strip()
            if body:
                rows.append({"body": body, "label": int(item["label"])})
    df = pd.DataFrame(rows)
    print(f"  Enron spam     : {len(df):,} satır "
          f"(spam={int((df.label==1).sum()):,}, ham={int((df.label==0).sum()):,})")
    return df


def load_sms_spam() -> pd.DataFrame:
    """sms_spam — 5.5k SMS spam/ham."""
    d = load_dataset("sms_spam", split="train")
    rows = []
    for item in d:
        body = str(item["sms"]).strip()
        if body:
            rows.append({"body": body, "label": int(item["label"])})
    df = pd.DataFrame(rows)
    print(f"  SMS spam       : {len(df):,} satır "
          f"(spam={int((df.label==1).sum()):,}, ham={int((df.label==0).sum()):,})")
    return df


def load_deysi_spam() -> pd.DataFrame:
    """Deysi/spam-detection-dataset — 8k e-posta spam/ham."""
    d = load_dataset("Deysi/spam-detection-dataset", split="train")
    label_map = {"spam": 1, "not_spam": 0, "ham": 0, "1": 1, "0": 0}
    rows = []
    for item in d:
        body = str(item["text"]).strip()
        raw = str(item["label"]).lower().strip()
        label = label_map.get(raw)
        if body and label is not None:
            rows.append({"body": body, "label": label})
    df = pd.DataFrame(rows)
    print(f"  Deysi spam     : {len(df):,} satır "
          f"(spam={int((df.label==1).sum()):,}, ham={int((df.label==0).sum()):,})")
    return df


def load_language_id_turkish() -> pd.DataFrame:
    """papluca/language-identification — Türkçe cümleler, normal e-posta olarak etiketlenir."""
    d = load_dataset("papluca/language-identification", split="train")
    rows = []
    for item in d:
        if str(item.get("labels", "")).strip() == "tr":
            body = str(item["text"]).strip()
            if body and len(body) > 20:
                rows.append({"body": body, "label": 0})
    df = pd.DataFrame(rows)
    print(f"  TR lang-id     : {len(df):,} satır (normal, Türkçe)")
    return df


def load_language_id_english_normal() -> pd.DataFrame:
    """papluca/language-identification — İngilizce cümleler, normal olarak etiketlenir."""
    d = load_dataset("papluca/language-identification", split="train")
    rows = []
    for item in d:
        if str(item.get("labels", "")).strip() == "en":
            body = str(item["text"]).strip()
            if body and len(body) > 20:
                rows.append({"body": body, "label": 0})
    df = pd.DataFrame(rows)
    print(f"  EN lang-id     : {len(df):,} satır (normal, İngilizce)")
    return df


LOADERS = [
    load_enron_spam,
    load_sms_spam,
    load_deysi_spam,
    load_language_id_turkish,
    load_language_id_english_normal,
]


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    clean_path   = project_root / "data" / "emails_clean.csv"

    print("📥 Datasetler indiriliyor...\n")
    frames = []
    for loader in LOADERS:
        try:
            frames.append(loader())
        except Exception as e:
            print(f"  HATA {loader.__name__}: {e}")

    if not frames:
        print("❌ Hiçbir dataset indirilemedi.")
        return

    new_df = pd.concat(frames, ignore_index=True)
    new_df = new_df.dropna(subset=["body"])
    new_df["body"] = new_df["body"].astype(str).str.strip()
    new_df = new_df[new_df["body"] != ""]

    print(f"\n📦 Toplam yeni   : {len(new_df):,} satır")

    if clean_path.exists():
        existing = pd.read_csv(clean_path)
        print(f"📦 Mevcut dataset: {len(existing):,} satır")
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df

    combined = combined.drop_duplicates(subset=["body"]).reset_index(drop=True)
    combined.to_csv(clean_path, index=False)

    print(f"\n✅ Birleştirilmiş : {len(combined):,} satır")
    print(f"   Label 0 (normal/ham)  : {int((combined.label==0).sum()):,}")
    print(f"   Label 1 (phishing/spam): {int((combined.label==1).sum()):,}")
    print(f"   Kaydedildi: {clean_path}")


if __name__ == "__main__":
    main()
