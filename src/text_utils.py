import re

# ── advanced_preprocessing sabitleri ─────────────────────────────────────────
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "this", "that", "these", "those", "it", "its", "i", "you",
    "he", "she", "we", "they", "my", "your", "his", "her", "our", "their",
    "from", "not", "no", "so", "if", "as", "by", "up", "out", "about",
    "than", "then", "there", "here", "when", "where", "who", "which", "what",
    "all", "each", "any", "some", "more", "also", "just", "can", "us",
    "bir", "ve", "bu", "da", "de", "ile", "için", "mi", "mı", "mu", "mü",
    "ya", "ki", "ne", "ben", "sen", "biz", "siz", "o", "onlar", "benden",
    "senden", "bizden", "sizden", "ama", "fakat", "ancak", "çünkü", "eğer",
    "gibi", "kadar", "daha", "en", "çok", "az", "hiç", "her", "bazı",
    "şu", "şey", "olan", "olarak", "var", "yok",
}
_URL_PATTERN   = re.compile(r"https?://\S+|www\.\S+")
_NUMBER_PATTERN = re.compile(r"^\d+$")
_PUNCT_PATTERN  = re.compile(r"[^\w\s]")


def advanced_preprocessing(text: str) -> str:
    """URL'leri token'a çevirir, stopword'leri ve kısa token'ları atar."""
    if not isinstance(text, str):
        return ""
    text = _URL_PATTERN.sub(" urltoken ", text)
    text = text.lower().strip()
    text = _PUNCT_PATTERN.sub(" ", text)
    tokens = [
        t for t in text.split()
        if len(t) > 2 and t not in _STOPWORDS and not _NUMBER_PATTERN.match(t)
    ]
    return " ".join(tokens)


SUSPICIOUS_KEYWORDS = [
    # ── İngilizce phishing kelimeleri ---
    "verify", "account", "login", "password", "urgent", "click",
    "suspended",  "confirm", "security", "update", "access",
    "credential", "expire", "limited", "unauthorized", "alert",
    "immediately", "action", "required", "threat", "blocked",
    "locked", "prize", "winner", "claim", "free", "gift",
    "offer", "discount", "congratulations", "selected", "reward",
    "invoice", "payment", "overdue", "refund", "tax", 
    "paypal", "amazon", "apple", "microsoft", "google", "netflix",
    "unusual", "suspicious", "compromised", "hacked", "breach",

    # ---Türkçe phishing kelimeleri --- 
    # Hesap & Güvenlik
    "dogrula", "doğrula", "hesap", "giris", "giriş", "sifre", "şifre",
    "acil", "tikla", "tıkla", "askiya", "askıya", "banka", "onayla",
    "guvenlik", "güvenlik", "kimlik", "parola", "engellendi", "bloke",
    "kisitlandi", "kısıtlandı", "silindi", "kapatildi", "kapatıldı",
    "dogrulama", "doğrulama", "yetkisiz", "ihlal", "tehdit",

    # Ödül & Kazanma
    "kazandiniz", "kazandınız", "odulunuz", "ödülünüz", "tebrikler",
    "secildiniz", "seçildiniz", "hediye", "ucretsiz", "ücretsiz",
    "bedava", "cekilisi", "çekilişi", "kazanan", "talep", "ödül",

    # Ödeme & Finans
    "odeme", "ödeme", "fatura", "borc", "borç", "gecikti", "vadesi",
    "iade", "vergi", "kredi", "hesap", "transfer", "para",
    "odenmedi", "ödenmedi", "kapatilacak", "kapatılacak",

    # Kargo & Teslimat
    "kargo", "paket", "teslim", "teslimat", "adres", "guncelle",
    "güncelle", "teslim edilemedi",

    # Aciliyet
    "hemen", "derhal", "ivedilikle", "son", "süre", 
    "dakika", "bekliyor", "beklemede", "kritik", "önemli",

    # Bağlantı & Eylem
    "baglanti", "bağlantı", "link", "tiklayin", "tıklayın",
    "giriniz", "doldurun", "gonderin", "gönderin", "yukle", "yükle",
]

# Türkçe karakter normalizasyon haritası
TURKISH_CHAR_MAP = str.maketrans(
    {
        "ç": "c", "Ç": "c",
        "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i",
        "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s",
        "ü": "u", "Ü": "u",
    }
)


def normalize_optional_text(value: object) -> str:
    """Boş, None veya NaN gelen değerleri güvenli şekilde metne çevirir."""
    if value is None:
        return ""
    value_text = str(value).strip()
    if value_text.lower() == "nan":
        return ""
    return value_text


def preprocessing(text: str) -> str:
    """Metni basit şekilde temizler: küçük harfe çevirir ve boşlukları düzenler."""
    return " ".join(str(text).lower().strip().split())


def normalize_for_keyword_matching(text: str) -> str:
    """Türkçe karakterleri sadeleştirip kelime eşleşmesini daha dayanıklı hale getirir."""
    return preprocessing(text).translate(TURKISH_CHAR_MAP)


def build_email_text(subject: str, body: str) -> str:
    """Subject ve body alanlarını tek bir eğitim veya tahmin metni haline getirir."""
    clean_subject = normalize_optional_text(subject)
    clean_body = normalize_optional_text(body)
    return f"{clean_subject} {clean_body}".strip()


def find_suspicious_keywords(text: str) -> list[str]:
    """Metin içinde geçen şüpheli kelimeleri bulur."""
    clean_text = normalize_for_keyword_matching(text)
    matched_keywords: list[str] = []

    for keyword in SUSPICIOUS_KEYWORDS:
        normalized_keyword = re.escape(keyword.translate(TURKISH_CHAR_MAP))
        if re.search(rf"\b{normalized_keyword}\b", clean_text) and keyword not in matched_keywords:
            matched_keywords.append(keyword)

    return matched_keywords


def get_keyword_score(matched_keywords: list[str]) -> float:
    """Şüpheli kelime sayısına göre basit bir destek skoru hesaplar."""
    return min(100.0, len(matched_keywords) * 12.0)