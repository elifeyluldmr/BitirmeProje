import re

try:
    from src.config import (
        HEADER_SCORE_DOMAIN_MISMATCH, HEADER_SCORE_IP_SENDER, HEADER_SCORE_FREE_MAIL_CORP,
        HEADER_SCORE_SUSPICIOUS_WORD, HEADER_SCORE_URGENCY_WORD, HEADER_SCORE_ALL_CAPS,
        HEADER_SCORE_EXCLAIM, HEADER_SCORE_MANY_DIGITS, HEADER_SUSPICIOUS_THRESHOLD,
        HEADER_MIN_CAPS_LEN, HEADER_EXCLAIM_MIN_COUNT, HEADER_DIGIT_MIN_COUNT,
    )
except ModuleNotFoundError:
    from config import (
        HEADER_SCORE_DOMAIN_MISMATCH, HEADER_SCORE_IP_SENDER, HEADER_SCORE_FREE_MAIL_CORP,
        HEADER_SCORE_SUSPICIOUS_WORD, HEADER_SCORE_URGENCY_WORD, HEADER_SCORE_ALL_CAPS,
        HEADER_SCORE_EXCLAIM, HEADER_SCORE_MANY_DIGITS, HEADER_SUSPICIOUS_THRESHOLD,
        HEADER_MIN_CAPS_LEN, HEADER_EXCLAIM_MIN_COUNT, HEADER_DIGIT_MIN_COUNT,
    )

# Konu satırında geçince insanı acele ettirmeye çalışan kelimeler
_URGENCY_WORDS = {
    "urgent", "action required", "verify now", "immediate",
    "acil", "hemen", "derhal", "kritik", "önemli", "son uyarı",
    "warning", "alert", "suspended", "locked", "blocked",
}

# Gönderici adresinde bu kelimeler varsa sahte "sistem bildirimi" gibi görünüyor
_SUSPICIOUS_SENDER_WORDS = {
    "security", "alert", "noreply", "support", "helpdesk",
    "güvenlik", "destek", "bildirim", "sistem", "admin",
    "update", "verify", "account", "billing",
}

# Gmail ve benzeri kişisel adresler, kurumsal banka gibi davranıyorsa şüpheli
_FREE_MAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "yandex.com", "protonmail.com", "icloud.com",
    "hotmail.com.tr", "yahoo.com.tr",
}

# Domain yerine IP kullananları yakalamak için
_IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _extract_domain(addr: str) -> str:
    # E-posta adresindeki @ işaretinden sonrasını domain olarak alıyoruz
    match = re.search(r"@([\w.\-]+)", addr)
    return match.group(1).lower() if match else ""


def analyze_headers(
    from_addr: str = "",
    reply_to: str  = "",
    subject: str   = "",
) -> dict:
    # Her şüpheli özellik için puan ekleyerek toplam başlık risk skorunu buluyoruz
    score = 0
    flags: list[str] = []

    from_domain  = _extract_domain(from_addr)
    reply_domain = _extract_domain(reply_to)

    # From ve Reply-To farklı domainse birisi sahte demek, bu çok güçlü bir sinyal
    if from_domain and reply_domain and from_domain != reply_domain:
        score += HEADER_SCORE_DOMAIN_MISMATCH
        flags.append(f"From ve Reply-To farklı domain: {from_domain} ↔ {reply_domain}")

    # Gönderici olarak domain yerine IP adresi yazmak çok nadir, genelde kötü niyet göstergesi
    if from_domain and _IP_PATTERN.match(from_domain):
        score += HEADER_SCORE_IP_SENDER
        flags.append("Gönderici IP adresi kullanıyor (domain yok)")

    # Gmail'den "Türkiye Bankası" gibi davranmak klasik phishing taktiği
    subject_lower = subject.lower()
    from_lower    = from_addr.lower()
    if from_domain in _FREE_MAIL_DOMAINS:
        corporate_keywords = [
            "bank", "banka", "microsoft", "apple", "google",
            "paypal", "amazon", "netflix", "government", "devlet",
        ]
        if any(kw in subject_lower or kw in from_lower for kw in corporate_keywords):
            score += HEADER_SCORE_FREE_MAIL_CORP
            flags.append(f"Ücretsiz mail ({from_domain}) kurumsal kimlik taklidi yapıyor")

    # Gönderici adreste "security@", "noreply@" gibi kelimeler olması kendini meşru göstermeye çalışma
    if from_addr:
        for kw in _SUSPICIOUS_SENDER_WORDS:
            if kw in from_lower:
                score += HEADER_SCORE_SUSPICIOUS_WORD
                flags.append(f"Gönderici adresinde şüpheli kelime: '{kw}'")
                break

    # Konu satırında aciliyet yaratmaya çalışıyorsa puan ekle
    if subject:
        for kw in _URGENCY_WORDS:
            if kw in subject_lower:
                score += HEADER_SCORE_URGENCY_WORD
                flags.append(f"Konu satırında aciliyet: '{kw}'")
                break

        # Tamamen büyük harf konu dikkat çekmek için kullanılan eski bir numara
        if subject.isupper() and len(subject) > HEADER_MIN_CAPS_LEN:
            score += HEADER_SCORE_ALL_CAPS
            flags.append("Konu satırı tamamen büyük harf")

        # Birden fazla ünlem işareti gereksiz bir aciliyet hissi yaratıyor
        if subject.count("!") > HEADER_EXCLAIM_MIN_COUNT:
            score += HEADER_SCORE_EXCLAIM
            flags.append("Konu satırında fazla '!' işareti")

        # Çok fazla rakam tracking kodu ya da sahte sipariş numarası taklidini anlatıyor
        if len(re.findall(r"\d", subject)) > HEADER_DIGIT_MIN_COUNT:
            score += HEADER_SCORE_MANY_DIGITS
            flags.append("Konu satırında çok fazla rakam")

    return {
        "score":         min(100, score),
        "flags":         flags,
        "is_suspicious": score >= HEADER_SUSPICIOUS_THRESHOLD,
        "from_domain":   from_domain,
        "reply_domain":  reply_domain,
    }
