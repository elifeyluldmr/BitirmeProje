"""
Otomatik E-posta Analiz ve Önceliklendirme Pipeline'ı

CSV modunda:
  python src/agent_pipeline.py --input emails.csv --output rapor.json
  python src/agent_pipeline.py --input emails.csv --output rapor.csv --webhook https://hook.example.com/phishing

IMAP modunda (gerçek gelen kutusu):
  python src/agent_pipeline.py --imap-host imap.gmail.com --imap-user user@gmail.com --imap-pass "sifre" --output rapor.json
"""

import sys
import json
import argparse
import urllib.request
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
    subject   = str(row.get("subject", ""))
    body      = str(row.get("body", ""))
    from_addr = str(row.get("from", row.get("sender", "")))
    reply_to  = str(row.get("reply_to", ""))

    text   = build_email_text(subject, body)
    result = predict_details_with_headers(text, from_addr, reply_to, subject)

    score = result["risk_score"]
    bd    = result.get("score_breakdown", {})
    sigs  = bd.get("signals", {})

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
        "lr_olasilik":     round(result.get("lr_probability", result["phishing_probability"]), 1),
        "transformer_olasilik": bd.get("transformer_probability"),
        "keyword_sayisi":  len(result["matched_keywords"]),
        "url_sayisi":      result["url_analysis"]["total_count"],
        "supheyli_url":    result["url_analysis"]["suspicious_count"],
        "anomali_skoru":   result.get("anomaly", {}).get("score", 0),
        "header_skoru":    result.get("header_analysis", {}).get("score", 0),
        "header_uyarilar": result.get("header_analysis", {}).get("flags", []),
        # 5 katman katkıları
        "katman_model":    sigs.get("model",   {}).get("contribution", 0),
        "katman_keyword":  sigs.get("keyword", {}).get("contribution", 0),
        "katman_url":      sigs.get("url",     {}).get("contribution", 0),
        "katman_header":   sigs.get("header",  {}).get("contribution", 0),
        "katman_anomali":  sigs.get("anomaly", {}).get("contribution", 0),
        "aksiyonlar":      result.get("actions", []),
        "analiz_zamani":   datetime.now().isoformat(),
    }


def send_webhook(webhook_url: str, payload: dict) -> bool:
    """Analiz özetini JSON olarak belirtilen URL'ye POST eder.

    SIEM / SOAR / Slack / Teams webhook'larıyla uyumlu.
    """
    try:
        data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        req  = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            ok = resp.status < 300
        if ok:
            print(f"✅  Webhook gönderildi: {webhook_url}")
        else:
            print(f"⚠️  Webhook HTTP {resp.status}: {webhook_url}")
        return ok
    except Exception as exc:
        print(f"⚠️  Webhook gönderilemedi ({webhook_url}): {exc}")
        return False


def _save_results(results: list[dict], summary: dict, output_path: str) -> None:
    out = Path(output_path)
    if out.suffix == ".json":
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"ozet": summary, "sonuclar": results}, f, ensure_ascii=False, indent=2, default=str)
    else:
        pd.DataFrame(results).to_csv(out, index=False, encoding="utf-8-sig")
    print(f"✅  Rapor kaydedildi: {output_path}")


def _build_summary(results: list[dict]) -> dict:
    phishing_count = sum(1 for r in results if r["karar"] == "YES")
    return {
        "toplam":        len(results),
        "phishing":      phishing_count,
        "guvenli":       len(results) - phishing_count,
        "kritik":        sum(1 for r in results if r["risk_seviyesi"] == "KRİTİK"),
        "yuksek":        sum(1 for r in results if r["risk_seviyesi"] == "YÜKSEK"),
        "analiz_zamani": datetime.now().isoformat(),
    }


def _print_summary(summary: dict) -> None:
    print(f"\n📊 Özet:")
    print(f"   Toplam   : {summary['toplam']:,}")
    print(f"   Phishing : {summary['phishing']:,}")
    print(f"   Kritik   : {summary['kritik']:,}")
    print(f"   Yüksek   : {summary['yuksek']:,}")


def run_pipeline(
    input_path: str,
    output_path: str,
    min_risk: float = 0.0,
    only_phishing: bool = False,
    webhook_url: str | None = None,
) -> dict:
    """CSV dosyasındaki e-postaları toplu analiz eder, önceliklendirir ve kaydeder."""
    df = pd.read_csv(input_path)
    print(f"📦 {len(df):,} e-posta yüklendi: {input_path}")

    results = []
    for i, row in df.iterrows():
        try:
            results.append(analyze_email(row.to_dict()))
            if (i + 1) % 50 == 0:
                print(f"   {i+1}/{len(df)} analiz edildi...")
        except Exception as exc:
            print(f"   ⚠️  Satır {i} atlandı: {exc}")

    results.sort(key=lambda x: x["risk_skoru"], reverse=True)

    if only_phishing:
        results = [r for r in results if r["karar"] == "YES"]
    if min_risk > 0:
        results = [r for r in results if r["risk_skoru"] >= min_risk]

    summary = _build_summary(results)
    _print_summary(summary)
    _save_results(results, summary, output_path)

    if webhook_url:
        send_webhook(webhook_url, {"kaynak": "csv", "ozet": summary, "sonuclar": results[:100]})

    return summary


def run_imap_pipeline(
    host: str,
    port: int,
    user: str,
    password: str,
    folder: str,
    max_emails: int,
    output_path: str,
    min_risk: float = 0.0,
    only_phishing: bool = False,
    webhook_url: str | None = None,
    mark_seen: bool = False,
) -> dict:
    """IMAP gelen kutusundan e-posta çekip analiz eder."""
    from src.email_connector import connect, fetch_emails, mark_as_seen, disconnect

    print(f"🔌  {host}:{port} adresine bağlanılıyor ({user})...")
    conn = connect(host, port, user, password)
    print(f"📥  '{folder}' klasöründen en fazla {max_emails} e-posta çekiliyor...")
    emails = fetch_emails(conn, folder, max_emails, unseen_only=True)
    print(f"   {len(emails)} e-posta çekildi.")

    results = []
    for i, em in enumerate(emails):
        try:
            result = analyze_email(em)
            results.append(result)
            if mark_seen:
                mark_as_seen(conn, em["id"])
        except Exception as exc:
            print(f"   ⚠️  E-posta {em.get('id')} atlandı: {exc}")

    disconnect(conn)

    results.sort(key=lambda x: x["risk_skoru"], reverse=True)

    if only_phishing:
        results = [r for r in results if r["karar"] == "YES"]
    if min_risk > 0:
        results = [r for r in results if r["risk_skoru"] >= min_risk]

    summary = _build_summary(results)
    _print_summary(summary)
    _save_results(results, summary, output_path)

    if webhook_url:
        send_webhook(webhook_url, {"kaynak": "imap", "hesap": user, "ozet": summary, "sonuclar": results[:100]})

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Phishing e-posta analiz pipeline'ı")

    # CSV modu
    parser.add_argument("--input",         help="Giriş CSV dosyası (CSV modu)")
    parser.add_argument("--output",        required=True,      help="Çıkış dosyası (.json veya .csv)")
    parser.add_argument("--min-risk",      type=float, default=0.0,
                        help="Minimum risk skoru filtresi (0-100)")
    parser.add_argument("--only-phishing", action="store_true",
                        help="Sadece phishing sonuçlarını göster")
    parser.add_argument("--webhook",       help="Sonuçların gönderileceği webhook URL (SIEM/SOAR/Slack)")

    # IMAP modu
    parser.add_argument("--imap-host",    help="IMAP sunucu adresi (ör. imap.gmail.com)")
    parser.add_argument("--imap-port",    type=int, default=993,  help="IMAP port (varsayılan: 993)")
    parser.add_argument("--imap-user",    help="E-posta adresi")
    parser.add_argument("--imap-pass",    help="Şifre veya uygulama şifresi")
    parser.add_argument("--imap-folder",  default="INBOX",       help="IMAP klasörü")
    parser.add_argument("--imap-max",     type=int, default=50,   help="Maksimum e-posta sayısı")
    parser.add_argument("--mark-seen",    action="store_true",    help="Analiz sonrası okundu olarak işaretle")

    args = parser.parse_args()

    if args.imap_host:
        if not args.imap_user or not args.imap_pass:
            parser.error("IMAP modu için --imap-user ve --imap-pass gereklidir.")
        run_imap_pipeline(
            host=args.imap_host,
            port=args.imap_port,
            user=args.imap_user,
            password=args.imap_pass,
            folder=args.imap_folder,
            max_emails=args.imap_max,
            output_path=args.output,
            min_risk=args.min_risk,
            only_phishing=args.only_phishing,
            webhook_url=args.webhook,
            mark_seen=args.mark_seen,
        )
    else:
        if not args.input:
            parser.error("CSV modu için --input gereklidir.")
        run_pipeline(
            input_path=args.input,
            output_path=args.output,
            min_risk=args.min_risk,
            only_phishing=args.only_phishing,
            webhook_url=args.webhook,
        )


if __name__ == "__main__":
    main()
