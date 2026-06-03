"""
Anomali tespiti testleri — extract_features ve get_anomaly_score
Çalıştır: python -m pytest tests/test_anomaly.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.anomaly_detector import extract_features, get_anomaly_score


PHISHING_TEXT = (
    "URGENT!!! Your bank account has been suspended. "
    "Click http://secure-login.tk/verify to restore access IMMEDIATELY. "
    "Enter your PASSWORD and CREDIT CARD number now! http://fake-site.tk"
)
NORMAL_TEXT = (
    "Hi team, please find the meeting notes attached. "
    "The project deadline is next Friday. Let me know if you have questions."
)


# ── extract_features ──────────────────────────────────────────────────────────

def test_extract_features_returns_nine_values():
    features = extract_features(NORMAL_TEXT)
    assert len(features) == 9


def test_extract_features_all_numeric():
    features = extract_features(NORMAL_TEXT)
    for val in features:
        assert isinstance(val, (int, float)), f"Beklenen sayısal değer, gelen: {type(val)}"


def test_extract_features_url_count_detected():
    text = "Visit http://evil.tk and http://steal.tk for free prize!"
    features = extract_features(text)
    url_feature = features[1]
    assert url_feature >= 2


def test_extract_features_no_urls():
    features = extract_features("Simple message with no links at all.")
    assert features[1] == 0.0


def test_extract_features_exclamation_count():
    text = "Win now!!! Click here!!"
    features = extract_features(text)
    exclaim_feature = features[2]
    assert exclaim_feature >= 3


def test_extract_features_phishing_higher_keyword_count():
    normal_features  = extract_features(NORMAL_TEXT)
    phishing_features = extract_features(PHISHING_TEXT)
    assert phishing_features[7] >= normal_features[7]


def test_extract_features_empty_text():
    features = extract_features("")
    assert len(features) == 9
    for val in features:
        assert val >= 0


def test_extract_features_values_in_range():
    features = extract_features(PHISHING_TEXT)
    assert 0 <= features[3] <= 1     # caps_ratio
    assert 0 <= features[4] <= 1     # digit_ratio
    assert features[1] <= 10         # url_count üst sınır
    assert features[2] <= 10         # exclaim üst sınır


# ── get_anomaly_score ─────────────────────────────────────────────────────────

def test_get_anomaly_score_keys():
    result = get_anomaly_score(NORMAL_TEXT)
    assert "score" in result
    assert "is_anomaly" in result
    assert "available" in result


def test_get_anomaly_score_range():
    result = get_anomaly_score(PHISHING_TEXT)
    assert 0 <= result["score"] <= 100


def test_get_anomaly_score_returns_bool_flags():
    result = get_anomaly_score(NORMAL_TEXT)
    assert isinstance(result["is_anomaly"], bool)
    assert isinstance(result["available"], bool)
