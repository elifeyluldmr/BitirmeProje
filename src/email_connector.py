"""
IMAP e-posta bağlayıcısı — gerçek gelen kutusundan e-posta çekip ayrıştırır.

Kullanım (CLI):
  python src/email_connector.py --host imap.gmail.com --user ornek@gmail.com --pass "uygulama-sifresi" --output emails.csv

Gmail için "Uygulama Şifresi" gerekir (2FA aktifken normal şifre çalışmaz):
  Google Hesabım → Güvenlik → Uygulama Şifreleri
"""

import imaplib
import email as _email_lib
import argparse
import csv
import sys
from email.header import decode_header as _decode_header
from pathlib import Path


# ── Yardımcı ayrıştırıcılar ──────────────────────────────────────────────────

def _decode_str(raw) -> str:
    """MIME kodlu başlık değerini düz metin stringe çevirir."""
    if raw is None:
        return ""
    parts = _decode_header(str(raw))
    decoded = []
    for part, enc in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            decoded.append(str(part))
    return " ".join(decoded).strip()


def _extract_body(msg) -> str:
    """E-postadan düz metin gövdesini çıkarır; HTML varsa atlar."""
    body_parts: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and \
               "attachment" not in str(part.get("Content-Disposition", "")):
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body_parts.append(payload.decode(charset, errors="replace"))
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            body_parts.append(payload.decode(charset, errors="replace"))

    return "\n".join(body_parts).strip()


# ── Ana fonksiyonlar ──────────────────────────────────────────────────────────

def connect(
    host: str,
    port: int = 993,
    user: str = "",
    password: str = "",
    use_ssl: bool = True,
) -> imaplib.IMAP4:
    """IMAP sunucusuna bağlanır ve oturum açar.

    Raises:
        imaplib.IMAP4.error: Kimlik doğrulama veya bağlantı hatası.
    """
    if use_ssl:
        conn = imaplib.IMAP4_SSL(host, port)
    else:
        conn = imaplib.IMAP4(host, port)
    conn.login(user, password)
    return conn


def fetch_emails(
    conn: imaplib.IMAP4,
    folder: str = "INBOX",
    max_count: int = 50,
    unseen_only: bool = True,
) -> list[dict]:
    """Klasörden e-postaları çekip ayrıştırılmış dict listesi döndürür.

    Her dict şu anahtarları içerir:
        id, subject, body, from, reply_to, date, uid
    """
    conn.select(folder, readonly=True)
    criteria = "UNSEEN" if unseen_only else "ALL"
    status, data = conn.search(None, criteria)
    if status != "OK" or not data[0]:
        return []

    uid_list = data[0].split()
    uid_list = uid_list[-max_count:]  # En yeni max_count e-posta

    emails: list[dict] = []
    for uid in uid_list:
        try:
            status, msg_data = conn.fetch(uid, "(RFC822)")
            if status != "OK" or not msg_data or msg_data[0] is None:
                continue

            raw = msg_data[0][1]
            msg = _email_lib.message_from_bytes(raw)

            emails.append({
                "id":       uid.decode("ascii", errors="replace"),
                "subject":  _decode_str(msg.get("Subject")),
                "body":     _extract_body(msg),
                "from":     _decode_str(msg.get("From")),
                "reply_to": _decode_str(msg.get("Reply-To")),
                "date":     _decode_str(msg.get("Date")),
            })
        except Exception as exc:
            print(f"  ⚠️  UID {uid} atlandı: {exc}", file=sys.stderr)

    return emails


def mark_as_seen(conn: imaplib.IMAP4, uid: str) -> None:
    """Belirtilen e-postayı IMAP sunucusunda 'okundu' olarak işaretler."""
    conn.select("INBOX")
    conn.store(uid.encode(), "+FLAGS", "\\Seen")


def disconnect(conn: imaplib.IMAP4) -> None:
    """Bağlantıyı güvenli biçimde kapatır."""
    try:
        conn.close()
    except Exception:
        pass
    try:
        conn.logout()
    except Exception:
        pass


def save_to_csv(emails: list[dict], path: str) -> None:
    """E-posta listesini agent_pipeline ile uyumlu CSV formatında kaydeder."""
    if not emails:
        print("Kaydedilecek e-posta yok.")
        return
    out = Path(path)
    fieldnames = ["id", "subject", "body", "from", "reply_to", "date"]
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(emails)
    print(f"✅  {len(emails)} e-posta kaydedildi: {out}")


# ── CLI girişi ────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="IMAP gelen kutusundan e-posta çek ve CSV'ye aktar."
    )
    p.add_argument("--host",        required=True,              help="IMAP sunucu adresi (ör. imap.gmail.com)")
    p.add_argument("--port",        type=int, default=993,      help="IMAP port (varsayılan: 993 SSL)")
    p.add_argument("--user",        required=True,              help="E-posta adresi")
    p.add_argument("--pass",        dest="password",
                   required=True,                               help="Şifre veya uygulama şifresi")
    p.add_argument("--folder",      default="INBOX",            help="Klasör adı (varsayılan: INBOX)")
    p.add_argument("--max",         type=int, default=50,       help="Maksimum e-posta sayısı")
    p.add_argument("--all",         action="store_true",        help="Okunmamış yerine tüm e-postalar")
    p.add_argument("--output",      default="fetched_emails.csv",
                                                                help="Çıkış CSV dosyası")
    p.add_argument("--no-ssl",      action="store_true",        help="SSL kullanma (güvensiz)")
    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    print(f"🔌  {args.host}:{args.port} adresine bağlanılıyor ({args.user})...")
    try:
        conn = connect(args.host, args.port, args.user, args.password, use_ssl=not args.no_ssl)
    except imaplib.IMAP4.error as exc:
        print(f"❌  Bağlantı hatası: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"📥  '{args.folder}' klasöründen e-postalar çekiliyor...")
    emails = fetch_emails(conn, args.folder, args.max, unseen_only=not args.all)
    disconnect(conn)

    print(f"   {len(emails)} e-posta çekildi.")
    save_to_csv(emails, args.output)
    print(f"\n💡  Analiz için: python src/agent_pipeline.py --input {args.output} --output rapor.json")


if __name__ == "__main__":
    main()
