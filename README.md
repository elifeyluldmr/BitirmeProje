# Phishing Email Detection

Python ile phishing e-posta tespiti icin egitim, tahmin ve Streamlit dashboard projesi.

## Project Structure

- `data/`: Raw and processed datasets
- `src/`: Training and inference utilities
- `models/`: Saved model artifacts
- `app/`: API application code
- `reports/`: Evaluation outputs and reports

## Quick Start

1. Sanal ortam olustur ve aktif et.
2. Paketleri kur:
   ```bash
   pip install -r requirements.txt
   ```
3. Modeli egit:
   ```bash
   python src/train_model.py
   ```
4. Tahmin testini calistir:
   ```bash
   python src/predict.py
   ```
5. Dashboard'u calistir:
   ```bash
   streamlit run app/dashboard.py
   ```
6. API kullanmak istersen:
   ```bash
   uvicorn app.main:app --reload
   ```

## Dataset

- Aktif egitim verisi: `data/emails.csv`
- Bu dosya su an Kaggle'dan alinan phishing e-posta verisinin proje formatina donusturulmus halini kullanir.
- Beklenen kolonlar:
  - `subject`
  - `body`
  - `label`
- `label` degerleri:
  - `0` = normal email
  - `1` = phishing email

## One-Command Run (PowerShell)

From project root:

```powershell
./run.ps1
```

This script will:

1. Create `data/emails.csv` from the sample template if missing.
2. Train the model.
3. Start the FastAPI server.

## Current Model Flow

- Egitimde `subject` ve `body` birlestirilir.
- Ortak preprocessing mantigi `src/text_utils.py` icinde tutulur.
- TF-IDF vectorizer ve Logistic Regression modeli birlikte `models/phishing_model.pkl` dosyasina kaydedilir.
- Dashboard ve tahmin scripti ayni kaydedilmis model nesnesini kullanir.

## Reports

- Son egitim metrikleri: `reports/kaggle_train_metrics.txt`

## API Smoke Test (PowerShell)

After the API is running, open a second terminal in project root and run:

```powershell
./test_api.ps1
```

Optional custom URL:

```powershell
./test_api.ps1 -BaseUrl "http://127.0.0.1:8000"
```
