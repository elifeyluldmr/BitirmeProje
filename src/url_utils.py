import re
from urllib.parse import urlparse

_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

_SUSPICIOUS_KEYWORDS = {
    "login", "verify", "secure", "account", "update", "confirm", "bank",
    "paypal", "signin", "password", "credential", "banking", "alert",
    "suspended", "urgent", "dogrula", "giris", "sifre", "hesap",
    "odul", "odeme", "nakit", "teslim", "kimlik", "borc", "haciz",
    "police", "guncelle", "sigorta",
}

_SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
    ".click", ".work", ".ru", ".cn", ".pw", ".info",
}

# Ücretsiz hosting servislerinin domain parçaları — phishing'de yaygın kullanılır
_FREE_HOSTING_PARTS = {
    "free-host", "freehost", "000webhostapp", "atspace", "byet",
    "infinityfree", "freehostia", "esy", "hol", "wixsite",
    "netlify", "pages.dev", "github.io",
}


def extract_urls(text: str) -> list[str]:
    """Metinden URL'leri çıkarır."""
    return _URL_PATTERN.findall(text)


def analyze_url(url: str) -> dict:
    """Tek bir URL'yi analiz edip şüpheli belirtileri tespit eder."""
    try:
        normalized = url if url.startswith("http") else "http://" + url
        parsed = urlparse(normalized)
        domain = parsed.netloc.lower().lstrip("www.")
        path_and_query = (parsed.path + "?" + parsed.query).lower()

        score = 0
        flags: list[str] = []

        if _IP_PATTERN.match(domain.split(":")[0]):
            score += 30
            flags.append("IP adresi domain olarak kullanılmış")

        for tld in _SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                score += 20
                flags.append(f"Şüpheli TLD: {tld}")
                break

        for kw in _SUSPICIOUS_KEYWORDS:
            if kw in domain:
                score += 15
                flags.append(f"Domain'de şüpheli kelime: '{kw}'")
                break

        if len(domain) > 50:
            score += 10
            flags.append("Çok uzun domain adı")

        if domain.count(".") > 3:
            score += 15
            flags.append("Aşırı subdomain sayısı")

        domain_parts = domain.split(".")
        for part in domain_parts:
            if part in _FREE_HOSTING_PARTS:
                score += 20
                flags.append(f"Ücretsiz hosting servisi: '{part}'")
                break

        # Kısa çizgili subdomain (odul-teslim, guvenli-hesap gibi)
        if domain.count(".") >= 1:
            subdomain = domain_parts[0]
            if "-" in subdomain and len(subdomain) > 5:
                score += 10
                flags.append(f"Kısa çizgili subdomain: '{subdomain}'")

        if "@" in url:
            score += 25
            flags.append("URL'de @ işareti (spoofing belirtisi)")

        if not url.lower().startswith("https"):
            score += 10
            flags.append("HTTPS kullanmıyor")

        for kw in _SUSPICIOUS_KEYWORDS:
            if kw in path_and_query:
                score += 10
                flags.append(f"URL path'inde şüpheli kelime: '{kw}'")
                break

        short_url = url[:80] + "..." if len(url) > 80 else url
        return {
            "url": short_url,
            "domain": domain,
            "score": min(100, score),
            "flags": flags,
            "is_suspicious": score >= 20,
        }
    except Exception:
        return {"url": url, "domain": "", "score": 0, "flags": [], "is_suspicious": False}


def analyze_urls_in_text(text: str) -> dict:
    """Metindeki tüm URL'leri analiz eder ve özet döndürür."""
    urls = extract_urls(text)
    if not urls:
        return {"urls": [], "max_score": 0, "suspicious_count": 0, "total_count": 0}

    analyses = [analyze_url(u) for u in urls[:10]]
    return {
        "urls": analyses,
        "max_score": max(a["score"] for a in analyses),
        "suspicious_count": sum(1 for a in analyses if a["is_suspicious"]),
        "total_count": len(analyses),
    }
