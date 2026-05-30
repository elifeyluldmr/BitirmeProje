"""
Entegrasyon testleri — pipeline uçtan uca çalışma doğrulaması
Çalıştır: python -m pytest tests/test_pipeline.py -v
"""
from __future__ import annotations

import sys
import json
import csv
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.predict import predict_email, predict_details
from src.agent_pipeline import analyze_email, run_pipeline, _build_summary
from src.report_generator import generate_single_report, generate_batch_report
from src.explain_model import get_shap_explanation, get_lime_explanation

# ── Sabit test metinleri ──────────────────────────────────────────────────────

PHISHING_EMAIL = (
    "URGENT: Your bank account has been suspended. "
    "Click http://secure-login-verify.tk/update to restore immediately. "
    "Enter your password and credit card number now."
)
NORMAL_EMAIL = (
    "Hi team, the quarterly report is attached. "
    "Please review and send your feedback by Friday. Thanks!"
)


# ── Uçtan uca pipeline testi ─────────────────────────────────────────────────

def test_pipeline_csv_to_json(tmp_path):
    """CSV girişinden JSON çıktısına tam pipeline akışı."""
    input_csv = tmp_path / "input.csv"
    output_json = tmp_path / "output.json"

    with open(input_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "subject", "body", "from", "reply_to"])
        writer.writeheader()
        writer.writerow({"id": "1", "subject": "Urgent!", "body": PHISHING_EMAIL, "from": "spammer@fake.tk", "reply_to": ""})
        writer.writerow({"id": "2", "subject": "Report", "body": NORMAL_EMAIL, "from": "hr@company.com", "reply_to": ""})

    summary = run_pipeline(str(input_csv), str(output_json))

    assert summary["toplam"] == 2
    assert "phishing" in summary
    assert "guvenli" in summary
    assert output_json.exists()

    with open(output_json, encoding="utf-8") as f:
        data = json.load(f)
    assert "ozet" in data
    assert "sonuclar" in data
    assert len(data["sonuclar"]) == 2


def test_pipeline_csv_to_csv(tmp_path):
    """CSV girişinden CSV çıktısına pipeline akışı."""
    input_csv = tmp_path / "input.csv"
    output_csv = tmp_path / "output.csv"

    with open(input_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "subject", "body", "from", "reply_to"])
        writer.writeheader()
        writer.writerow({"id": "1", "subject": "Win prize!", "body": PHISHING_EMAIL, "from": "", "reply_to": ""})

    run_pipeline(str(input_csv), str(output_csv))
    assert output_csv.exists()
    df_out = __import__("pandas").read_csv(output_csv)
    assert len(df_out) >= 1
    assert "karar" in df_out.columns
    assert "risk_skoru" in df_out.columns


def test_pipeline_only_phishing_filter(tmp_path):
    """--only-phishing filtresi sadece phishing sonuçları döndürür."""
    input_csv = tmp_path / "input.csv"
    output_json = tmp_path / "output.json"

    with open(input_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "subject", "body", "from", "reply_to"])
        writer.writeheader()
        writer.writerow({"id": "1", "subject": "Urgent", "body": PHISHING_EMAIL, "from": "", "reply_to": ""})
        writer.writerow({"id": "2", "subject": "Hi", "body": NORMAL_EMAIL, "from": "", "reply_to": ""})

    run_pipeline(str(input_csv), str(output_json), only_phishing=True)
    with open(output_json, encoding="utf-8") as f:
        data = json.load(f)
    for r in data["sonuclar"]:
        assert r["karar"] == "YES"


def test_pipeline_min_risk_filter(tmp_path):
    """--min-risk filtresi düşük riskli sonuçları eliyor."""
    input_csv = tmp_path / "input.csv"
    output_json = tmp_path / "output.json"

    with open(input_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "subject", "body", "from", "reply_to"])
        writer.writeheader()
        writer.writerow({"id": "1", "subject": "Hi", "body": NORMAL_EMAIL, "from": "", "reply_to": ""})

    run_pipeline(str(input_csv), str(output_json), min_risk=90.0)
    with open(output_json, encoding="utf-8") as f:
        data = json.load(f)
    for r in data["sonuclar"]:
        assert r["risk_skoru"] >= 90.0


# ── analyze_email testi ───────────────────────────────────────────────────────

def test_analyze_email_returns_all_fields():
    row = {"id": "test-1", "subject": "Urgent bank alert", "body": PHISHING_EMAIL, "from": "", "reply_to": ""}
    result = analyze_email(row)
    required = {"id", "karar", "risk_skoru", "risk_seviyesi", "guven", "phishing_turu",
                "model_olasilik", "keyword_sayisi", "url_sayisi", "supheyli_url",
                "anomali_skoru", "header_skoru", "aksiyonlar", "analiz_zamani"}
    assert required.issubset(result.keys())


def test_analyze_email_risk_score_range():
    row = {"id": "test-2", "subject": "Meeting", "body": NORMAL_EMAIL, "from": "", "reply_to": ""}
    result = analyze_email(row)
    assert 0 <= result["risk_skoru"] <= 100


def test_analyze_email_phishing_higher_than_normal():
    r_phish  = analyze_email({"id": "p", "subject": "Urgent!", "body": PHISHING_EMAIL, "from": "x@fake.tk", "reply_to": ""})
    r_normal = analyze_email({"id": "n", "subject": "Hi",      "body": NORMAL_EMAIL,   "from": "",           "reply_to": ""})
    assert r_phish["risk_skoru"] > r_normal["risk_skoru"]


def test_analyze_email_risk_levels():
    row = {"id": "rl", "subject": "Urgent!", "body": PHISHING_EMAIL, "from": "", "reply_to": ""}
    result = analyze_email(row)
    assert result["risk_seviyesi"] in ("DÜŞÜK", "ORTA", "YÜKSEK", "KRİTİK")


# ── _build_summary testi ──────────────────────────────────────────────────────

def test_build_summary_counts():
    results = [
        {"karar": "YES", "risk_seviyesi": "KRİTİK"},
        {"karar": "YES", "risk_seviyesi": "YÜKSEK"},
        {"karar": "NO",  "risk_seviyesi": "DÜŞÜK"},
    ]
    summary = _build_summary(results)
    assert summary["toplam"] == 3
    assert summary["phishing"] == 2
    assert summary["guvenli"] == 1
    assert summary["kritik"] == 1
    assert summary["yuksek"] == 1


# ── report_generator testi ────────────────────────────────────────────────────

def test_generate_single_report_returns_html():
    result = predict_details(PHISHING_EMAIL)
    html = generate_single_report(result, email_preview=PHISHING_EMAIL[:100])
    assert "<!DOCTYPE html>" in html
    assert "PHİSHİNG" in html or "GÜVENLİ" in html
    assert "Risk Skoru" in html


def test_generate_single_report_contains_metrics():
    result = predict_details(NORMAL_EMAIL)
    html = generate_single_report(result)
    assert "Güven Skoru" in html
    assert "Model Olasılığı" in html
    assert "Keyword Skoru" in html


def test_generate_batch_report_creates_file(tmp_path):
    results = [
        predict_details(PHISHING_EMAIL),
        predict_details(NORMAL_EMAIL),
    ]
    previews = [PHISHING_EMAIL[:60], NORMAL_EMAIL[:60]]
    out = str(tmp_path / "batch.html")
    generate_batch_report(results, out, previews)
    assert Path(out).exists()
    content = Path(out).read_text(encoding="utf-8")
    assert "Toplu Phishing" in content
    assert "Toplam E-posta" in content


# ── Model performans regresyon testi ─────────────────────────────────────────

def test_model_performance_regression():
    """F1 skoru %85 altına düşerse başarısız olur."""
    from sklearn.metrics import f1_score
    import pickle
    project_root = Path(__file__).resolve().parents[1]
    results_path = project_root / "models" / "test_results.pkl"

    if not results_path.exists():
        pytest.skip("test_results.pkl bulunamadı — önce train_model.py çalıştırın")

    with open(results_path, "rb") as f:
        r = pickle.load(f)

    f1 = f1_score(r["y_test"], r["y_pred"], zero_division=0)
    assert f1 >= 0.85, f"Model F1 skoru regresyon eşiğinin altında: {f1:.4f} < 0.85"


def test_transformer_performance_regression():
    """Transformer F1 skoru %85 altına düşerse başarısız olur."""
    from sklearn.metrics import f1_score
    import pickle
    project_root = Path(__file__).resolve().parents[1]
    results_path = project_root / "models" / "transformer_test_results.pkl"

    if not results_path.exists():
        pytest.skip("transformer_test_results.pkl bulunamadı — önce train_transformer.py çalıştırın")

    with open(results_path, "rb") as f:
        r = pickle.load(f)

    f1 = f1_score(r["y_test"], r["y_pred"], zero_division=0)
    assert f1 >= 0.85, f"Transformer F1 skoru regresyon eşiğinin altında: {f1:.4f} < 0.85"


# ── SHAP / LIME entegrasyon testleri ─────────────────────────────────────────

def test_shap_explanation_returns_list():
    from src.predict import load_model_objects
    model, vectorizer = load_model_objects()
    words = get_shap_explanation(PHISHING_EMAIL, model, vectorizer, top_n=5)
    assert isinstance(words, list)
    assert len(words) <= 5
    for word, score in words:
        assert isinstance(word, str)
        assert isinstance(score, float)


def test_lime_explanation_returns_list():
    from src.predict import load_model_objects
    model, vectorizer = load_model_objects()
    try:
        words = get_lime_explanation(PHISHING_EMAIL, model, vectorizer, top_n=5)
        assert isinstance(words, list)
    except ImportError:
        pytest.skip("LIME kurulu değil")
