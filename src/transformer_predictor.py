from __future__ import annotations

from pathlib import Path

# Model bir kez yüklendikten sonra burada tutuyoruz, her tahmin için tekrar yüklememek için
_cache: dict = {}


def _model_dir() -> Path:
    # models/transformer klasörünün tam yolu
    return Path(__file__).resolve().parents[1] / "models" / "transformer"


def is_available() -> bool:
    # config.json varsa model eğitilmiş ve kullanıma hazır demek
    return (_model_dir() / "config.json").exists()


def _load() -> tuple | None:
    # Daha önce yüklendiyse cache'den dön, tekrar diskten okumaya gerek yok
    if "model" in _cache:
        return _cache["model"], _cache["tokenizer"], _cache["device"]

    # Model klasörü yoksa sessizce None dön, hata fırlatma
    if not is_available():
        return None

    try:
        import torch
        from transformers import (
            DistilBertTokenizerFast,
            DistilBertForSequenceClassification,
        )

        d = str(_model_dir())

        # Tokenizer ve modeli diskten yükle
        tokenizer = DistilBertTokenizerFast.from_pretrained(d)
        model = DistilBertForSequenceClassification.from_pretrained(d)

        # GPU varsa kullan, yoksa CPU'da çalışır
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        # Tahmin modunda çalıştır, gradient hesaplamaya gerek yok
        model.eval()

        # Bir dahaki çağrı için cache'e al
        _cache["model"] = model
        _cache["tokenizer"] = tokenizer
        _cache["device"] = device
        return model, tokenizer, device
    except Exception:
        # Yükleme başarısız olursa None dön, uygulama çökmeden devam etsin
        return None


def predict(text: str) -> float | None:
    # Model yoksa None dön, üst katman bunu kontrol ediyor
    loaded = _load()
    if loaded is None:
        return None

    model, tokenizer, device = loaded
    try:
        import torch

        # Metni token'lara çevir, 256 tokenden uzun kısımları kes
        enc = tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt",
        )

        # Tensörleri doğru cihaza taşı
        ids = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)

        # Gradient hesaplamadan çalıştır, bellek ve zaman tasarrufu sağlıyor
        with torch.no_grad():
            logits = model(input_ids=ids, attention_mask=mask).logits
            # Softmax ile olasılığa çevir, index 1 phishing sınıfı
            prob = torch.softmax(logits, dim=1)[0, 1].item()

        # 0-100 aralığına çevirerek döndür
        return float(prob * 100)
    except Exception:
        return None
