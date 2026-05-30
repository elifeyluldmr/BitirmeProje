"""
Transformer Model Eğitim Scripti — DistilBERT Multilingual
Çalıştır: python src/train_transformer.py
Gereksinimler: pip install transformers torch
GPU varsa otomatik kullanır, yoksa CPU ile çalışır (yavaş olur).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pickle
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, classification_report,
)

from src.text_utils import normalize_optional_text

MODEL_NAME   = "distilbert-base-multilingual-cased"
MAX_LEN      = 256
BATCH_SIZE   = 8       # 4GB VRAM için güvenli değer
EPOCHS       = 3
LR           = 2e-5
SAMPLE_SIZE  = 20_000  # Her sınıftan max örnek (toplam 40K)


class EmailDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], tokenizer: object) -> None:
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=MAX_LEN,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> dict:
        return {
            "input_ids":      self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels":         self.labels[idx],
        }


def evaluate(model: object, loader: DataLoader, device: object) -> tuple[list, list]:
    model.eval()
    all_preds: list[int] = []
    all_probs: list[float] = []
    with torch.no_grad():
        for batch in loader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            outputs        = model(input_ids=input_ids, attention_mask=attention_mask)
            probs          = torch.softmax(outputs.logits, dim=1)[:, 1].cpu().numpy()
            preds          = (probs >= 0.5).astype(int)
            all_preds.extend(preds.tolist())
            all_probs.extend(probs.tolist())
    return all_preds, all_probs


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    clean_path   = project_root / "data" / "emails_clean.csv"
    original_path = project_root / "data" / "emails.csv"
    data_path    = clean_path if clean_path.exists() else original_path

    model_dir    = project_root / "models" / "transformer"
    model_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Cihaz: {device}")

    df = pd.read_csv(data_path)
    print(f"📦 Toplam satır: {len(df):,}")

    df["text"] = df["body"].apply(normalize_optional_text)
    df = df[df["text"].str.strip() != ""].reset_index(drop=True)

    # Dengeli örneklem — eğitim süresini GPU VRAM'e uygun tutar
    phishing = df[df["label"] == 1].sample(min(SAMPLE_SIZE, (df["label"] == 1).sum()), random_state=42)
    normal   = df[df["label"] == 0].sample(min(SAMPLE_SIZE, (df["label"] == 0).sum()), random_state=42)
    df = pd.concat([phishing, normal]).sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"   Örneklem: {len(df):,} ({len(phishing):,} phishing + {len(normal):,} normal)")

    texts  = df["text"].tolist()
    labels = df["label"].astype(int).tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")

    print(f"⬇️  Tokenizer yükleniyor: {MODEL_NAME}")
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

    train_dataset = EmailDataset(X_train, y_train, tokenizer)
    test_dataset  = EmailDataset(X_test,  y_test,  tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE)

    print(f"⬇️  Model yükleniyor: {MODEL_NAME}")
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.to(device)

    optimizer    = AdamW(model.parameters(), lr=LR)
    total_steps  = len(train_loader) * EPOCHS
    scheduler    = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=total_steps // 10,
        num_training_steps=total_steps,
    )

    print(f"\n🚀 Eğitim başlıyor ({EPOCHS} epoch)...")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0.0
        for step, batch in enumerate(train_loader, 1):
            optimizer.zero_grad()
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels_batch   = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels_batch)
            loss    = outputs.loss
            total_loss += loss.item()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            if step % 50 == 0:
                print(f"   Epoch {epoch+1}/{EPOCHS} | Step {step}/{len(train_loader)} | Loss: {loss.item():.4f}")

        avg_loss = total_loss / len(train_loader)
        print(f"✅ Epoch {epoch+1} tamamlandı — Ortalama Loss: {avg_loss:.4f}")

    print("\n📊 Değerlendirme yapılıyor...")
    all_preds, all_probs = evaluate(model, test_loader, device)

    accuracy  = accuracy_score(y_test, all_preds)
    precision = precision_score(y_test, all_preds, zero_division=0)
    recall    = recall_score(y_test, all_preds, zero_division=0)
    f1        = f1_score(y_test, all_preds, zero_division=0)

    print("\n📊 Transformer Model Performansı:")
    print(f"   Accuracy : {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall   : {recall:.4f}")
    print(f"   F1 Score : {f1:.4f}")
    print(classification_report(y_test, all_preds, target_names=["Normal", "Phishing"]))

    model.save_pretrained(str(model_dir))
    tokenizer.save_pretrained(str(model_dir))
    print(f"✅ Model kaydedildi: {model_dir}")

    results_path = project_root / "models" / "transformer_test_results.pkl"
    with open(results_path, "wb") as f:
        pickle.dump({
            "y_test":    np.array(y_test),
            "y_pred":    np.array(all_preds),
            "y_prob":    np.array(all_probs),
            "accuracy":  accuracy,
            "precision": precision,
            "recall":    recall,
            "f1":        f1,
        }, f)
    print(f"✅ Test sonuçları kaydedildi: {results_path}")
    print("\n💡 Dashboard'da karşılaştırmayı görmek için: streamlit run app/dashboard.py")


if __name__ == "__main__":
    main()
