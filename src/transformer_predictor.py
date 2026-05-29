"""
DistilBERT inference modülü — train_transformer.py ile eğitilmiş modeli kullanır.
models/transformer/config.json yoksa tüm fonksiyonlar sessizce None/False döndürür.
"""

from pathlib import Path

_cache: dict = {}


def _model_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "models" / "transformer"


def is_available() -> bool:
    """Transformer modeli eğitilmiş ve yüklenmeye hazırsa True döndürür."""
    return (_model_dir() / "config.json").exists()


def _load() -> tuple | None:
    """Model, tokenizer ve device'ı önbellekli yükler. Başarısızsa None döndürür."""
    if "model" in _cache:
        return _cache["model"], _cache["tokenizer"], _cache["device"]

    if not is_available():
        return None

    try:
        import torch
        from transformers import (
            DistilBertTokenizerFast,
            DistilBertForSequenceClassification,
        )

        d = str(_model_dir())
        tokenizer = DistilBertTokenizerFast.from_pretrained(d)
        model = DistilBertForSequenceClassification.from_pretrained(d)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()

        _cache["model"] = model
        _cache["tokenizer"] = tokenizer
        _cache["device"] = device
        return model, tokenizer, device
    except Exception:
        return None


def predict(text: str) -> float | None:
    """Metni DistilBERT ile değerlendirir.

    Dönüş: 0-100 arası phishing olasılığı.
    Transformer yüklü/eğitilmemişse None döndürür.
    """
    loaded = _load()
    if loaded is None:
        return None

    model, tokenizer, device = loaded
    try:
        import torch

        enc = tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt",
        )
        ids = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)

        with torch.no_grad():
            logits = model(input_ids=ids, attention_mask=mask).logits
            prob = torch.softmax(logits, dim=1)[0, 1].item()

        return float(prob * 100)
    except Exception:
        return None
