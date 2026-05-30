"""
Unit testler — predict pipeline, URL/header/keyword analizi
Çalıştır: python -m pytest tests/ -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.predict import predict_email, predict_details, classify_phishing_type
from src.url_utils import analyze_url, extract_urls
from src.header_utils import analyze_headers
from src.text_utils import get_keyword_score, find_suspicious_keywords


# ── predict_email ─────────────────────────────────────────────────────────────

PHISHING_TEXT = (
    "URGENT: Your bank account has been suspended. "
    "Click http://secure-login.tk/verify to restore access immediately. "
    "Enter your password and credit card number now."
)
NORMAL_TEXT = (
    "Hi team, please find the meeting notes attached. "
    "The project deadline is next Friday. Let me know if you have questions."
)


def test_predict_email_phishing():
    assert predict_email(PHISHING_TEXT) == "YES"


def test_predict_email_normal():
    assert predict_email(NORMAL_TEXT) == "NO"


def test_predict_email_returns_yes_or_no():
    result = predict_email(PHISHING_TEXT)
    assert result in ("YES", "NO")


# ── predict_details ───────────────────────────────────────────────────────────

def test_predict_details_keys():
    result = predict_details(PHISHING_TEXT)
    required_keys = {
        "label", "risk_score", "phishing_probability",
        "keyword_score", "url_analysis", "anomaly", "actions",
    }
    assert required_keys.issubset(result.keys())


def test_predict_details_risk_score_range():
    result = predict_details(PHISHING_TEXT)
    assert 0 <= result["risk_score"] <= 100


def test_predict_details_phishing_prob_range():
    result = predict_details(PHISHING_TEXT)
    assert 0 <= result["phishing_probability"] <= 100


def test_predict_details_phishing_higher_risk_than_normal():
    phishing_result = predict_details(PHISHING_TEXT)
    normal_result   = predict_details(NORMAL_TEXT)
    assert phishing_result["risk_score"] > normal_result["risk_score"]


# ── classify_phishing_type ────────────────────────────────────────────────────

def test_classify_financial_fraud():
    text = "Your bank account credit card payment is overdue. Send money transfer now."
    ptype = classify_phishing_type(text)
    assert isinstance(ptype, str)
    assert len(ptype) > 0


def test_classify_returns_string_for_normal():
    ptype = classify_phishing_type(NORMAL_TEXT)
    assert isinstance(ptype, str)


# ── URL analizi ───────────────────────────────────────────────────────────────

def test_extract_urls_finds_url():
    text = "Visit http://suspicious-bank.tk/login for details."
    urls = extract_urls(text)
    assert len(urls) >= 1
    assert any("suspicious-bank.tk" in u for u in urls)


def test_extract_urls_empty_text():
    assert extract_urls("No links here.") == []


def test_analyze_url_suspicious_tld():
    result = analyze_url("http://free-prize.tk/claim")
    assert result["score"] > 0
    assert result["is_suspicious"] is True


def test_analyze_url_no_https():
    result = analyze_url("http://example.com/page")
    assert result["score"] > 0


def test_analyze_url_ip_address():
    result = analyze_url("http://192.168.1.1/login")
    assert result["score"] >= 30


def test_analyze_url_safe():
    result = analyze_url("https://www.google.com/search?q=python")
    assert result["is_suspicious"] is False


# ── Header analizi ────────────────────────────────────────────────────────────

def test_header_mismatch_flagged():
    result = analyze_headers(
        from_addr="support@paypal.com",
        reply_to="attacker@gmail.com",
        subject="Verify your account",
    )
    assert result["score"] > 0
    assert result["is_suspicious"] is True


def test_header_no_mismatch():
    result = analyze_headers(
        from_addr="hr@company.com",
        reply_to="hr@company.com",
        subject="Monthly newsletter",
    )
    assert isinstance(result["score"], (int, float))


def test_header_urgent_subject():
    result = analyze_headers(
        from_addr="info@bank.com",
        reply_to="info@bank.com",
        subject="URGENT: Account suspended immediately!!!",
    )
    assert result["score"] > 0


# ── Keyword analizi ───────────────────────────────────────────────────────────

def test_keyword_score_phishing():
    keywords = find_suspicious_keywords(PHISHING_TEXT)
    score = get_keyword_score(keywords)
    assert score > 0


def test_keyword_score_normal():
    keywords = find_suspicious_keywords("Good morning. The weather is nice today. See you at lunch.")
    score = get_keyword_score(keywords)
    assert score == 0


def test_find_suspicious_keywords_returns_list():
    keywords = find_suspicious_keywords(PHISHING_TEXT)
    assert isinstance(keywords, list)
    assert len(keywords) > 0


def test_find_suspicious_keywords_empty():
    keywords = find_suspicious_keywords("Hello, how are you?")
    assert isinstance(keywords, list)
