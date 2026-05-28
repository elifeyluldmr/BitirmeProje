"""
E-posta Başlık Analizi
From/Reply-To uyumsuzluğu, spoofing belirtileri ve konu satırı analizi.
"""

import re

_URGENCY_WORDS = {
    "urgent", "action required", "verify now", "immediate",
    "acil", "hemen", "derhal", "kritik", "önemli", "son uyarı",
    "warning", "alert", "suspended", "locked", "blocked",
}

_SUSPICIOUS_SENDER_WORDS = {
    "security", "alert", "noreply", "support", "helpdesk",
    "güvenlik", "destek", "bildirim", "sistem", "admin",
    "update", "verify", "account", "billing",
}

_FREE_MAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "yandex.com", "protonmail.com", "icloud.com",
    "hotmail.com.tr", "yahoo.com.tr",
}

_IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _extract_domain(addr: str) -> str:
    """E-posta adresinden ya da ham adresten domain çıkarır."""
    match = re.search(r"@([\w.\-]+)", addr)
    return match.group(1).lower() if match else ""


def analyze_headers(
    from_addr: str = "",
    reply_to: str  = "",
    subject: str   = "",
) -> dict:
    """E-posta başlıklarını analiz edip şüpheli işaret ve skor döndürür.

    Parametreler
    ────────────
    from_addr : Gönderici adresi   (ör. "noreply@bank-secure.tk")
    reply_to  : Reply-To adresi    (ör. "attacker@gmail.com")
    subject   : Konu satırı

    Döndürür
    ────────
    score        : 0-100, yüksekse şüpheli
    flags        : Bulunan uyarılar
    is_suspicious: score ≥ 20 ise True
    """
    score = 0
    flags: list[str] = []

    from_domain   = _extract_domain(from_addr)
    reply_domain  = _extract_domain(reply_to)

    # ── From/Reply-To domain uyumsuzluğu ─────────────────────────────────
    if from_domain and reply_domain and from_domain != reply_domain:
        score += 35
        flags.append(f"From ve Reply-To farklı domain: {from_domain} ↔ {reply_domain}")

    # ── Gönderici IP adresi ───────────────────────────────────────────────
    if from_domain and _IP_PATTERN.match(from_domain):
        score += 30
        flags.append("Gönderici IP adresi kullanıyor (domain yok)")

    # ── Ücretsiz mail domain'inden kurumsal görünüm ───────────────────────
    subject_lower = subject.lower()
    from_lower    = from_addr.lower()
    if from_domain in _FREE_MAIL_DOMAINS:
        # Kurumsal kelime iddiası varsa şüpheli
        corporate_keywords = ["bank", "banka", "microsoft", "apple", "google",
                              "paypal", "amazon", "netflix", "government", "devlet"]
        if any(kw in subject_lower or kw in from_lower for kw in corporate_keywords):
            score += 25
            flags.append(f"Ücretsiz mail ({from_domain}) kurumsal kimlik taklidi yapıyor")

    # ── Gönderici adresinde şüpheli kelime ───────────────────────────────
    if from_addr:
        for kw in _SUSPICIOUS_SENDER_WORDS:
            if kw in from_lower:
                score += 10
                flags.append(f"Gönderici adresinde şüpheli kelime: '{kw}'")
                break

    # ── Konu satırı — aciliyet kelimeleri ────────────────────────────────
    if subject:
        for kw in _URGENCY_WORDS:
            if kw in subject_lower:
                score += 15
                flags.append(f"Konu satırında aciliyet: '{kw}'")
                break

        if subject.isupper() and len(subject) > 5:
            score += 10
            flags.append("Konu satırı tamamen büyük harf")

        if subject.count("!") > 1:
            score += 10
            flags.append("Konu satırında fazla '!' işareti")

        if len(re.findall(r"\d", subject)) > 6:
            score += 5
            flags.append("Konu satırında çok fazla rakam")

    return {
        "score":        min(100, score),
        "flags":        flags,
        "is_suspicious": score >= 20,
        "from_domain":  from_domain,
        "reply_domain": reply_domain,
    }
