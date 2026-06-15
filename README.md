# Phishing Email Detection

Python ile phishing (kimlik avı) e-posta tespiti için makine öğrenmesi ve transformer tabanlı hibrit tespit sistemi.

## Proje Yapısı

```
phishing-email-detection/
├── data/
│   ├── emails_clean.csv         # Aktif eğitim verisi (221k+ e-posta, 7 kaynak)
│   └── emails.sample.csv        # Örnek veri şablonu
├── src/
│   ├── config.py                # Tüm sabit değerler ve ağırlıklar (tek kaynak)
│   ├── prepare_dataset.py       # CSV temizleme ve birleştirme
│   ├── download_datasets.py     # HuggingFace + yerel zip'ten veri indirme
│   ├── train_model.py           # TF-IDF + Logistic Regression eğitimi
│   ├── train_transformer.py     # DistilBERT fine-tuning
│   ├── train_type_classifier.py # Phishing tür sınıflandırıcı (finansal, sahte kimlik vb.)
│   ├── predict.py               # 5 katmanlı hibrit risk skoru hesaplama
│   ├── transformer_predictor.py # DistilBERT inference modülü (lazy yükleme)
│   ├── anomaly_detector.py      # Anomali tespiti (Isolation Forest)
│   ├── explain_model.py         # Model açıklanabilirliği (SHAP / LIME)
│   ├── agent_pipeline.py        # Ajan tabanlı analiz pipeline
│   ├── text_utils.py            # Preprocessing ve anahtar kelime analizi
│   ├── url_utils.py             # URL risk analizi
│   ├── header_utils.py          # E-posta header analizi
│   ├── email_connector.py       # IMAP/SMTP bağlantısı
│   ├── report_generator.py      # HTML analiz raporu üretici
│   ├── analyze_dataset.py       # Dataset analiz araçları
│   └── generate_english_data.py # İngilizce sentetik veri üretimi
├── app/
│   ├── main.py                  # FastAPI REST API (3 endpoint)
│   └── dashboard.py             # Streamlit web dashboard
├── models/
│   ├── phishing_model.pkl       # TF-IDF + Logistic Regression modeli
│   ├── anomaly_model.pkl        # Anomali tespiti modeli
│   ├── test_results.pkl         # LR model test sonuçları
│   └── transformer/             # DistilBERT fine-tuned modeli (516 MB)
├── reports/
│   └── kaggle_train_metrics.txt # Son eğitim metrikleri
├── venv/                        # Aktif sanal ortam
├── requirements.txt
├── run.ps1                      # Tek komutla API + dashboard başlat
└── test_api.ps1                 # API smoke testi
```

## Hızlı Başlangıç

```powershell
# 1. Sanal ortam oluştur ve aktif et
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Paketleri kur
pip install -r requirements.txt

# 3. Datasetleri indir ve birleştir
python src/download_datasets.py

# 4. LR modelini eğit
python src/train_model.py

# 5. (Opsiyonel) Transformer modelini eğit — GPU önerilir, CPU'da 2-3 saat sürer
python src/train_transformer.py

# 6. Dashboard'u başlat (port 8501)
venv\Scripts\streamlit run app\dashboard.py --server.port 8501

# 7. API'yi başlat (port 8000)
venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Tek Komutla Çalıştır (PowerShell)

```powershell
./run.ps1
```

## Dataset

| Özellik | Değer |
|---|---|
| Aktif dosya | `data/emails_clean.csv` |
| Toplam e-posta | ~221,000 |
| Sınıf dağılımı | Normal %50.1 / Phishing %49.9 |
| Kolonlar | `body`, `label` |
| Dil | İngilizce (ASCII oranı >%90 filtresi) |

> **Not:** Türkçe dataset projede kullanılmıyor.

### Veri Kaynakları

`emails_clean.csv` aşağıdaki kaynaklardan derlendi ve birleştirildi:

- `SetFit/enron_spam` — HuggingFace Enron (~33k)
- `Deysi/spam-detection-dataset` — HuggingFace (~8k)
- `zefang-liu/phishing-email-dataset` — HuggingFace (~18k)
- `SpamAssassin` — Apache corpus (~9k)
- CEAS08, Enron, Nazario, Nigerian Fraud, Kaggle phishing arşivleri

Veri yeniden indirilmek istenirse: `python src/download_datasets.py`

## Modeller

### 1. TF-IDF + Logistic Regression (ana model)

| Parametre | Değer |
|---|---|
| Vektörleştirici | TF-IDF, ngram (1,2), max 30k özellik |
| Algoritma | Logistic Regression (liblinear) |
| Eğitim seti | ~177k e-posta |
| Accuracy | %97.94 |
| F1 Score | %97.94 |
| ROC AUC | 0.9993 |

### 2. DistilBERT Multilingual (transformer model)

| Parametre | Değer |
|---|---|
| Taban model | distilbert-base-multilingual-cased |
| Epoch | 3 |
| Eğitim seti | 40k e-posta (20k/sınıf) |
| Accuracy | %98.88 |
| F1 Score | %98.87 |
| Blend oranı | %60 Transformer + %40 LR |

### 5 Katmanlı Risk Skoru

```
Risk Skoru = w1·S_Model + w2·S_Keyword + w3·S_URL + w4·S_Header + w5·S_Anomaly

  w1 = 0.40  →  TF-IDF LR / DistilBERT blend
  w2 = 0.20  →  Anahtar kelime analizi
  w3 = 0.20  →  URL risk analizi
  w4 = 0.12  →  E-posta header analizi (opsiyonel)
  w5 = 0.08  →  Isolation Forest anomali tespiti (opsiyonel)

Eşik: 55 ve üzeri → PHISHİNG
```

Header veya anomali sağlanmadıysa ağırlıkları diğer sinyallere orantılı dağıtılır.

## API Endpoint'leri

| Method | Endpoint | Açıklama |
|---|---|---|
| GET | `/health` | Sağlık kontrolü |
| POST | `/predict` | Hızlı karar (YES/NO) |
| POST | `/predict/details` | Tam analiz — risk skoru, URL, anomali, header, aksiyonlar |
| POST | `/predict/batch` | Toplu analiz, risk skoruna göre sıralı (maks 500 e-posta) |

API dokümantasyonu: `http://127.0.0.1:8000/docs`

### Örnek İstek

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/details" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "text": "Urgent: Your account will be suspended. Click here to verify.",
    "subject": "Account Suspended",
    "from_addr": "noreply@secure-bank.tk",
    "reply_to": "attacker@gmail.com"
  }'
```

### API Smoke Test

```powershell
./test_api.ps1
# Özel URL ile:
./test_api.ps1 -BaseUrl "http://127.0.0.1:8000"
```

## Açıklanabilirlik

Dashboard'da her analiz için üç farklı açıklama yöntemi sunuluyor:

- **SHAP** — Modelin hangi kelimelere ne kadar ağırlık verdiğini gösterir
- **LIME** — Kelimeleri tek tek çıkararak kararın değişip değişmediğini ölçer
- **Transformer LIME** — DistilBERT üzerinde aynı black-box analizi (model eğitilmişse)
