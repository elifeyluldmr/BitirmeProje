"""
Gerçek phishing/spam datasetlerini HuggingFace ve yerel zip'ten indirir,
birleştirerek emails_clean.csv olarak kaydeder.

Çalıştır: python src/download_datasets.py

Kaynaklar (tümü gerçek, halka açık):
  1. SetFit/enron_spam               — 33k Enron e-postası
  2. sms_spam                        — 5.5k SMS spam/ham
  3. Deysi/spam-detection-dataset    — 8k e-posta
  4. Yerel Kaggle zip                — ~18k Kaggle phishing e-postası
  5. ealvaradob/phishing-emails      — phishing/safe e-posta
  6. knowledgator/phishing-email-detection — phishing dataset
  7. prasanthsasikumar/phishing-emails     — phishing dataset
  8. TrainingDataPro/phishing-emails       — phishing dataset
"""
from __future__ import annotations

import sys
import zipfile
import io
import subprocess
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from datasets import load_dataset


# ── Yardımcı: label normalize ─────────────────────────────────────────────────

_LABEL_MAP = {
    "phishing": 1, "phishing email": 1, "spam": 1,
    "1": 1, "true": 1, "yes": 1, "malicious": 1,
    "safe": 0, "safe email": 0, "ham": 0, "not_spam": 0, "legitimate": 0,
    "0": 0, "false": 0, "no": 0, "benign": 0,
}


def _norm_label(raw) -> int | None:
    return _LABEL_MAP.get(str(raw).strip().lower())


def _to_df(rows: list[dict], source: str) -> pd.DataFrame:
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["body", "label"])
    ph = int((df.label == 1).sum()) if len(df) else 0
    nm = int((df.label == 0).sum()) if len(df) else 0
    print(f"  {source:<40}: {len(df):>7,}  (phishing={ph:,}, normal={nm:,})")
    return df


# ── 1. Enron spam ─────────────────────────────────────────────────────────────

def load_enron_spam() -> pd.DataFrame:
    rows = []
    for split in ("train", "test"):
        d = load_dataset("SetFit/enron_spam", split=split)
        for item in d:
            body = str(item.get("text") or item.get("message") or "").strip()
            if body:
                rows.append({"body": body, "label": int(item["label"])})
    return _to_df(rows, "SetFit/enron_spam")


# ── 2. SMS spam ───────────────────────────────────────────────────────────────

def load_sms_spam() -> pd.DataFrame:
    d = load_dataset("sms_spam", split="train")
    rows = [{"body": str(i["sms"]).strip(), "label": int(i["label"])}
            for i in d if str(i["sms"]).strip()]
    return _to_df(rows, "sms_spam")


# ── 3. Deysi spam ─────────────────────────────────────────────────────────────

def load_deysi_spam() -> pd.DataFrame:
    d = load_dataset("Deysi/spam-detection-dataset", split="train")
    rows = []
    for item in d:
        lbl = _norm_label(item["label"])
        body = str(item["text"]).strip()
        if body and lbl is not None:
            rows.append({"body": body, "label": lbl})
    return _to_df(rows, "Deysi/spam-detection-dataset")


# ── 4. Kaggle yerel zip ────────────────────────────────────────────────────────

def load_kaggle_phishing_zip() -> pd.DataFrame:
    """dataphishing_dataset.zip içindeki Phishing_Email.csv — BytesIO ile okur."""
    project_root = Path(__file__).resolve().parents[1]
    candidates = [
        project_root / "data" / "dataphishing_dataset.zip.zip",  # gerçek dosya
        project_root / "data" / "dataphishing_dataset.zip",      # OneDrive placeholder
    ]

    # 0-byte placeholder'ları atla
    zip_path = next((p for p in candidates if p.exists() and p.stat().st_size > 0), None)
    if zip_path is None:
        print(f"  {'Kaggle zip':<40}: bulunamadı, atlanıyor.")
        return pd.DataFrame(columns=["body", "label"])

    try:
        # Önce pathlib.read_bytes() dene, olmadı PowerShell Expand-Archive kullan
        try:
            zip_bytes = io.BytesIO(zip_path.read_bytes())
            zip_src = zip_bytes
        except PermissionError:
            # OneDrive kilitli — PowerShell ile geçici dizine çıkart
            tmp_dir = tempfile.mkdtemp()
            subprocess.run(
                ["powershell", "-Command",
                 f'Expand-Archive -Path "{zip_path}" -DestinationPath "{tmp_dir}" -Force'],
                capture_output=True, check=True,
            )
            # Çıkartılan CSV'yi bul ve oku
            csv_files = list(Path(tmp_dir).rglob("*.csv"))
            if not csv_files:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                print(f"  {'Kaggle zip':<40}: CSV çıkartılamadı.")
                return pd.DataFrame(columns=["body", "label"])
            df_raw = pd.read_csv(csv_files[0])
            shutil.rmtree(tmp_dir, ignore_errors=True)
            df_raw.columns = [c.strip().lower() for c in df_raw.columns]
            body_col  = next((c for c in df_raw.columns if "text" in c or "body" in c or "email" in c), df_raw.columns[0])
            label_col = next((c for c in df_raw.columns if "type" in c or "label" in c or "class" in c), df_raw.columns[-1])
            rows = []
            for _, row in df_raw.iterrows():
                body = str(row[body_col]).strip()
                lbl  = _norm_label(row[label_col])
                if body and lbl is not None and len(body) >= 20:
                    rows.append({"body": body, "label": lbl})
            return _to_df(rows, "Kaggle zip (PowerShell)")
        zip_src = zip_bytes

        # İç içe zip varsa (zip.zip) tekrar aç
        with zipfile.ZipFile(zip_src) as outer:
            names = outer.namelist()
            # İçinde zip varsa onu da aç
            inner_zips = [n for n in names if n.endswith(".zip")]
            csv_files  = [n for n in names if n.endswith(".csv")]

            if inner_zips and not csv_files:
                inner_bytes = io.BytesIO(outer.read(inner_zips[0]))
                with zipfile.ZipFile(inner_bytes) as inner:
                    csv_files = [n for n in inner.namelist() if n.endswith(".csv")]
                    csv_name  = csv_files[0]
                    with inner.open(csv_name) as f:
                        df_raw = pd.read_csv(f)
            elif csv_files:
                csv_name = csv_files[0]
                with outer.open(csv_name) as f:
                    df_raw = pd.read_csv(f)
            else:
                print(f"  {'Kaggle zip':<40}: CSV bulunamadı.")
                return pd.DataFrame(columns=["body", "label"])

        # Kolon normalize
        df_raw.columns = [c.strip().lower() for c in df_raw.columns]
        body_col  = next((c for c in df_raw.columns if "text" in c or "body" in c or "email" in c), df_raw.columns[0])
        label_col = next((c for c in df_raw.columns if "type" in c or "label" in c or "class" in c), df_raw.columns[-1])

        rows = []
        for _, row in df_raw.iterrows():
            body = str(row[body_col]).strip()
            lbl  = _norm_label(row[label_col])
            if body and lbl is not None and len(body) >= 20:
                rows.append({"body": body, "label": lbl})

        return _to_df(rows, f"Kaggle zip ({csv_name[:25]})")

    except Exception as exc:
        print(f"  {'Kaggle zip':<40}: hata — {exc}")
        return pd.DataFrame(columns=["body", "label"])


# ── 5-7. HuggingFace phishing datasetleri ─────────────────────────────────────

def _load_hf_generic(
    repo_id: str,
    splits: tuple = ("train",),
    text_fields: tuple = ("text", "body", "email", "Email Text", "message", "content"),
    label_fields: tuple = ("label", "Email Type", "type", "class", "spam"),
) -> pd.DataFrame:
    """Genel HuggingFace yükleyicisi — farklı kolon isimlerini otomatik bulur."""
    rows = []
    for split in splits:
        try:
            d = load_dataset(repo_id, split=split)
            if len(d) == 0:
                continue
            sample = d[0]

            body_key  = next((k for k in text_fields  if k in sample), None)
            label_key = next((k for k in label_fields if k in sample), None)

            if body_key is None or label_key is None:
                # Son çare: ilk iki kolon
                keys = list(sample.keys())
                if len(keys) >= 2:
                    body_key, label_key = keys[0], keys[-1]
                else:
                    continue

            for item in d:
                body = str(item.get(body_key, "")).strip()
                lbl  = _norm_label(item.get(label_key, ""))
                if body and lbl is not None and len(body) >= 20:
                    rows.append({"body": body, "label": lbl})
        except Exception:
            continue

    return _to_df(rows, repo_id)


def load_ealvaradob() -> pd.DataFrame:
    return _load_hf_generic(
        "ealvaradob/phishing-emails",
        splits=("train", "test"),
        text_fields=("text", "body", "email", "Email Text", "message"),
        label_fields=("label", "Email Type", "type", "class"),
    )


def load_knowledgator() -> pd.DataFrame:
    return _load_hf_generic(
        "knowledgator/phishing-email-detection",
        splits=("train", "test", "validation"),
    )


def load_prasanth() -> pd.DataFrame:
    return _load_hf_generic(
        "prasanthsasikumar/phishing-emails",
        splits=("train",),
    )


def load_trainingdatapro() -> pd.DataFrame:
    return _load_hf_generic(
        "TrainingDataPro/phishing-emails",
        splits=("train",),
    )


def load_fathyshalab() -> pd.DataFrame:
    return _load_hf_generic(
        "fathyshalab/spam_ham",
        splits=("train", "test"),
    )


def load_shahidul() -> pd.DataFrame:
    return _load_hf_generic(
        "shahidul034/email_phishing_dataset",
        splits=("train", "test"),
    )


def load_cybersectony() -> pd.DataFrame:
    return _load_hf_generic(
        "cybersectony/PhishingEmailDetection",
        splits=("train", "test", "validation"),
        text_fields=("text", "body", "email_text", "Email Text", "message", "content"),
        label_fields=("label", "Email Type", "type", "class", "phishing"),
    )


def load_talby_enron() -> pd.DataFrame:
    return _load_hf_generic(
        "talby/enron-email-dataset",
        splits=("train", "test"),
    )


def load_jacecarter() -> pd.DataFrame:
    return _load_hf_generic(
        "JaceCarter/phishing-email-dataset",
        splits=("train",),
    )


def load_gchhablani() -> pd.DataFrame:
    return _load_hf_generic(
        "gchhablani/spam-email-dataset",
        splits=("train", "test"),
    )


def load_chizhikchi() -> pd.DataFrame:
    return _load_hf_generic(
        "chizhikchi/email-spam",
        splits=("train",),
    )


# ── 8. Türkçe spam datasetleri ───────────────────────────────────────────────

def load_turkish_email_spam() -> pd.DataFrame:
    """anilguven/turkish_spam_email — 1 k Türkçe e-posta spam/ham."""
    return _load_hf_generic(
        "anilguven/turkish_spam_email",
        splits=("train", "test"),
        text_fields=("text", "body"),
        label_fields=("labels", "label"),
    )


def load_zefang_phishing() -> pd.DataFrame:
    """zefang-liu/phishing-email-dataset — 18 k phishing/safe e-posta."""
    rows = []
    try:
        d = load_dataset("zefang-liu/phishing-email-dataset", split="train")
        for item in d:
            body = str(item.get("Email Text", "")).strip()
            raw_label = str(item.get("Email Type", "")).strip().lower()
            lbl = _norm_label(raw_label)
            if body and lbl is not None and len(body) >= 20:
                rows.append({"body": body, "label": lbl})
    except Exception as exc:
        print(f"  {'zefang-liu/phishing-email-dataset':<40}: hata — {exc}")
    return _to_df(rows, "zefang-liu/phishing-email-dataset")


def load_translated_turkish() -> pd.DataFrame:
    """
    İngilizce phishing/normal e-postalarını Helsinki-NLP/opus-mt-en-tr ile Türkçe'ye çevirir.
    İlk çalıştırmada model indirilir (~300 MB) ve sonuç data/turkish_translated.csv'ye cache'lenir.
    """
    cache_path = Path(__file__).resolve().parents[1] / "data" / "turkish_translated.csv"

    if cache_path.exists() and cache_path.stat().st_size > 10_000:
        df = pd.read_csv(cache_path)
        df = df[df["body"].str.len() >= 20].dropna(subset=["body", "label"])
        return _to_df(df[["body", "label"]].to_dict("records"), "Türkçe çeviri (cache)")

    try:
        from transformers import MarianMTModel, MarianTokenizer
        import torch
    except ImportError:
        print(f"  {'Türkçe çeviri':<40}: 'transformers' kurulu değil, atlanıyor.")
        return pd.DataFrame(columns=["body", "label"])

    model_candidates = [
        "Helsinki-NLP/opus-mt-tc-big-en-tr",
        "Helsinki-NLP/opus-mt-en-tr",
    ]
    tokenizer, model = None, None
    for model_id in model_candidates:
        try:
            print(f"  {'Türkçe çeviri':<40}: {model_id} indiriliyor...")
            tokenizer = MarianTokenizer.from_pretrained(model_id)
            model     = MarianMTModel.from_pretrained(model_id)
            break
        except Exception:
            continue
    if model is None:
        print(f"  {'Türkçe çeviri':<40}: hiçbir çeviri modeli yüklenemedi, atlanıyor.")
        return pd.DataFrame(columns=["body", "label"])

    model.eval()

    def translate_batch(texts: list[str]) -> list[str]:
        inputs = tokenizer(texts, return_tensors="pt", padding=True,
                           truncation=True, max_length=256)
        with torch.no_grad():
            out = model.generate(**inputs)
        return [tokenizer.decode(t, skip_special_tokens=True) for t in out]

    # Kaynak: SetFit/enron_spam (çalıştığı bilinen dataset)
    try:
        src = load_dataset("SetFit/enron_spam", split="train")
    except Exception as exc:
        print(f"  {'Türkçe çeviri':<40}: kaynak dataset yüklenemedi — {exc}")
        return pd.DataFrame(columns=["body", "label"])

    sample_row = src[0]
    body_key  = next((k for k in ("text", "message", "body", "email") if k in sample_row), None)
    label_key = next((k for k in ("label", "spam", "type")            if k in sample_row), None)
    if not body_key or not label_key:
        print(f"  {'Türkçe çeviri':<40}: kolon bulunamadı.")
        return pd.DataFrame(columns=["body", "label"])

    phishing = [(str(r[body_key])[:300], 1) for r in src
                if _norm_label(r[label_key]) == 1 and len(str(r[body_key]).strip()) >= 30][:1500]
    normal   = [(str(r[body_key])[:300], 0) for r in src
                if _norm_label(r[label_key]) == 0 and len(str(r[body_key]).strip()) >= 30][:1500]
    all_samples = phishing + normal
    print(f"  {'Türkçe çeviri':<40}: {len(all_samples)} e-posta çevriliyor...")

    rows, batch_size = [], 8
    for i in range(0, len(all_samples), batch_size):
        batch  = all_samples[i : i + batch_size]
        texts  = [t for t, _ in batch]
        labels = [l for _, l in batch]
        try:
            translated = translate_batch(texts)
            for body, lbl in zip(translated, labels):
                if len(body.strip()) >= 20:
                    rows.append({"body": body.strip(), "label": lbl})
        except Exception:
            continue

    if not rows:
        return pd.DataFrame(columns=["body", "label"])

    df = pd.DataFrame(rows)
    df.to_csv(cache_path, index=False, encoding="utf-8")
    return _to_df(rows, "Helsinki-NLP EN→TR (Türkçe çeviri)")


# ── Ana akış ──────────────────────────────────────────────────────────────────

LOADERS = [
    load_enron_spam,
    load_sms_spam,
    load_deysi_spam,
    load_kaggle_phishing_zip,
    load_zefang_phishing,
    load_ealvaradob,
    load_knowledgator,
    load_prasanth,
    load_trainingdatapro,
    load_fathyshalab,
    load_shahidul,
    load_cybersectony,
    load_talby_enron,
    load_jacecarter,
    load_gchhablani,
    load_chizhikchi,
    load_turkish_email_spam,
    # load_translated_turkish,  # CPU'da çok yavaş; GPU varsa aktif edin
]


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    clean_path   = project_root / "data" / "emails_clean.csv"

    print("📥 Gerçek datasetler yükleniyor...\n")
    frames = []
    for loader in LOADERS:
        try:
            df = loader()
            if len(df) > 0:
                frames.append(df[["body", "label"]])
        except Exception as exc:
            print(f"  HATA [{loader.__name__}]: {exc}")

    if not frames:
        print("❌ Hiçbir dataset yüklenemedi.")
        return

    combined = pd.concat(frames, ignore_index=True)
    combined["body"]  = combined["body"].astype(str).str.strip()
    combined["label"] = pd.to_numeric(combined["label"], errors="coerce")
    combined = combined[combined["label"].isin([0, 1])]
    combined["label"] = combined["label"].astype(int)
    combined = combined[(combined["body"] != "") & (combined["body"].str.len() >= 20)]

    before = len(combined)
    combined = combined.drop_duplicates(subset=["body"]).reset_index(drop=True)

    combined.to_csv(clean_path, index=False, encoding="utf-8")

    ph = int((combined.label == 1).sum())
    nm = int((combined.label == 0).sum())
    print(f"\n{'─'*52}")
    print(f"  {before - len(combined):,} tekrar eden satır kaldırıldı")
    print(f"{'─'*52}")
    print(f"✅ emails_clean.csv → {clean_path}")
    print(f"   Toplam  : {len(combined):,}")
    print(f"   Normal  : {nm:,}  (%{nm/len(combined)*100:.1f})")
    print(f"   Phishing: {ph:,}  (%{ph/len(combined)*100:.1f})")
    print(f"{'─'*52}")
    print("Sonraki adım:")
    print("   python src/train_model.py")


if __name__ == "__main__":
    main()
