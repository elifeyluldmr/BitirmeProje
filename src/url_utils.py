import re
from urllib.parse import urlparse

try:
    from src.config import (
        URL_SCORE_IP_DOMAIN, URL_SCORE_SUSPICIOUS_TLD, URL_SCORE_KEYWORD_DOMAIN,
        URL_SCORE_LONG_DOMAIN, URL_SCORE_EXCESS_SUBDOMAIN, URL_SCORE_FREE_HOSTING,
        URL_SCORE_HYPHEN_SUBDOMAIN, URL_SCORE_AT_SIGN, URL_SCORE_NO_HTTPS,
        URL_SCORE_KEYWORD_PATH, URL_SUSPICIOUS_THRESHOLD, URL_MAX_ANALYZE,
    )
except ModuleNotFoundError:
    from config import (
        URL_SCORE_IP_DOMAIN, URL_SCORE_SUSPICIOUS_TLD, URL_SCORE_KEYWORD_DOMAIN,
        URL_SCORE_LONG_DOMAIN, URL_SCORE_EXCESS_SUBDOMAIN, URL_SCORE_FREE_HOSTING,
        URL_SCORE_HYPHEN_SUBDOMAIN, URL_SCORE_AT_SIGN, URL_SCORE_NO_HTTPS,
        URL_SCORE_KEYWORD_PATH, URL_SUSPICIOUS_THRESHOLD, URL_MAX_ANALYZE,
    )

# URL'leri bulmak için kullanılan regex, http/https ve www ile başlayanları yakalar
_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_IP_PATTERN  = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

# Domain içinde geçtiğinde şüphe uyandıran kelimeler
_SUSPICIOUS_KEYWORDS = {
    "login", "verify", "secure", "account", "update", "confirm", "bank",
    "paypal", "signin", "password", "credential", "banking", "alert",
    "suspended", "urgent", "dogrula", "giris", "sifre", "hesap",
    "odul", "odeme", "nakit", "teslim", "kimlik", "borc", "haciz",
    "police", "guncelle", "sigorta",
}

# Phishing'de çok kullanılan ücretsiz ve kolay alınan uzantılar
_SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
    ".click", ".work", ".ru", ".cn", ".pw", ".info",
}

# Ücretsiz hosting domain parçaları, phishing siteleri burada barınıyor
_FREE_HOSTING_PARTS = {
    "free-host", "freehost", "000webhostapp", "atspace", "byet",
    "infinityfree", "freehostia", "esy", "hol", "wixsite",
    "netlify", "pages.dev", "github.io",
}


def extract_urls(text: str) -> list[str]:
    # Metindeki tüm URL'leri çıkarıp liste olarak dönüyoruz
    return _URL_PATTERN.findall(text)


def analyze_url(url: str) -> dict:
    # Her şüpheli özellik için puan ekliyoruz, sonunda toplam risk skoru çıkıyor
    try:
        normalized     = url if url.startswith("http") else "http://" + url
        parsed         = urlparse(normalized)
        domain         = parsed.netloc.lower().lstrip("www.")
        path_and_query = (parsed.path + "?" + parsed.query).lower()

        score = 0
        flags: list[str] = []

        # Domain yerine direkt IP kullananlar genelde sahte site
        if _IP_PATTERN.match(domain.split(":")[0]):
            score += URL_SCORE_IP_DOMAIN
            flags.append("IP adresi domain olarak kullanılmış")

        # Ücretsiz ve kötüye kullanılan TLD'ler
        for tld in _SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                score += URL_SCORE_SUSPICIOUS_TLD
                flags.append(f"Şüpheli TLD: {tld}")
                break

        # Domain adının içinde "login", "bank" gibi kelimeler var mı
        for kw in _SUSPICIOUS_KEYWORDS:
            if kw in domain:
                score += URL_SCORE_KEYWORD_DOMAIN
                flags.append(f"Domain'de şüpheli kelime: '{kw}'")
                break

        # 50 karakterden uzun domainler genelde kullanıcıyı şaşırtmak için yapılmış
        if len(domain) > 50:
            score += URL_SCORE_LONG_DOMAIN
            flags.append("Çok uzun domain adı")

        # 3'ten fazla nokta varsa çok fazla subdomain var demek
        if domain.count(".") > 3:
            score += URL_SCORE_EXCESS_SUBDOMAIN
            flags.append("Aşırı subdomain sayısı")

        domain_parts = domain.split(".")
        for part in domain_parts:
            if part in _FREE_HOSTING_PARTS:
                score += URL_SCORE_FREE_HOSTING
                flags.append(f"Ücretsiz hosting servisi: '{part}'")
                break

        # "odul-teslim.site" gibi tireli subdomainler sahte sitelerde yaygın
        if domain.count(".") >= 1:
            subdomain = domain_parts[0]
            if "-" in subdomain and len(subdomain) > 5:
                score += URL_SCORE_HYPHEN_SUBDOMAIN
                flags.append(f"Kısa çizgili subdomain: '{subdomain}'")

        # URL'de @ işareti kullanıcıyı yanıltmak için kullanılıyor
        if "@" in url:
            score += URL_SCORE_AT_SIGN
            flags.append("URL'de @ işareti (spoofing belirtisi)")

        # HTTPS yoksa bağlantı şifrelenmemiş demek
        if not url.lower().startswith("https"):
            score += URL_SCORE_NO_HTTPS
            flags.append("HTTPS kullanmıyor")

        # Sayfa yolunda da şüpheli kelime olabilir
        for kw in _SUSPICIOUS_KEYWORDS:
            if kw in path_and_query:
                score += URL_SCORE_KEYWORD_PATH
                flags.append(f"URL path'inde şüpheli kelime: '{kw}'")
                break

        # Çok uzun URL'leri kısaltıyoruz, okunabilirlik için
        short_url = url[:80] + "..." if len(url) > 80 else url
        return {
            "url":          short_url,
            "domain":       domain,
            "score":        min(100, score),
            "flags":        flags,
            "is_suspicious": score >= URL_SUSPICIOUS_THRESHOLD,
        }
    except Exception:
        # URL parse edilemezse boş sonuç dön, hata fırlatma
        return {"url": url, "domain": "", "score": 0, "flags": [], "is_suspicious": False}


def analyze_urls_in_text(text: str) -> dict:
    # Metinden URL'leri çıkar ve hepsini analiz et
    urls = extract_urls(text)
    if not urls:
        return {"urls": [], "max_score": 0, "suspicious_count": 0, "total_count": 0}

    # Çok fazla URL varsa ilk 10 tanesiyle yetiniyoruz
    analyses = [analyze_url(u) for u in urls[:URL_MAX_ANALYZE]]
    return {
        "urls":             analyses,
        "max_score":        max(a["score"] for a in analyses),
        "suspicious_count": sum(1 for a in analyses if a["is_suspicious"]),
        "total_count":      len(analyses),
    }
