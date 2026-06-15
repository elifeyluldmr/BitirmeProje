import re

# Sık kullanılan İngilizce stopword'ler, bunları metinden atıyoruz
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "this", "that", "these", "those", "it", "its", "i", "you",
    "he", "she", "we", "they", "my", "your", "his", "her", "our", "their",
    "from", "not", "no", "so", "if", "as", "by", "up", "out", "about",
    "than", "then", "there", "here", "when", "where", "who", "which", "what",
    "all", "each", "any", "some", "more", "also", "just", "can", "us",
}

# URL'leri tek bir token'a indirgiyoruz, model URL içeriğini değil varlığını öğrensin
_URL_PATTERN    = re.compile(r"https?://\S+|www\.\S+")
_NUMBER_PATTERN = re.compile(r"^\d+$")
_PUNCT_PATTERN  = re.compile(r"[^\w\s]")


def advanced_preprocessing(text: str) -> str:
    # Model eğitimi ve tahmin için kullanılan asıl temizleme fonksiyonu
    if not isinstance(text, str):
        return ""
    # Önce URL'leri temizle, ardından küçük harfe al
    text = _URL_PATTERN.sub(" urltoken ", text)
    text = text.lower().strip()
    text = _PUNCT_PATTERN.sub(" ", text)
    # Kısa tokenleri, sayıları ve stopword'leri at
    tokens = [
        t for t in text.split()
        if len(t) > 2 and t not in _STOPWORDS and not _NUMBER_PATTERN.match(t)
    ]
    return " ".join(tokens)


# Phishing e-postalarda sık geçen kelimeler, elle derlendi
SUSPICIOUS_KEYWORDS = [
    "verify", "account", "login", "password", "urgent", "click",
    "suspended", "confirm", "security", "update", "access",
    "credential", "expire", "limited", "unauthorized", "alert",
    "immediately", "action", "required", "threat", "blocked",
    "locked", "prize", "winner", "claim", "free", "gift",
    "offer", "discount", "congratulations", "selected", "reward",
    "invoice", "payment", "overdue", "refund", "tax",
    "paypal", "amazon", "apple", "microsoft", "google", "netflix",
    "unusual", "suspicious", "compromised", "hacked", "breach",
]


def normalize_optional_text(value: object) -> str:
    # None veya NaN gelen değerleri boş string'e çeviriyoruz
    if value is None:
        return ""
    value_text = str(value).strip()
    if value_text.lower() == "nan":
        return ""
    return value_text


def preprocessing(text: str) -> str:
    # Keyword eşleştirmesi için minimal temizlik, stopword ve kısa kelime filtrelemez.
    # ML eğitimi için advanced_preprocessing() kullanılmalı.
    return " ".join(str(text).lower().strip().split())


def build_email_text(subject: str, body: str) -> str:
    # Subject ve body'yi birleştirip tek bir metin oluşturuyoruz
    clean_subject = normalize_optional_text(subject)
    clean_body    = normalize_optional_text(body)
    return f"{clean_subject} {clean_body}".strip()


def find_suspicious_keywords(text: str) -> list[str]:
    # Metinde hangi şüpheli kelimelerin geçtiğini buluyoruz
    clean_text = preprocessing(text)
    matched_keywords: list[str] = []
    for keyword in SUSPICIOUS_KEYWORDS:
        # Tam kelime eşleşmesi istiyoruz, "click" için "clicking" eşleşmesin
        if re.search(rf"\b{re.escape(keyword)}\b", clean_text) and keyword not in matched_keywords:
            matched_keywords.append(keyword)
    return matched_keywords


def get_keyword_score(matched_keywords: list[str]) -> float:
    # Her eşleşen kelime 12 puan ekliyor, maksimum 100'de kalıyor
    return min(100.0, len(matched_keywords) * 12.0)
