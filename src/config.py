# Bütün sabit değerler burada toplanıyor, dağıtmak yerine tek yerden yönetmek daha kolay.

# 55 puan ve üzeri phishing sayılıyor
PHISHING_THRESHOLD = 55.0

# Her sinyalin risk skoruna katkı ağırlığı
# Header veya anomali yoksa o ağırlık sıfırlanıp diğerleri yeniden dağıtılıyor
W_MODEL   = 0.40
W_KEYWORD = 0.20
W_URL     = 0.20
W_HEADER  = 0.12
W_ANOMALY = 0.08

# Transformer ile TF-IDF LR'ı blend ederken kullanılan oranlar
TRANSFORMER_W = 0.60
LR_W          = 0.40

# Isolation Forest parametreleri, denemelerle bu değerlere karar verdik
ANOMALY_N_ESTIMATORS  = 200
ANOMALY_CONTAMINATION = 0.05
ANOMALY_RANDOM_STATE  = 42

# Ham skoru 0-100 aralığına çevirmek için offset ve ölçek faktörü
ANOMALY_SCORE_OFFSET = 0.3
ANOMALY_SCORE_SCALE  = 120

# URL risk puanları, her şüpheli özellik bu kadar puan ekliyor
URL_SCORE_IP_DOMAIN        = 30   # domain yerine IP adresi kullanmış
URL_SCORE_SUSPICIOUS_TLD   = 20   # .tk, .ml gibi ücretsiz ve kötüye kullanılan uzantılar
URL_SCORE_KEYWORD_DOMAIN   = 15   # domain içinde "login", "verify" gibi kelimeler var
URL_SCORE_LONG_DOMAIN      = 10   # 50 karakteri geçen domainler genelde sahte
URL_SCORE_EXCESS_SUBDOMAIN = 15   # 3'ten fazla subdomain varsa şüpheli
URL_SCORE_FREE_HOSTING     = 20   # netlify, github.io gibi ücretsiz barındırma servisleri
URL_SCORE_HYPHEN_SUBDOMAIN = 10   # "guvenli-hesap" gibi tireli subdomain
URL_SCORE_AT_SIGN          = 25   # URL'de @ işareti spoofing için kullanılıyor
URL_SCORE_NO_HTTPS         = 10   # HTTPS yoksa güvenli değil
URL_SCORE_KEYWORD_PATH     = 10   # URL yolunda şüpheli kelime var

URL_SUSPICIOUS_THRESHOLD = 20   # bu puanın üzerindeki URL şüpheli sayılıyor
URL_MAX_ANALYZE          = 10   # tek e-postada en fazla bu kadar URL analiz ediyoruz

# Header analiz puanları
HEADER_SCORE_DOMAIN_MISMATCH = 35   # From ve Reply-To farklı domain, bu neredeyse kesin kötü
HEADER_SCORE_IP_SENDER       = 30   # göndericinin IP adresi var, domain yok
HEADER_SCORE_FREE_MAIL_CORP  = 25   # gmail'den banka gibi davranıyor
HEADER_SCORE_SUSPICIOUS_WORD = 10   # gönderici adresinde "security", "alert" gibi kelimeler
HEADER_SCORE_URGENCY_WORD    = 15   # konu satırında "acil", "hemen" gibi baskı kelimeleri
HEADER_SCORE_ALL_CAPS        = 10   # konu tamamen büyük harf yazılmış
HEADER_SCORE_EXCLAIM         = 10   # birden fazla ünlem işareti var
HEADER_SCORE_MANY_DIGITS     = 5    # konuda çok fazla rakam var

HEADER_SUSPICIOUS_THRESHOLD = 20   # bu puanın üzerindeki header şüpheli sayılıyor
HEADER_MIN_CAPS_LEN         = 5    # büyük harf kontrolü için minimum konu uzunluğu
HEADER_EXCLAIM_MIN_COUNT    = 1    # bu sayının üzerinde ünlem varsa puan ekleniyor
HEADER_DIGIT_MIN_COUNT      = 6    # bu sayının üzerinde rakam varsa puan ekleniyor
