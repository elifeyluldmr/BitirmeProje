"""
FastAPI endpoint testleri — TestClient ile HTTP katmanı doğrulaması
Çalıştır: python -m pytest tests/test_api.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

PHISHING_TEXT = (
    "URGENT: Your bank account has been suspended. "
    "Click http://secure-login.tk/verify to restore access immediately. "
    "Enter your password and credit card number now."
)
NORMAL_TEXT = (
    "Hi team, please find the meeting notes attached. "
    "The project deadline is next Friday. Let me know if you have questions."
)


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── /predict ──────────────────────────────────────────────────────────────────

def test_predict_phishing_returns_yes():
    r = client.post("/predict", json={"text": PHISHING_TEXT})
    assert r.status_code == 200
    assert r.json()["label"] == "YES"


def test_predict_normal_returns_no():
    r = client.post("/predict", json={"text": NORMAL_TEXT})
    assert r.status_code == 200
    assert r.json()["label"] == "NO"


def test_predict_label_is_yes_or_no():
    r = client.post("/predict", json={"text": PHISHING_TEXT})
    assert r.json()["label"] in ("YES", "NO")


# ── /predict/details ──────────────────────────────────────────────────────────

def test_predict_details_required_keys():
    r = client.post("/predict/details", json={"text": PHISHING_TEXT})
    assert r.status_code == 200
    data = r.json()
    for key in ("label", "risk_score", "confidence", "phishing_probability",
                "keyword_score", "url_analysis", "actions"):
        assert key in data, f"Eksik alan: {key}"


def test_predict_details_risk_score_range():
    r = client.post("/predict/details", json={"text": PHISHING_TEXT})
    score = r.json()["risk_score"]
    assert 0 <= score <= 100


def test_predict_details_with_headers():
    payload = {
        "text": PHISHING_TEXT,
        "from_addr": "support@paypal.com",
        "reply_to": "attacker@gmail.com",
        "subject": "Verify your account now",
    }
    r = client.post("/predict/details", json=payload)
    assert r.status_code == 200
    assert "header_analysis" in r.json()


def test_predict_details_phishing_higher_risk_than_normal():
    r_phish  = client.post("/predict/details", json={"text": PHISHING_TEXT}).json()
    r_normal = client.post("/predict/details", json={"text": NORMAL_TEXT}).json()
    assert r_phish["risk_score"] > r_normal["risk_score"]


# ── /predict/batch ────────────────────────────────────────────────────────────

def test_predict_batch_returns_correct_total():
    payload = {"emails": [PHISHING_TEXT, NORMAL_TEXT]}
    r = client.post("/predict/batch", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert data["phishing"] + data["safe"] == data["total"]


def test_predict_batch_sorted_by_risk():
    payload = {"emails": [NORMAL_TEXT, PHISHING_TEXT]}
    results = client.post("/predict/batch", json=payload).json()["results"]
    scores = [item["risk_score"] for item in results if "risk_score" in item]
    assert scores == sorted(scores, reverse=True)


def test_predict_batch_limit_exceeded():
    payload = {"emails": ["test"] * 501}
    r = client.post("/predict/batch", json=payload)
    assert r.status_code == 200
    assert "error" in r.json()
