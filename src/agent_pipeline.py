"""
Otomatik E-posta Analiz ve Önceliklendirme Pipeline'ı
Çalıştır: python src/agent_pipeline.py --input emails.csv --output rapor.json
          python src/agent_pipeline.py --input emails.csv --output rapor.csv
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.predict import predict_details_with_headers
from src.text_utils import build_email_text

# Risk seviyesi eşikleri
CRITICAL_THRESHOLD = 80
HIGH_THRESHOLD     = 60
MEDIUM_THRESHOLD   = 40


def risk_level(score: float) -> str:
    if score >= CRITICAL_THRESHOLD:
        return "KRİTİK"
    if score >= HIGH_THRESHOLD:
        return "YÜKSEK"
    if score >= MEDIUM_THRESHOLD:
        return "ORTA"
    return "DÜŞÜK"


def analyze_email(row: dict) -> dict:
    """Tek bir e-postayı analiz edip zenginleştirilmiş sonuç döndürür."""
    subject  = str(row.get("subject", ""))
    body     = str(row.get("body", ""))
    from_addr = str(row.get("from", row.get("sender", "")))
    reply_to = str(row.get("reply_to", ""))

    text   = build_email_text(subject, body)
    result = predict_details_with_headers(text, from_addr, reply_to, subject)

    score = result["risk_score"]
    return {
        "id":              row.get("id", ""),
        "subject":         subject[:80],
        "from":            from_addr,
        "karar":           result["label"],
        "risk_skoru":      round(score, 1),
        "risk_seviyesi":   risk_level(score),
        "guven":           round(result["confidence"], 1),
        "phishing_turu":   result.get("phishing_type", ""),
        "model_olasilik":  round(result["phishing_probability"], 1),
        "keyword_sayisi":  len(result["matched_keywords"]),
        "url_sayisi":      result["url_analysis"]["total_count"],
        "supheyli_url":    result["url_analysis"]["suspicious_count"],
        "anomali_skoru":   result.get("anomaly", {}).get("score", 0),
        "header_skoru":    result.get("header_analysis", {}).get("score", 0),
        "header_uyarilar": result.get("header_analysis", {}).get("flags", []),
        "aksiyonlar":      result.get("actions", []),
        "analiz_zamani":   datetime.now().isoformat(),
    }


def run_pipeline(
    input_path: str,
    output_path: str,
    min_risk: float = 0.0,
    only_phishing: bool = False,
) -> dict:
    """CSV dosyasındaki e-postaları toplu analiz eder, önceliklendirir ve kaydeder."""
    df = pd.read_csv(input_path)
    print(f"📦 {len(df):,} e-posta yüklendi: {input_path}")

    results = []
    for i, row in df.iterrows():
        try:
            result = analyze_email(row.to_dict())
            results.append(result)
            if (i + 1) % 50 == 0:
                print(f"   {i+1}/{len(df)} analiz edildi...")
        except Exception as e:
            print(f"   ⚠️ Satır {i} atlandı: {e}")

    # Risk skoruna göre sırala (yüksekten düşüğe)
    results.sort(key=lambda x: x["risk_skoru"], reverse=True)

    # Filtrele
    if only_phishing:
        results = [r for r in results if r["karar"] == "YES"]
    if min_risk > 0:
        results = [r for r in results if r["risk_skoru"] >= min_risk]

    # Özet istatistikler
    phishing_count  = sum(1 for r in results if r["karar"] == "YES")
    critical_count  = sum(1 for r in results if r["risk_seviyesi"] == "KRİTİK")
    high_count      = sum(1 for r in results if r["risk_seviyesi"] == "YÜKSEK")

    summary = {
        "toplam":          len(results),
        "phishing":        phishing_count,
        "guvenli":         len(results) - phishing_count,
        "kritik":          critical_count,
        "yuksek":          high_count,
        "analiz_zamani":   datetime.now().isoformat(),
    }

    print(f"\n📊 Özet:")
    print(f"   Toplam   : {summary['toplam']:,}")
    print(f"   Phishing : {summary['phishing']:,}")
    print(f"   Kritik   : {summary['kritik']:,}")
    print(f"   Yüksek   : {summary['yuksek']:,}")

    # Kaydet
    out = Path(output_path)
    if out.suffix == ".json":
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"ozet": summary, "sonuclar": results}, f, ensure_ascii=False, indent=2)
    else:
        pd.DataFrame(results).to_csv(out, index=False, encoding="utf-8-sig")

    print(f"✅ Rapor kaydedildi: {output_path}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Phishing e-posta analiz pipeline'ı")
    parser.add_argument("--input",         required=True,  help="Giriş CSV dosyası")
    parser.add_argument("--output",        required=True,  help="Çıkış dosyası (.json veya .csv)")
    parser.add_argument("--min-risk",      type=float, default=0.0, help="Minimum risk skoru filtresi (0-100)")
    parser.add_argument("--only-phishing", action="store_true",     help="Sadece phishing sonuçlarını göster")
    args = parser.parse_args()

    run_pipeline(args.input, args.output, args.min_risk, args.only_phishing)


if __name__ == "__main__":
    main()
