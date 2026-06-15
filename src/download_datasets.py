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

import os
import sys
import time
import zipfile
import io
import subprocess
import tempfile
import shutil
import tarfile
import urllib.request
import email as email_lib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from datasets import load_dataset


# ── HuggingFace token ile kimlik doğrulama ────────────────────────────────────

def _hf_login() -> bool:
    """HF_TOKEN varsa giriş yapar. Token'ı https://huggingface.co/settings/tokens adresinden al."""
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        print("⚠️  HF_TOKEN bulunamadı — rate-limit'li erişim (bazı datasetler atlanabilir)")
        print("   Token için: https://huggingface.co/settings/tokens")
        print("   Kullanım : set HF_TOKEN=hf_xxxx  (PowerShell'de)  ardından scripti çalıştır\n")
        return False
    try:
        import huggingface_hub
        huggingface_hub.login(token=token, add_to_git_credential=False)
        print("✅ HuggingFace oturumu açıldı — tüm datasetlere erişim aktif\n")
        return True
    except ImportError:
        print("⚠️  huggingface_hub kurulu değil: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"⚠️  HF login hatası: {e}")
        return False


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
    retries: int = 2,
) -> pd.DataFrame:
    """Genel HuggingFace yükleyicisi — farklı kolon isimlerini otomatik bulur."""
    rows = []
    for split in splits:
        for attempt in range(retries):
            try:
                d = load_dataset(repo_id, split=split)
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(3)
                    continue
                print(f"    ↳ HATA [{repo_id}/{split}]: {type(e).__name__}: {str(e)[:120]}")
                d = None
        if d is None:
            continue
        try:
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


def load_spamassassin() -> pd.DataFrame:
    """Apache SpamAssassin halka açık corpus (~6k e-posta, köklü benchmark)."""
    return _load_hf_generic(
        "maximedb/spamassassin",
        splits=("train", "test"),
        text_fields=("text", "body", "message"),
        label_fields=("label", "spam", "type"),
    )


def load_spam_email_clf() -> pd.DataFrame:
    """muriki/spam-email-classification — 5k spam/ham e-posta."""
    return _load_hf_generic(
        "muriki/spam-email-classification",
        splits=("train",),
        text_fields=("text", "body", "Email"),
        label_fields=("label", "spam", "Label"),
    )


def load_mshenoda_spam() -> pd.DataFrame:
    """mshenoda/email-spam — ~30k gerçek e-posta spam/ham."""
    return _load_hf_generic(
        "mshenoda/email-spam",
        splits=("train",),
        text_fields=("text", "body", "message", "email"),
        label_fields=("label", "spam", "type", "class"),
    )


def load_danish_tilak() -> pd.DataFrame:
    """danish-nlp/email-spam — çeşitli İngilizce spam e-postalar."""
    return _load_hf_generic(
        "danish-nlp/email-spam",
        splits=("train", "test"),
        text_fields=("text", "body", "message"),
        label_fields=("label", "spam"),
    )


def load_uciml_spam() -> pd.DataFrame:
    """uciml/sms-spam-collection — UCI SMS Spam Collection (5.5k)."""
    return _load_hf_generic(
        "uciml/sms-spam-collection",
        splits=("train",),
        text_fields=("sms", "text", "message", "body"),
        label_fields=("label", "spam", "type"),
    )


def load_fraud_emails() -> pd.DataFrame:
    """Deysi/fraud-emails — dolandırıcılık e-postaları."""
    return _load_hf_generic(
        "Deysi/fraud-emails",
        splits=("train",),
        text_fields=("text", "body", "message", "email"),
        label_fields=("label", "spam", "type"),
    )


def load_archive_zip() -> pd.DataFrame:
    """data/archive.zip — CEAS08, Enron, Nazario, Nigerian Fraud, SpamAssassin, phishing_email."""
    project_root = Path(__file__).resolve().parents[1]
    zip_path = project_root / "data" / "archive.zip"
    if not zip_path.exists():
        print(f"  {'archive.zip':<40}: bulunamadı, atlanıyor.")
        return pd.DataFrame(columns=["body", "label"])

    all_rows = []
    try:
        with zipfile.ZipFile(zip_path) as z:
            for name in z.namelist():
                if not name.endswith(".csv"):
                    continue
                try:
                    with z.open(name) as f:
                        df = pd.read_csv(f, encoding="utf-8", on_bad_lines="skip")
                        df.columns = [c.strip().lower() for c in df.columns]

                        body_col  = next((c for c in df.columns if c in
                                          ("body", "text", "text_combined", "message", "email", "content")), None)
                        label_col = next((c for c in df.columns if c in
                                          ("label", "labels", "spam", "type", "class")), None)

                        if body_col is None or label_col is None:
                            continue

                        df = df[[body_col, label_col]].rename(columns={body_col: "body", label_col: "label"})
                        df["body"]  = df["body"].astype(str).str.strip()
                        df["label"] = df["label"].apply(_norm_label)
                        df = df.dropna(subset=["label"])
                        df["label"] = df["label"].astype(int)
                        df = df[df["body"].str.len() >= 20]
                        all_rows.append(df)
                        ph = int((df.label == 1).sum())
                        nm = int((df.label == 0).sum())
                        print(f"  archive/{name:<35}: {len(df):>7,}  (phishing={ph:,}, normal={nm:,})")
                except Exception as e:
                    print(f"  archive/{name}: atlandı — {e}")
    except Exception as exc:
        print(f"  archive.zip: HATA — {exc}")
        return pd.DataFrame(columns=["body", "label"])

    if not all_rows:
        return pd.DataFrame(columns=["body", "label"])
    return pd.concat(all_rows, ignore_index=True)[["body", "label"]]


def load_archive2_zip() -> pd.DataFrame:
    """data/archive2.zip — Phishing_Email.csv (~18k phishing/safe e-posta)."""
    project_root = Path(__file__).resolve().parents[1]
    zip_path = project_root / "data" / "archive2.zip"
    if not zip_path.exists():
        print(f"  {'archive2.zip':<40}: bulunamadı, atlanıyor.")
        return pd.DataFrame(columns=["body", "label"])

    rows = []
    try:
        with zipfile.ZipFile(zip_path) as z:
            for name in z.namelist():
                if not name.endswith(".csv"):
                    continue
                with z.open(name) as f:
                    df = pd.read_csv(f, encoding="utf-8", on_bad_lines="skip")
                    # Kolonlar: 'Email Text', 'Email Type'
                    body_col  = next((c for c in df.columns if "text" in c.lower() or "body" in c.lower()), None)
                    label_col = next((c for c in df.columns if "type" in c.lower() or "label" in c.lower()
                                      or "spam" in c.lower()), None)
                    if body_col is None or label_col is None:
                        continue
                    for _, row in df.iterrows():
                        body = str(row[body_col]).strip()
                        lbl  = _norm_label(row[label_col])
                        if body and lbl is not None and len(body) >= 20:
                            rows.append({"body": body, "label": lbl})
    except Exception as exc:
        print(f"  archive2.zip: HATA — {exc}")

    return _to_df(rows, "archive2/Phishing_Email")


def load_ceas08() -> pd.DataFrame:
    """CEAS 2008 — Conference on Email Anti-Spam benchmark (~40k e-posta)."""
    return _load_hf_generic(
        "0x7194633/CEAS_08",
        splits=("train",),
        text_fields=("body", "text", "message", "email"),
        label_fields=("label", "spam", "type", "class"),
    )


def load_trec07_direct() -> pd.DataFrame:
    """TREC 2007 Spam Track Public Corpus — ~75k gerçek e-posta.
    Gordon Cormack, University of Waterloo. ~400MB indirme."""
    import ssl, gzip
    base    = "http://plg.uwaterloo.ca/~gvcormac/treccorpus07/"
    ctx     = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE

    # Etiketleri indir
    labels: dict = {}
    try:
        with urllib.request.urlopen(base + "trec07p.labels.gz", timeout=30, context=ctx) as resp:
            with gzip.open(resp) as gz:
                for line in gz:
                    parts = line.decode("utf-8", errors="ignore").strip().split()
                    if len(parts) == 2:
                        lbl_str, path = parts
                        labels[path] = 1 if lbl_str == "spam" else 0
        print(f"  TREC 2007: {len(labels):,} etiket yüklendi, e-posta korpusu indiriliyor (~400MB)...")
    except Exception as exc:
        print(f"  TREC 2007 labels: atlandı — {exc}")
        return pd.DataFrame(columns=["body", "label"])

    rows = []
    try:
        with urllib.request.urlopen(base + "trec07p.tgz", timeout=600, context=ctx) as resp:
            data = io.BytesIO(resp.read())
        with tarfile.open(fileobj=data, mode="r:gz") as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                label = labels.get(member.name)
                if label is None:
                    continue
                f = tar.extractfile(member)
                if f is None:
                    continue
                raw = f.read()
                try:
                    msg  = email_lib.message_from_bytes(raw)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode("utf-8", errors="ignore")
                                    break
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                    body = body.strip()
                    if len(body) >= 20:
                        rows.append({"body": body, "label": label})
                except Exception:
                    continue
    except Exception as exc:
        print(f"  TREC 2007 corpus: atlandı — {exc}")

    return _to_df(rows, "TREC 2007 (direct)")


def load_lingspam_direct() -> pd.DataFrame:
    """Ling-Spam dataset — AUEB, ~2.4k spam/ham e-posta (klasik akademik benchmark).
    Doğrudan tar.gz olarak indirilir, token gerektirmez."""
    import ssl
    url = "http://www.aueb.gr/users/ion/data/lingspam_public.tar.gz"
    rows = []
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, timeout=30, context=ctx) as resp:
            data = io.BytesIO(resp.read())
        with tarfile.open(fileobj=data, mode="r:gz") as tar:
            for member in tar.getmembers():
                if not member.isfile() or not member.name.endswith(".txt"):
                    continue
                f = tar.extractfile(member)
                if f is None:
                    continue
                body = f.read().decode("utf-8", errors="ignore").strip()
                if len(body) < 20:
                    continue
                # Dosya yoluna göre etiketle: spmsg = spam, diğerleri = ham
                label = 1 if "spmsg" in member.name.lower() else 0
                rows.append({"body": body, "label": label})
    except Exception as exc:
        print(f"  Ling-Spam (direct): atlandı — {exc}")
    return _to_df(rows, "Ling-Spam (direct)")


def load_spamassassin_direct() -> pd.DataFrame:
    """Apache SpamAssassin Public Corpus — tüm arşivler (~9k gerçek e-posta)."""
    import ssl
    base = "https://spamassassin.apache.org/old/publiccorpus/"
    files = [
        ("20021010_easy_ham.tar.bz2",   0),
        ("20021010_hard_ham.tar.bz2",   0),
        ("20030228_easy_ham.tar.bz2",   0),
        ("20030228_easy_ham_2.tar.bz2", 0),
        ("20030228_hard_ham.tar.bz2",   0),
        ("20021010_spam.tar.bz2",       1),
        ("20030228_spam.tar.bz2",       1),
        ("20030228_spam_2.tar.bz2",     1),
        ("20050311_spam_2.tar.bz2",     1),
    ]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    rows = []
    for filename, label in files:
        try:
            url = base + filename
            with urllib.request.urlopen(url, timeout=30, context=ctx) as resp:
                data = io.BytesIO(resp.read())
            with tarfile.open(fileobj=data, mode="r:bz2") as tar:
                for member in tar.getmembers():
                    if not member.isfile():
                        continue
                    f = tar.extractfile(member)
                    if f is None:
                        continue
                    raw = f.read()
                    try:
                        msg = email_lib.message_from_bytes(raw)
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        body = body.strip()
                        if len(body) >= 20:
                            rows.append({"body": body, "label": label})
                    except Exception:
                        continue
        except Exception as exc:
            print(f"  SpamAssassin ({filename}): atlandı — {exc}")
            continue
    return _to_df(rows, "SpamAssassin (direct)")


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


# ── Ana akış ──────────────────────────────────────────────────────────────────

LOADERS = [
    # ── Kaggle arşivleri (birincil kaynak — phishing odaklı) ─────────────────
    load_archive_zip,          # CEAS08(39k)+Enron(30k)+Nazario(1.5k)+Nigerian(3.3k)+phishing(82k)
    load_archive2_zip,         # Phishing_Email.csv (~18k)
    # ── Ek kaynaklar (spam + ham çeşitliliği için) ────────────────────────────
    load_enron_spam,           # 33k — Enron HuggingFace versiyonu
    load_deysi_spam,           # 8k  — Deysi spam
    load_kaggle_phishing_zip,  # 18k — dataphishing_dataset.zip (yerel)
    load_zefang_phishing,      # 18k — Zefang phishing
    load_spamassassin_direct,  # ~9k — Apache SpamAssassin
]


def _is_english(text: str) -> bool:
    """ASCII oranı >%90 ise İngilizce kabul et. Hızlı, bağımlılıksız filtre."""
    text = str(text)
    if len(text) < 20:
        return False
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / len(text)) > 0.90


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    clean_path   = project_root / "data" / "emails_clean.csv"

    _hf_login()
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

    # İngilizce filtresi — sentetik/Türkçe/Portekizce vb. çıkar
    before_lang = len(combined)
    combined = combined[combined["body"].apply(_is_english)].reset_index(drop=True)
    print(f"\n🌐 Dil filtresi: {before_lang:,} → {len(combined):,} (İngilizce e-posta kaldı)")

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
