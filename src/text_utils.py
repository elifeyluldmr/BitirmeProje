SUSPICIOUS_KEYWORDS = [
    # ── İngilizce phishing kelimeleri ────────────────────────
    "verify", "account", "login", "password", "urgent", "click",
    "suspended", "bank", "confirm", "security", "update", "access",
    "credential", "expire", "limited", "unauthorized", "alert",
    "immediately", "action", "required", "threat", "blocked",
    "locked", "prize", "winner", "claim", "free", "gift",
    "offer", "discount", "congratulations", "selected", "reward",
    "invoice", "payment", "overdue", "refund", "tax", "irs",
    "paypal", "amazon", "apple", "microsoft", "google", "netflix",
    "unusual", "suspicious", "compromised", "hacked", "breach",

    # ── Türkçe phishing kelimeleri ───────────────────────────
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
    "iade", "vergi", "kredi", "banka", "hesap", "transfer", "para",
    "odenmedi", "ödenmedi", "kapatilacak", "kapatılacak",

    # Kargo & Teslimat
    "kargo", "paket", "teslim", "teslimat", "adres", "guncelle",
    "güncelle", "teslim edilemedi",

    # Aciliyet
    "hemen", "derhal", "ivedilikle", "son", "süre", "saat",
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
        normalized_keyword = keyword.translate(TURKISH_CHAR_MAP)
        if normalized_keyword in clean_text and keyword not in matched_keywords:
            matched_keywords.append(keyword)

    return matched_keywords


def get_keyword_score(matched_keywords: list[str]) -> float:
    """Şüpheli kelime sayısına göre basit bir destek skoru hesaplar."""
    return min(100.0, len(matched_keywords) * 12.0)