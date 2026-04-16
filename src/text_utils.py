SUSPICIOUS_KEYWORDS = [
    "verify",
    "account",
    "login",
    "password",
    "urgent",
    "click",
    "suspended",
    "bank",
    "confirm",
    "security",
    "dogrula",
    "hesap",
    "giris",
    "sifre",
    "acil",
    "tikla",
    "askiya",
    "banka",
    "onayla",
    "guvenlik",
]

TURKISH_CHAR_MAP = str.maketrans(
    {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }
)


def normalize_optional_text(value: object) -> str:
    """Bos, None veya NaN gelen degerleri guvenli sekilde metne cevirir."""
    if value is None:
        return ""

    value_text = str(value).strip()
    if value_text.lower() == "nan":
        return ""

    return value_text


def preprocessing(text: str) -> str:
    """Metni basit bir sekilde temizler: kucuk harfe cevirir ve bosluklari duzenler."""
    return " ".join(str(text).lower().strip().split())


def normalize_for_keyword_matching(text: str) -> str:
    """Turkce karakterleri sadeleştirip kelime eşleşmesini daha dayanıklı hale getirir."""
    return preprocessing(text).translate(TURKISH_CHAR_MAP)


def build_email_text(subject: str, body: str) -> str:
    """Subject ve body alanlarini tek bir egitim veya tahmin metni haline getirir."""
    clean_subject = normalize_optional_text(subject)
    clean_body = normalize_optional_text(body)
    return f"{clean_subject} {clean_body}".strip()


def find_suspicious_keywords(text: str) -> list[str]:
    """Metin icinde gecen supheli kelimeleri bulur."""
    clean_text = normalize_for_keyword_matching(text)
    matched_keywords: list[str] = []

    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in clean_text and keyword not in matched_keywords:
            matched_keywords.append(keyword)

    return matched_keywords


def get_keyword_score(matched_keywords: list[str]) -> float:
    """Supheli kelime sayisina gore basit bir destek skoru hesaplar."""
    return min(100.0, len(matched_keywords) * 18.0)