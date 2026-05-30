"""
Gerçekçi Türkçe E-posta Üretici
Çalıştır: python src/generate_turkish_emails.py

Kural: Gerçek e-posta formatı — selamlama + en az 2 paragraf + imza.
       Tek satır / SMS / WhatsApp / not tarzı kesinlikle üretilmez.
"""

import csv
import random
from pathlib import Path

random.seed(42)
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "turkish_generated.csv"

# ─────────────────────────────────────────────────────────────
# YARDIMCI VERİLER
# ─────────────────────────────────────────────────────────────

ISIMLER = [
    "Ayşe Kaya", "Mehmet Yılmaz", "Fatma Demir", "Ali Çelik", "Zeynep Arslan",
    "Mustafa Şahin", "Elif Yıldız", "Hasan Aydın", "Merve Koç", "Emre Polat",
    "Seda Güneş", "Burak Doğan", "Hatice Erdoğan", "Serkan Özcan", "Büşra Aslan",
    "Kemal Yurt", "Nilüfer Aktaş", "Oğuzhan Çetin", "Gülnur Bulut", "Tarık Ersoy",
    "Dilek Karahan", "Volkan Tekin", "Şeyma Güler", "Cenk Korkmaz", "Aslı Bayrak",
    "Umut Kaplan", "İrem Yıldırım", "Furkan Başar", "Neslihan Taş", "Arda Uysal",
    "Ceren Doğru", "Murat Kılıç", "Pınar Saygı", "Tolga Erdem", "Sibel Çakır",
    "Barış Yılmaz", "Derya Demirci", "Orkun Sever", "Yasemin Kurt", "Alper Tunç",
    "Deniz Öztürk", "Gökhan Acar", "Selin Karadeniz", "Taner Bozkurt", "Ece Gürbüz",
    "Serhat Duman", "Meltem Altın", "Onur Yıldız", "Berna Çelik", "Kaan Arslan",
]

SOYISIMLER = [
    "Kaya", "Yılmaz", "Demir", "Çelik", "Arslan", "Şahin", "Yıldız",
    "Aydın", "Koç", "Polat", "Güneş", "Doğan", "Erdoğan", "Özcan",
    "Yurt", "Aktaş", "Çetin", "Bulut", "Ersoy", "Karahan", "Tekin",
    "Güler", "Korkmaz", "Bayrak", "Kaplan", "Yıldırım", "Başar", "Taş",
    "Öztürk", "Acar", "Karadeniz", "Bozkurt", "Gürbüz", "Duman", "Altın",
]

SAHTE_LINKLER = [
    "http://guvenli-giris.banka-dogrulama.net/hesap",
    "https://hesap-dogrulama.garanti-musteri.tk/giris",
    "http://odeme-bekliyor.kargo-takip-tr.xyz/takip",
    "https://odul-kazandiniz.uyelik.info/talep",
    "http://microsoft-destek.tr-guvenlik.net/aktivasyon",
    "https://apple-kimlik.icloud-turkiye.co/dogrula",
    "http://paypal-hesap.odeme-onay.net/tr/giris",
    "https://dhl-kargo.teslimat-bekliyor.tk/adres",
    "http://vergiai-geri-odeme.gelir-idaresi.co/basvuru",
    "https://sosyal-guvenlik-destek.sgk-tr.net/basvuru",
    "http://hesap-dogrula.akbank-guvenlik.tk/giris",
    "https://kimlik-dogrula.tr-edevlet.net/giris",
    "http://kripto-kazan.bitcoin-tr.xyz/uye",
    "https://netflix-hesap.odeme-guncelle.tk/tr",
    "http://amazon-tr.paket-bekliyor.net/onay",
    "https://instagram-destek.hesap-koruma.co/itiraz",
    "http://sgk-emekli.destek-tr.net/basvuru",
    "https://bankam-guvenlik.hesapim-tr.xyz/onayla",
    "http://ucretsiz-kargo.kampanya-tr.net/kazan",
    "https://ozel-teklif.kredi-karti-tr.tk/basvur",
    "http://guvenli-odeme.tr-islem.net/dogrula",
    "https://kampanya-kazan.ucretsiz-uyelik.tk/al",
    "http://hesabim-askida.banka-tr-dogrula.net/giris",
    "https://teslimat-bekliyor.kargo-adres-guncelle.xyz/adres",
    "http://emekli-maas.sgk-guncelle.net/hesap",
    "http://is-basvurusu.kariyer-tr-net.xyz/basvur",
    "https://sigorta-odeme.police-guncelle.tk/hesap",
    "http://yatirim-kazan.borsa-tr.xyz/hesap",
    "https://saglik-sigorta.ozel-klinik-tr.net/randevu",
    "http://kamu-ihale.devlet-tr.xyz/basvuru",
    "https://banka-kredi.hizli-onay-tr.net/basvur",
    "http://hediye-kazan.markam-tr.xyz/odul",
    "https://vize-basvuru.konsolosluk-tr.net/form",
    "http://universite-kayit.egitim-tr.xyz/giris",
    "https://siber-guvenlik.destek-tr.net/tara",
]

GERCEK_LINKLER = [
    "https://www.garantibbva.com.tr",
    "https://www.akbank.com",
    "https://www.ziraatbank.com.tr",
    "https://www.hepsiburada.com",
    "https://www.trendyol.com",
    "https://www.n11.com",
    "https://www.ptt.gov.tr",
    "https://www.turkcell.com.tr",
    "https://www.vodafone.com.tr",
    "https://www.lcwaikiki.com",
    "https://www.boyner.com.tr",
    "https://www.migros.com.tr",
    "https://biletix.com",
    "https://www.yemeksepeti.com",
    "https://www.kariyer.net",
    "https://www.sahibinden.com",
    "https://www.turkhava.com.tr",
    "https://www.ekol.com",
    "https://www.sgk.gov.tr",
    "https://www.gib.gov.tr",
]

BANKALAR = [
    "Garanti BBVA", "Akbank", "İş Bankası", "Ziraat Bankası",
    "Yapı Kredi", "Halkbank", "VakıfBank", "Denizbank",
    "QNB Finansbank", "TEB", "ING Bank", "HSBC Türkiye",
]
KARGO_FIRMALARI = [
    "Yurtiçi Kargo", "Aras Kargo", "PTT Kargo",
    "MNG Kargo", "Sürat Kargo", "UPS", "DHL", "Trendyol Express",
]
MARKALAR = [
    "Trendyol", "Hepsiburada", "N11", "GittiGidiyor",
    "Boyner", "LC Waikiki", "Zara", "H&M",
    "Migros", "Carrefour", "MediaMarkt", "Teknosa",
]
OPERATORLER    = ["Turkcell", "Vodafone", "Türk Telekom"]
SEHIRLER       = [
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya",
    "Adana", "Konya", "Gaziantep", "Mersin", "Kayseri",
    "Eskişehir", "Trabzon", "Samsun", "Diyarbakır", "Kocaeli",
]
POZISYONLAR = [
    "Yazılım Geliştirici", "Proje Yöneticisi", "Pazarlama Uzmanı",
    "Veri Analisti", "Muhasebe Uzmanı", "İnsan Kaynakları Uzmanı",
    "Satış Temsilcisi", "Müşteri Hizmetleri Uzmanı", "Grafik Tasarımcı",
    "İş Geliştirme Uzmanı", "Ürün Müdürü", "Lojistik Koordinatörü",
]
UNIVERSITELER = [
    "İstanbul Üniversitesi", "Ankara Üniversitesi", "Ege Üniversitesi",
    "Boğaziçi Üniversitesi", "ODTÜ", "Sabancı Üniversitesi",
    "Koç Üniversitesi", "Gazi Üniversitesi", "Hacettepe Üniversitesi",
    "İTÜ", "Bilkent Üniversitesi", "Yıldız Teknik Üniversitesi",
]
DERSLER = [
    "Veri Yapıları ve Algoritmalar", "Makine Öğrenmesi",
    "Nesneye Yönelik Programlama", "Veritabanı Yönetim Sistemleri",
    "İşletim Sistemleri", "Bilgisayar Ağları", "Yapay Zeka",
    "Web Programlama", "Mobil Uygulama Geliştirme", "Siber Güvenlik",
]
SIGORTA_TURLERI = [
    "Kasko Sigortası", "Sağlık Sigortası", "Konut Sigortası",
    "Hayat Sigortası", "Trafik Sigortası", "İşyeri Sigortası",
]
URUN_KATEGORILERI = [
    "Elektronik", "Giyim", "Ev ve Bahçe", "Spor", "Kitap",
    "Kozmetik", "Oyuncak", "Otomotiv Aksesuar",
]
UNVANLAR = ["Sayın", "Değerli", "Sayın Müşterimiz"]

# ─────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────

def _isim():        return random.choice(ISIMLER)
def _soyisim():     return random.choice(SOYISIMLER)
def _banka():       return random.choice(BANKALAR)
def _kargo():       return random.choice(KARGO_FIRMALARI)
def _marka():       return random.choice(MARKALAR)
def _link():        return random.choice(SAHTE_LINKLER)
def _glink():       return random.choice(GERCEK_LINKLER)
def _operator():    return random.choice(OPERATORLER)
def _sehir():       return random.choice(SEHIRLER)
def _pozisyon():    return random.choice(POZISYONLAR)
def _uni():         return random.choice(UNIVERSITELER)
def _ders():        return random.choice(DERSLER)
def _sigorta():     return random.choice(SIGORTA_TURLERI)
def _urun_kat():    return random.choice(URUN_KATEGORILERI)
def _unvan():       return random.choice(UNVANLAR)

def _tutar():
    return random.choice([
        "890", "1.250", "2.450", "3.800", "5.900",
        "8.750", "12.400", "15.750", "23.600", "47.900",
        "64.500", "125.000", "248.000",
    ])

def _kargo_no():
    return "".join([str(random.randint(0, 9)) for _ in range(10)])

def _siparis_no():
    return f"#{random.randint(100_000_000, 999_999_999)}"

def _tarih():
    gun = random.randint(1, 28)
    ay  = random.choice([
        "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
    ])
    return f"{gun} {ay} 2024"

def _saat():
    return f"{random.randint(9, 18)}:{random.choice(['00', '30'])}"

def _ip():
    return (f"{random.randint(80, 220)}.{random.randint(10, 255)}"
            f".{random.randint(1, 254)}.{random.randint(1, 254)}")

def _maas():
    return random.choice(["18.500", "22.000", "28.000", "35.000", "45.000", "60.000"])

def _yuzde():
    return random.choice([10, 15, 20, 25, 30, 40, 50])


# ═════════════════════════════════════════════════════════════
# PHİSHİNG  (label = 1)
# ═════════════════════════════════════════════════════════════

# ── 1. FİNANSAL DOLANDIRICILIK ───────────────────────────────

FINANSAL = [

    lambda: f"""{_unvan()} {_isim()},

{_banka()} Güvenlik ve Dolandırıcılık Önleme Birimi olarak, hesabınızda {_tarih()} tarihinde gerçekleşen olağandışı bir işlemi sizinle paylaşmak istiyoruz. {_tutar()} TL tutarında yurt dışı kaynaklı bir para transferi başlatılmış olup bu işlem şu an inceleme sürecinde askıya alınmış durumdadır.

Bu transferi siz başlatmadıysanız hesabınıza yetkisiz erişim söz konusu olabilir. Hesabınızın güvenliğini sağlamak ve işlemi iptal etmek için kimlik doğrulama sürecini 24 saat içinde tamamlamanız gerekmektedir. Aksi takdirde işlem otomatik olarak onaylanacak ve para aktarımı gerçekleşecektir.

Güvenli Doğrulama Bağlantısı: {_link()}

Saygılarımızla,
{_banka()} Güvenlik ve Dolandırıcılık Önleme Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Gelir İdaresi Başkanlığı bünyesinde yürütülen yıl sonu vergi denetimi kapsamında {_tarih()} - {_tarih()} dönemine ait beyanlarınız incelenmiştir. İnceleme sonucunda {_tutar()} TL tutarında fazla vergi ödemesi yapıldığı tespit edilmiş olup bu tutarın iadesi için başvuru sürecinizi başlatmanız gerekmektedir.

İade başvurusunu tamamlayabilmek için kimlik doğrulaması ve güncel banka hesap bilgilerinizin sisteme işlenmesi zorunludur. Başvurunuzu 30 gün içinde tamamlamazsanız iade hakkınız zaman aşımına uğrayacaktır.

İade Başvuru Portalı: {_link()}

Saygılarımızla,
Gelir İdaresi Başkanlığı — e-Hizmetler ve İade Birimi""",

    lambda: f"""{_unvan()} {_isim()},

{_banka()} internet bankacılığı sistemimiz {_tarih()} tarihinde güvenlik altyapısı güncellemesi almıştır. Bu güncelleme kapsamında tüm müşterilerimizin hesap erişim bilgilerini {_tarih()} tarihine kadar yenilemeleri zorunlu hale gelmiştir.

Güncelleme işlemi yaklaşık 5 dakika sürmekte olup yeni şifrenizi sisteme tanımlamanız yeterli olacaktır. İşlemi tamamlamayan müşterilerimizin hesaplarına erişim geçici olarak kısıtlanacaktır.

Hesap Güncelleme Portalı: {_link()}

Saygılarımızla,
{_banka()} Dijital Bankacılık Departmanı""",

    lambda: f"""{_unvan()} {_isim()},

Kredi kartınızın {_tarih()} tarihli ekstresini incelediğimizde {_tutar()} TL tutarında tanımlanmamış bir işlem kaydı tespit ettik. İşlem yurt dışı kaynaklı görünmekte olup IP adresi {_ip()} olarak kayıtlara geçmiştir.

Bu işlemi siz gerçekleştirmediyseniz kartınızı geçici olarak bloke edebilir ve iade sürecini başlatabilirsiniz. İtiraz işlemini 48 saat içinde başlatmanız, hızlı çözüm sağlanması açısından büyük önem taşımaktadır.

Kart İtiraz ve Durdurma Formu: {_link()}

Saygılarımızla,
{_banka()} Kart Hizmetleri ve İtiraz Birimi""",

    lambda: f"""{_unvan()} {_isim()},

SGK Sosyal Güvenlik Kurumu kayıtlarınız incelendiğinde, {_tarih()} - {_tarih()} dönemini kapsayan emeklilik prim ödemelerinizde eksiklik tespit edilmiştir. Söz konusu eksikliğin giderilmesi için prim güncelleme işleminin en geç {_tarih()} tarihine kadar tamamlanması gerekmektedir.

Prim güncellemesi yapılmaması durumunda gelecekteki emeklilik hak hesaplamalarınız eksik bilgi üzerinden yapılacak ve maaş miktarınız olumsuz etkilenebilecektir. İşlemi T.C. kimlik numaranız ve emeklilik sicil numaranızla online olarak gerçekleştirebilirsiniz.

Prim Güncelleme Sistemi: {_link()}

Saygılarımızla,
SGK Dijital Hizmetler Birimi""",

    lambda: f"""{_unvan()} {_isim()},

{_operator()} Fatura Hizmetleri olarak, {_tarih()} dönem faturanızda {_tutar()} TL tutarında beklenmedik bir ücret oluştuğunu bildirmek isteriz. Bu ücretin standart aboneliğiniz dışında tanımlanan bir hizmetten kaynaklandığı değerlendirilmektedir.

Söz konusu ücrete itiraz etmek ve fatura detaylarınızı incelemek için müşteri portalımıza erişmenizi öneririz. İtirazınızı 48 saat içinde iletmeniz, işlemin tahsil edilmeden çözüme kavuşturulması açısından kritik önem taşımaktadır.

İtiraz ve İnceleme Formu: {_link()}

Saygılarımızla,
{_operator()} Fatura ve İtiraz Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

{_banka()} Mortgage Değerlendirme Birimi tarafından konut kredisi ön başvurunuz incelenmiştir. Başvurunuz ön onay aşamasını başarıyla geçmiş olup {_tutar()} TL tutarında kredi limiti tanımlanmaya hazır durumdadır.

Kredi işleminin tamamlanabilmesi için gelir belgesi, tapu bilgileri ve kimlik doğrulamasının sistem üzerinden yüklenmesi gerekmektedir. Ön onayınızın geçerlilik süresi {_tarih()} tarihinde dolacaktır.

Başvuru Tamamlama Portalı: {_link()}

Saygılarımızla,
{_banka()} Bireysel Bankacılık ve Kredi Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Yatırım portföyünüzde takip edilen kripto para biriminizin değeri son 24 saatte önemli ölçüde artış kaydetmiştir. Kârınızı realize etmek ve hesabınıza aktarmak için kimlik doğrulama işlemini tamamlamanız gerekmektedir.

Platform güvenlik politikamız gereği {_tutar()} TL üzerindeki çekim işlemlerinde ek doğrulama zorunludur. İşlemi aşağıdaki bağlantı üzerinden 2 saat içinde tamamlamanızı öneririz; aksi takdirde çekim talebiniz otomatik iptal edilecektir.

Hesap Doğrulama ve Çekim: {_link()}

Saygılarımızla,
Yatırım Platformu Güvenlik Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Türkiye Cumhuriyet Merkez Bankası tarafından yürütülen döviz hesabı uyum denetimi kapsamında hesabınıza ait bilgilerin güncellenmesi talep edilmektedir. Bu denetim, kara para aklamanın önlenmesine yönelik yasal düzenlemeler çerçevesinde gerçekleştirilmektedir.

Döviz hesabınızdaki {_tutar()} TL karşılığındaki tutarın kaynağını belgelemeniz ve kimlik bilgilerinizi doğrulamanız için aşağıdaki portala erişmeniz gerekmektedir. İşlemi 5 iş günü içinde tamamlamazsanız hesabınız dondurulabilir.

Uyum Doğrulama Portalı: {_link()}

Saygılarımızla,
Denetim ve Uyum Birimi""",
]

# ── 2. KİMLİK HIRSIZLIĞI ────────────────────────────────────

KIMLIK = [

    lambda: f"""{_unvan()} {_isim()},

e-Devlet Kapısı'na entegre edilen yeni güvenlik sistemi kapsamında tüm kullanıcıların kimlik bilgilerini {_tarih()} tarihine kadar doğrulamaları zorunlu hale getirilmiştir. Doğrulamayı tamamlamayan kullanıcıların e-Devlet hizmetlerine erişimi geçici olarak kısıtlanacaktır.

Güncelleme işlemi sırasında T.C. Kimlik Numaranız, nüfus cüzdanı seri numaranız ve kayıtlı cep telefonu numaranız talep edilecektir. İşlem yalnızca birkaç dakika sürecektir.

Kimlik Doğrulama Portalı: {_link()}

Saygılarımızla,
e-Devlet Kapısı Yönetim Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Microsoft hesabınıza {_tarih()} tarihinde {_sehir()} dışındaki bilinmeyen bir konumdan giriş yapıldığı tespit edilmiştir. Giriş yapan cihazın konum ve tarayıcı bilgileri mevcut profilinizle eşleşmemektedir.

Hesabınızın güvenliğini sağlamak için şifrenizi hemen değiştirmenizi ve iki adımlı doğrulamayı aktif hale getirmenizi tavsiye ederiz. Aşağıdaki güvenlik merkezinden gerekli adımları takip edebilirsiniz.

Güvenlik Merkezi: {_link()}

Saygılarımızla,
Microsoft Hesap Güvenlik Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Google hesabınızla ilişkilendirilmiş telefon numaranız {_tarih()} tarihinde değiştirilmiş; bu değişikliği sizden farklı bir cihazdan gerçekleştiren kişi hesabınıza erişmiş görünmektedir. Güvenlik sistemimiz bu işlemi şüpheli olarak işaretlemiştir.

Hesabınızı kurtarmak ve değişikliği geri almak için 24 saat içinde harekete geçmenizi öneririz. İşlem sırasında mevcut şifreniz ve yedek e-posta adresiniz istenecektir.

Hesap Kurtarma: {_link()}

Saygılarımızla,
Google Güvenlik Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_operator()} Güvenlik Birimi olarak, hattınıza ait SIM kartın {_tarih()} tarihinde {_sehir()} bölgesinde bir bayide değiştirildiğini bildirmek istiyoruz. Bu işlem sonucunda tüm arama ve mesaj trafiğiniz yeni SIM karta yönlendirilmiş durumdadır.

Bu işlemi siz gerçekleştirmediyseniz hattınıza yetkisiz el konulmuş olabilir. Hattınızı orijinal cihazınıza geri almak ve yeni SIM'i bloke etmek için aşağıdaki formu doldurmanız gerekmektedir.

Hat Güvenlik Formu: {_link()}

Saygılarımızla,
{_operator()} Hat Güvenlik Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Instagram hesabınıza ait e-posta adresi değiştirilmek üzere talep alınmıştır. Sistem bu isteği güvenlik protokolümüz gereği geçici olarak askıya almıştır; ancak 1 saat içinde işlem onaylanacaktır.

Bu talebi siz oluşturmadıysanız hesabınıza yetkisiz erişim girişimi söz konusu olabilir. Talebi iptal etmek ve hesabınızı güvenceye almak için hemen harekete geçmeniz gerekmektedir.

Hesap Güvenlik Merkezi: {_link()}

Saygılarımızla,
Instagram Güvenlik Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_uni()} öğrenci bilgi sistemi, güvenlik altyapısı yükseltmesi kapsamında yeni bir kimlik doğrulama sistemine geçiş yapmıştır. {_tarih()} tarihine kadar hesabınızı yeni sisteme taşımazsanız not görüntüleme, sınav başvurusu ve kayıt yenileme işlemlerine erişiminiz engellenecektir.

Taşıma işlemi için öğrenci numaranız ve T.C. kimlik numaranızla aşağıdaki portala giriş yapmanız yeterlidir. İşlem yalnızca 3-5 dakika sürmektedir.

Öğrenci Portalı Taşıma: {_link()}

Saygılarımızla,
{_uni()} Bilgi İşlem Daire Başkanlığı""",

    lambda: f"""{_unvan()} {_isim()},

LinkedIn profilinize {_tarih()} tarihinde bilinmeyen bir konumdan erişim denenmiştir. Deneme başarısız olmakla birlikte güvenlik sistemimiz bu girişimi şüpheli olarak işaretlemiş ve hesabınıza geçici kısıtlama uygulamıştır.

Hesabınızın tam kontrolünü geri almak, şüpheli cihaz erişimini engellemek ve şifrenizi güncellemek için güvenlik merkezimizi ziyaret etmenizi öneririz.

LinkedIn Güvenlik Merkezi: {_link()}

Saygılarımızla,
LinkedIn Güvenlik Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Nüfus Müdürlüğü sistemleri kapsamında gerçekleştirilen adres güncelleme çalışması sırasında, kayıtlı adres bilgilerinizde tutarsızlık tespit edilmiştir. Yasal yükümlülükler gereği adres bilgilerinizin {_tarih()} tarihine kadar güncellenmesi zorunlu tutulmaktadır.

Güncelleme işlemi için T.C. Kimlik Numaranız ve güncel iletişim bilgilerinizle sisteme giriş yapmanız yeterlidir. Güncelleme yapılmaması halinde resmi yazışmalar eski adresinize iletilmeye devam edecektir.

Adres Güncelleme Portalı: {_link()}

Saygılarımızla,
Nüfus ve Vatandaşlık İşleri Genel Müdürlüğü""",
]

# ── 3. KÖTÜ AMAÇLI LİNK ─────────────────────────────────────

KOTU_LINK = [

    lambda: f"""{_unvan()} {_isim()},

{random.choice(ISIMLER)}, sizinle önemli bir belge paylaşmıştır. Belge, şirket platformumuz üzerinden güvenli biçimde iletilmiş olup yalnızca yetkili alıcılar tarafından görüntülenebilmektedir. Gizlilik politikamız gereği belge içeriği bu e-postada yer almamaktadır.

Belgeye erişmek için aşağıdaki bağlantıyı kullanabilirsiniz. Bağlantı 72 saat boyunca aktif kalacak olup bu süre içinde erişim sağlamamanız durumunda belgeye bir daha ulaşamayabilirsiniz.

Belgeyi Görüntüle: {_link()}

Saygılarımızla,
Güvenli Belge Paylaşım Sistemi""",

    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihli {_tutar()} TL tutarındaki faturanız sisteme yüklenmiştir. Fatura No: {_kargo_no()} — Vade Tarihi: {_tarih()}.

Faturanızı görüntülemek, PDF olarak indirmek veya itiraz başlatmak için müşteri portalımıza giriş yapabilirsiniz. Vade tarihinden sonra gecikme faizi uygulanacak olup ödeme planı oluşturma seçeneğiniz kısıtlanacaktır.

Fatura Portalı: {_link()}

Saygılarımızla,
Fatura ve Finans Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Bilgisayarınızda yüklü güvenlik yazılımının lisansı {_tarih()} tarihinde sona ermektedir. Lisans yenilenmediği takdirde cihazınız virüs, casus yazılım ve fidye yazılımı tehditlerine karşı korumasız kalacaktır. Bu tür saldırılar kişisel verilerinizin ve finansal bilgilerinizin çalınmasına yol açabilir.

Mevcut müşterilerimize sunduğumuz özel yenileme kampanyasından yararlanmak için aşağıdaki bağlantıyı kullanabilirsiniz. İlk 100 yenileme için %{_yuzde()} ek indirim geçerlidir.

Lisans Yenileme: {_link()}

Saygılarımızla,
Güvenlik Yazılımı Destek Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde gerçekleştirilecek çevrimiçi toplantıya davetlisiniz. Toplantı, {random.choice(ISIMLER)} tarafından düzenlenecek olup gündem; {random.choice(['proje ilerlemesinin değerlendirilmesi', 'bütçe planlaması', 'ürün yol haritası güncellemesi', 'müşteri geri bildirim analizi', 'strateji belirleme oturumu'])} konularını kapsamaktadır.

Toplantı saati {_saat()} olarak planlanmıştır ve tahminen {random.randint(1, 2)} saat sürecektir. Katılım için aşağıdaki bağlantıya tıklayarak platformumuza önceden kayıt olmanız gerekmektedir.

Toplantıya Katıl: {_link()}

Saygılarımızla,
Toplantı Organizasyon Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_uni()} kütüphane sistemine entegre edilen yeni dijital kaynak portalı {_tarih()} tarihi itibarıyla hizmete girmiştir. Bu platform aracılığıyla binlerce akademik makale, e-kitap ve veri tabanına uzaktan erişim sağlayabilirsiniz.

İlk girişte kurumsal e-posta adresinizi ve öğrenci/akademisyen şifrenizi doğrulamanız gerekmektedir. Erişim sorunlarınız için bilgi işlem birimi ile iletişime geçebilirsiniz.

Dijital Kaynak Portalı: {_link()}

Saygılarımızla,
{_uni()} Kütüphane Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Sistemimiz, bilgisayarınızda güvenlik açığı içerdiği tespit edilen bir yazılım sürümü fark etmiştir. Bu açık, uzaktan kod çalıştırma saldırılarına karşı savunmasızlık oluşturmakta olup derhal güncelleme yapılmasını önermekteyiz.

Güncelleme paketini indirmek ve yüklemek için aşağıdaki bağlantıyı kullanabilirsiniz. Güncellemeden önce açık uygulamalarınızı kaydetmenizi tavsiye ederiz. İşlem yaklaşık 10 dakika sürecektir.

Güvenlik Güncellemesini İndir: {_link()}

Saygılarımızla,
Sistem Güvenliği Destek Ekibi""",
]

# ── 4. SAHTE ÖDÜL / ÇEKİLİŞ ─────────────────────────────────

ODUL = [

    lambda: f"""TEBRİKLER, {_isim().upper()}!

{_marka()} Yıl Sonu Çekilişi'nin kazananı olarak seçildiniz! Çekiliş {_tarih()} tarihinde noter huzurunda gerçekleştirilmiş olup {_tutar()} TL değerindeki ödül hesabınıza tanımlanmayı beklemektedir.

Ödülünüzü talep etmek için kimlik doğrulama işlemini {_tarih()} tarihine kadar tamamlamanız gerekmektedir. Doğrulama sonrasında ödülünüz 2 iş günü içinde banka hesabınıza aktarılacaktır.

Ödül Talep Formu: {_link()}

Saygılarımızla,
{_marka()} Ödül ve Kampanya Yönetim Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_marka()} müşteri memnuniyeti anketine katılımınız için özel bir davetiye hazırlandı. Anketi tamamlayan her katılımcı {_tutar()} TL değerinde alışveriş çeki ve özel hediye paketine hak kazanmaktadır.

Anket yalnızca 5 dakika sürmekte olup yanıtlarınız ürün ve hizmet kalitemizin artırılmasında doğrudan katkı sağlayacaktır. Katılım için aşağıdaki bağlantıyı kullanabilirsiniz.

Ankete Katıl ve Ödülünü Kazan: {_link()}

Saygılarımızla,
{_marka()} Müşteri Deneyimi ve Kampanya Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Hesabınızda biriken {random.randint(5_000, 50_000):,} sadakat puanı, {_tarih()} tarihi itibarıyla {_tutar()} TL değerinde hediye çekine dönüştürülmeye hak kazanmıştır. Hediye çekinizi tüm kategori ve ürünlerde kullanabilirsiniz.

Çekinizi aktive etmek için üye portalına giriş yapmanız yeterlidir. Çek, aktivasyondan itibaren 30 gün boyunca geçerli olacaktır. {_tarih()} tarihine kadar aktive edilmezse puanlarınız sıfırlanacaktır.

Üye Portalı ve Ödül Aktivasyonu: {_link()}

Saygılarımızla,
Sadakat Programı Yönetim Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_operator()} {random.randint(15, 25)}. Yıl Dönümü Kampanyası kapsamında düzenlenen büyük çekilişte adınız kura ile belirlenmiştir. Ödülünüz: yeni nesil akıllı telefon ve 12 aylık {_tutar()} TL değerinde tarife paketi hediyesi.

Ödülünüzü teslim alabilmek için hat sahipliğinizi doğrulamanız ve teslimat adresinizi sisteme girmeniz gerekmektedir. Doğrulama işlemi tamamen çevrimiçi olarak yürütülmektedir.

Ödül Teslimat Formu: {_link()}

Saygılarımızla,
{_operator()} Kampanya ve Ödül Merkezi""",

    lambda: f"""{_unvan()} {_isim()},

{_sehir()} Büyükşehir Belediyesi tarafından düzenlenen "Çevre Dostu Ulaşım" kampanyası kapsamında toplu taşıma kullanım verileriniz incelenmiş ve siz üst %{_yuzde()} diliminde yer almıştınız. Bu başarınız nedeniyle {_tutar()} TL değerinde ulaşım kartı bakiyesi hediye edilmektedir.

Hediyenizi hesabınıza tanımlatmak için aşağıdaki formu doldurup kimlik doğrulamanızı tamamlayabilirsiniz. İşlem sonucunda bakiye 48 saat içinde kartınıza yüklenir.

Hediye Talep Formu: {_link()}

Saygılarımızla,
{_sehir()} Büyükşehir Belediyesi — Ulaşım Hizmetleri""",
]

# ── 5. SAHTE KARGO / TESLİMAT ────────────────────────────────

KARGO_P = [

    lambda: f"""{_unvan()} {_isim()},

{_kargo()} Teslimat Ekibi olarak, {_siparis_no()} numaralı siparişinizin teslimat sürecinde önemli bir güncelleme olduğunu bildirmek istiyoruz. Teslimat adresinizde yaşanan doğrulama sorunu nedeniyle kargonuz dağıtım deposunda beklemektedir.

Teslimatın gerçekleşebilmesi için adres bilgilerinizi {_tarih()} tarihine kadar güncellemeniz gerekmektedir. Bu süre içinde güncelleme yapılmaması durumunda kargo, gönderene iade edilecektir.

Adres Güncelleme: {_link()}

Saygılarımızla,
{_kargo()} Müşteri Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde kargoya verilen {_siparis_no()} numaralı siparişiniz gümrük kontrolü aşamasında beklemektedir. Ürün kategorinize ait ek belge ve harç ödemesi talep edilmiştir.

Ürününüzün serbest bırakılabilmesi için {_tutar()} TL tutarındaki gümrük harcının ödenmesi ve kimlik belgenizin sisteme yüklenmesi gerekmektedir. İşlemi tamamlamazsanız ürün gönderene iade edilecektir.

Gümrük İşlem ve Ödeme Formu: {_link()}

Saygılarımızla,
Gümrük Müşavirliği Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

PTT Kargo Dağıtım Merkezi olarak, adınıza kayıtlı bir gönderinin {_tarih()} tarihinde {_sehir()} şubesine ulaştığını bildirmek isteriz. Gönderici bilgileri sistemimizde gizlilik kapsamında tutulmakta olup teslimatta açıklanacaktır.

Gönderiyi alabilmek için kimlik belgenizle şubemize gelmeniz ya da aşağıdaki portal üzerinden teslimat tercihinizi belirlemeniz gerekmektedir. Paket 5 iş günü sonra iade edilecektir.

Teslimat Yönetim Portalı: {_link()}

Saygılarımızla,
PTT Kargo Müşteri Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

{_marka()} üzerinden verdiğiniz {_siparis_no()} numaralı siparişin teslimat tarihi lojistik operasyonel nedenlerle {_tarih()}'den {_tarih()}'e revize edilmiştir. Bu gecikme için özür dileriz.

Yeni teslimat tarihinde adresinizde bulunmamanız durumunda teslimat tercihlerinizi güncelleyebilir ya da teslimatı komşunuza yönlendirebilirsiniz. Güncelleme için aşağıdaki paneli kullanabilirsiniz.

Teslimat Tercih Güncelleme: {_link()}

Saygılarımızla,
{_marka()} Lojistik ve Teslimat Birimi""",

    lambda: f"""{_unvan()} {_isim()},

{_kargo_no()} takip numaralı kargonuz, taşıma aracının rota değişikliğine gitmesi nedeniyle {_sehir()} bölgesindeki ara depoda geçici olarak bekletilmektedir. Teslimat süresi en az 2 iş günü uzayabilecektir.

Gecikmenin önüne geçmek için alternatif teslimat noktası veya farklı adres belirleyebilirsiniz. Ayrıca kargo sigorta başvurusunu da bu ekran üzerinden gerçekleştirebilirsiniz.

Teslimat Yönetim Paneli: {_link()}

Saygılarımızla,
{_kargo()} Teslimat Operasyonları""",
]

# ── 6. MARKA TAKLİDİ ─────────────────────────────────────────

MARKA_TAKLIT = [

    lambda: f"""{_unvan()} {_isim()},

Netflix hesabınıza kayıtlı ödeme yöntemi {_tarih()} tarihinde reddedilmiştir. Aboneliğinizin kesintisiz devam edebilmesi için ödeme bilgilerinizi {_tarih()} tarihine kadar güncellemeniz gerekmektedir.

Güncelleme yapılmaması halinde hesabınız ücretsiz plana düşürülecek ve izleme geçmişiniz silinecektir. İşlem yalnızca birkaç dakika sürmektedir.

Ödeme Bilgilerini Güncelle: {_link()}

Saygılarımızla,
Netflix Müşteri Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Amazon Türkiye hesabınızda {_tarih()} tarihinde {_tutar()} TL tutarında olağandışı bir satın alma girişimi tespit edilmiştir. Güvenlik sistemimiz bu işlemi şüpheli olarak işaretlemiş ve hesabınıza geçici kısıtlama uygulamıştır.

Hesabınızı yeniden aktive etmek ve söz konusu işlemi incelemek için kimlik doğrulama işlemini tamamlamanız gerekmektedir. İşlemi 24 saat içinde gerçekleştirmenizi öneririz.

Hesap Doğrulama: {_link()}

Saygılarımızla,
Amazon Türkiye Güvenlik Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Apple Kimliğiniz, {_tarih()} tarihinde {_sehir()} dışında bilinmeyen bir cihazdan kullanılmaya çalışılmıştır. Güvenlik protokolümüz bu girişimi durdurmuş olmakla birlikte hesabınızın korunması için ek adım atmanız önerilmektedir.

Hesabınızı güvenceye almak, tanınmayan cihazı engellemek ve şifrenizi güncellemek için aşağıdaki güvenlik merkezi bağlantısını kullanabilirsiniz.

Apple Kimlik Güvenlik Merkezi: {_link()}

Saygılarımızla,
Apple Güvenlik Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Spotify Premium aboneliğinizin {_tarih()} tarihindeki otomatik yenileme işlemi başarısız olmuştur. Ödeme yönteminizin güncel olmadığı değerlendirilmektedir.

Aboneliğinizin kesintiye uğramaması ve Premium özelliklerinizi kaybetmemeniz için ödeme bilgilerinizi en kısa sürede güncellemenizi öneririz. Güncellemeyi {_tarih()} tarihine kadar yapmazsanız hesabınız otomatik olarak ücretsiz plana geçirilecektir.

Ödeme Yönetimi: {_link()}

Saygılarımızla,
Spotify Müşteri Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Trendyol hesabınızda {_tarih()} tarihinde gerçekleştirilen {_tutar()} TL tutarındaki sipariş, teslimat adresiyle ilgili doğrulama hatası nedeniyle iptal edilmiştir. Stoktaki ürünlerin tükenmemesi için siparişinizi yeniden oluşturmanızı öneririz.

Hesabınıza giriş yaparak siparişi yenilemek veya mevcut adresinizi güncellemek için aşağıdaki bağlantıyı kullanabilirsiniz. Yeniden oluşturulan sipariş için öncelikli teslimat hakkı tanınacaktır.

Hesaba Giriş ve Sipariş Yenileme: {_link()}

Saygılarımızla,
Trendyol Müşteri Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Hepsiburada hesabınızda kayıtlı kredi kartınızın son kullanma tarihi geçmiştir. Hesabınıza tanımlı ödeme yönteminin güncellenmemesi durumunda yapacağınız siparişlerde ödeme işlemi tamamlanamayacaktır.

Ödeme bilgilerinizi güncellemek ve hesabınızda birikmiş {_tutar()} TL değerindeki Hepsiburada Ödeme Kartı bakiyenizi kullanmaya devam etmek için aşağıdaki bağlantıyı ziyaret edebilirsiniz.

Ödeme Yönetimi: {_link()}

Saygılarımızla,
Hepsiburada Müşteri Hizmetleri""",
]

# ── 7. SAHTE İŞ TEKLİFİ ─────────────────────────────────────

SAHTE_IS = [

    lambda: f"""{_unvan()} {_isim()},

CV havuzumuzda incelediğimiz profiliniz, {_pozisyon()} pozisyonu için belirlediğimiz nitelikleri karşılamaktadır. Bu nedenle sizi hızlandırılmış işe alım sürecimize davet etmek istiyoruz.

Pozisyon; {_sehir()} merkezli olup aylık {_maas()} TL başlangıç maaşı, esnek çalışma saatleri ve kapsamlı sosyal haklar sunmaktadır. İşe başlama tarihiniz müzakereye açık olup süreç yalnızca birkaç gün içinde tamamlanabilir.

Ön Başvuru ve Mülakata Davet: {_link()}

Saygılarımızla,
İnsan Kaynakları Koordinatörlüğü""",

    lambda: f"""{_unvan()} {_isim()},

Uluslararası iş platformumuzda kayıtlı profilinizi inceledik ve {_pozisyon()} rolü için son derece uygun buluyoruz. Şirketimiz {_sehir()} ofisi için yetenekli profesyoneller arıyor.

Sunduğumuz paket; {_maas()} TL aylık ücret, yılda iki kez performans primi, özel sağlık sigortası ve esnek çalışma düzenlemesini kapsamaktadır. Mülakatı hızlı tamamlamak adına önce çevrimiçi değerlendirme formunu doldurmanızı rica ediyoruz.

Değerlendirme Formu ve Başvuru: {_link()}

Saygılarımızla,
Global Recruitment Partners — Türkiye Ofisi""",

    lambda: f"""{_unvan()} {_isim()},

Kariyer platformumuzda yayınlanan {_pozisyon()} ilanımıza uygun bir profil taşıdığınızı tespit ettik ve sizi doğrudan değerlendirme sürecine almak istiyoruz. Standart başvuru aşamasını atlayarak mülakata davet edileceksiniz.

Pozisyon {_sehir()} veya uzaktan çalışma seçeneğiyle sunulmakta olup aylık brüt ücret {_maas()} TL'den başlamaktadır. Yemek, servis ve sağlık sigortası sosyal haklara dahildir.

Davet Onay Formu: {_link()}

Saygılarımızla,
Kurumsal Yetenek Edinimi Ekibi""",
]

# ── 8. SAHTE SİGORTA ─────────────────────────────────────────

SAHTE_SIGORTA = [

    lambda: f"""{_unvan()} {_isim()},

{_sigorta()} poliçeniz {_tarih()} tarihinde yenilenecek olup yenileme öncesinde poliçe koşullarında güncelleme yapılmıştır. Yeni koşulları onaylamak ve poliçenizin devamlılığını sağlamak için sisteme giriş yapmanız gerekmektedir.

Giriş yapmamanız durumunda poliçeniz belirtilen tarihten itibaren geçersiz hale gelecek ve sigorta güvenceniz sona erecektir. İşlem yalnızca birkaç dakika sürmektedir.

Poliçe Onay Portalı: {_link()}

Saygılarımızla,
Sigorta Hizmetleri Departmanı""",

    lambda: f"""{_unvan()} {_isim()},

Araç kasko sigorta dosyanız incelemiş; {_tarih()} tarihinde yaşanan hasar olayına ilişkin hasar tazminat bedelinizin hesaplandığı belirlenmiştir. Tazminat miktarı: {_tutar()} TL.

Ödemenin banka hesabınıza aktarılabilmesi için IBAN bilgilerinizin onaylanması ve kimlik doğrulamanın tamamlanması gerekmektedir. İşlemi 10 iş günü içinde tamamlamazsanız dosyanız arşive kaldırılacaktır.

Tazminat Başvuru Formu: {_link()}

Saygılarımızla,
Hasar Tazminat Birimi""",
]

# ── 9. SAHTE KAMU / DEVLET ───────────────────────────────────

SAHTE_DEVLET = [

    lambda: f"""{_unvan()} {_isim()},

Mahkeme kayıtları incelendiğinde, adınıza açılmış bir dava dosyası tespit edilmiştir. Söz konusu dava {_tarih()} tarihinde {_sehir()} Asliye Hukuk Mahkemesi'nde görülecek olup tarafınıza tebligat yapılamamıştır.

Davadan haberdar olmanız ve hukuki haklarınızı kullanabilmeniz için dosya detaylarını incelemeniz ve avukat atamanız gerekmektedir. Aşağıdaki e-tebligat sistemi üzerinden dosyaya erişebilirsiniz.

e-Tebligat Erişim Portalı: {_link()}

Saygılarımızla,
e-Tebligat Sistemi — Adalet Bakanlığı""",

    lambda: f"""{_unvan()} {_isim()},

Belediye tahsilat sistemi kayıtlarına göre adınıza kayıtlı taşınmaza ait {_tutar()} TL tutarında emlak vergisi ve çevre temizlik vergisi borcu bulunmaktadır. Bu borcun {_tarih()} tarihine kadar ödenmemesi durumunda yasal icra takibi başlatılacaktır.

Borcunuzu taksit seçenekleriyle veya peşin ödeyerek kapatabilirsiniz. Ödeme yaparak icra sürecini durdurmak için aşağıdaki belediye ödeme portalına erişebilirsiniz.

Belediye Ödeme Portalı: {_link()}

Saygılarımızla,
{_sehir()} Büyükşehir Belediyesi Tahsilat Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Trafik ceza kayıtlarınız incelenmiş ve plakasına kayıtlı araç üzerinden toplamda {_tutar()} TL tutarında ödenmemiş trafik para cezası bulunduğu tespit edilmiştir. Cezaların belirlenen son ödeme tarihine kadar ödenmemesi durumunda ehliyet ve araç tescil işlemleriniz dondurulacaktır.

Cezaları indirimli ödeyebilmek için son ödeme tarihi olan {_tarih()} tarihinden önce aşağıdaki e-ödeme sistemini kullanmanızı öneririz.

e-Ödeme Sistemi: {_link()}

Saygılarımızla,
Emniyet Genel Müdürlüğü — Trafik Hizmetleri""",
]


# ── 10. SAHTE TATİL / SEYAHAT PAKETİ ────────────────────────

SAHTE_TATIL = [

    lambda: f"""{_unvan()} {_isim()},

Seyahat acentemizin erken rezervasyon kampanyası kapsamında {_sehir()} çıkışlı özel tatil paketi için davetiyeniz hazırlandı. Paket; uçak bileti, 7 gece konaklama ve tam pansiyon hizmeti dahil olup kişi başı yalnızca {_tutar()} TL'den başlamaktadır.

Bu avantajlı fiyattan yararlanmak için rezervasyonunuzu {_tarih()} tarihine kadar tamamlamanız ve {_tutar()} TL tutarında ön ödeme yapmanız gerekmektedir. Kontenjan son derece sınırlıdır.

Rezervasyon ve Ödeme Formu: {_link()}

Saygılarımızla,
Tatil Paketleri Rezervasyon Merkezi""",

    lambda: f"""{_unvan()} {_isim()},

Üye olduğunuz seyahat kulübü aracılığıyla kazandığınız {_tutar()} TL değerindeki tatil çeki {_tarih()} tarihinde kullanıma açılmıştır. Bu çekle Türkiye'nin önde gelen otel ve tatil köylerinde geçerli olan özel paketlere erişebilirsiniz.

Çekten yararlanmak için üyelik doğrulamanızı tamamlamanız ve tercih ettiğiniz tesis ile tarihleri sistemde belirlemeniz gerekmektedir. Çek {_tarih()} tarihine kadar geçerlidir.

Üyelik Doğrulama ve Rezervasyon: {_link()}

Saygılarımızla,
Seyahat Kulübü Üye Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Uçuş bilet ücretlerinizde beklenmedik bir fiyat artışı yaşanmadan önce rezervasyonunuzu tamamlamanızı önemle tavsiye ederiz. {_sehir()} - {random.choice(['Dubai', 'Londra', 'Amsterdam', 'Roma', 'Paris', 'Berlin'])} hattında {_tarih()} tarihli sefer için anlık fiyat {_tutar()} TL'dir ve bu fiyat yalnızca 24 saat geçerlidir.

Rezervasyonunuzu güvence altına almak için aşağıdaki ödeme formunu doldurmanız yeterlidir. Koltuk garantisi için kredi kartı bilgileriniz talep edilecektir.

Bilet Rezervasyon Formu: {_link()}

Saygılarımızla,
Uçuş Rezervasyon Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihli {random.choice(['Maldivler', 'Bali', 'Phuket', 'Santorini', 'Dubrovnik'])} seyahat paketiniz için ön başvurunuz alınmıştır. Pakette 5 yıldızlı otel konaklaması, transfer hizmetleri ve rehberlik dahildir.

Rezervasyonun kesinleşebilmesi için pasaport bilgilerinizin sisteme girilmesi ve {_tutar()} TL tutarındaki kaparo ödemesinin {_tarih()} tarihine kadar yapılması gerekmektedir.

Ödeme ve Rezervasyon Tamamlama: {_link()}

Saygılarımızla,
Premium Seyahat Danışmanlık Merkezi""",
]

# ── 11. SAHTE EĞİTİM / KURS ──────────────────────────────────

SAHTE_EGITIM = [

    lambda: f"""{_unvan()} {_isim()},

Profiliniz, online eğitim platformumuzun seçkin üye programına kabul için değerlendirilmiş ve uygun bulunmuştur. {random.choice(['Yapay Zeka', 'Veri Bilimi', 'Siber Güvenlik', 'Dijital Pazarlama', 'Blockchain'])} alanındaki sertifika programımıza katılarak kariyerinizi bir üst seviyeye taşıyabilirsiniz.

Program normalde {_tutar()} TL ücretle sunulmakta; ancak size özel {_tarih()} tarihine kadar geçerli %{_yuzde()} indirim tanımlanmıştır. Sertifika, uluslararası geçerliliğe sahip olup birçok kurumca tanınmaktadır.

Kayıt ve Ödeme Formu: {_link()}

Saygılarımızla,
Eğitim Platformu Kayıt Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_uni()} iş birliğiyle düzenlenen "{random.choice(['İleri Seviye Python', 'Makine Öğrenmesi Temelleri', 'Proje Yönetimi', 'Dijital Pazarlama'])}" sertifika programına kayıt için son günler yaklaşmaktadır. Program {_tarih()} tarihinde başlayacak olup yalnızca {random.randint(20, 50)} kontenjan mevcuttur.

Katılım ücreti {_tutar()} TL olup erken kayıt indirimi {_tarih()} tarihine kadar geçerlidir. Kayıt formunu doldurup ödemenizi tamamladığınızda ders materyalleri e-posta adresinize gönderilecektir.

Kayıt Formu ve Ödeme: {_link()}

Saygılarımızla,
Sertifika Programları Koordinatörlüğü""",

    lambda: f"""{_unvan()} {_isim()},

Yurt dışı burs programı başvuruları başlamıştır. {random.choice(['İngiltere', 'Almanya', 'Hollanda', 'İsveç', 'Kanada'])} üniversitelerinde lisans veya yüksek lisans eğitimi almak isteyen adaylar için {_tutar()} TL değerinde burs olanağı sunulmaktadır.

Başvuru sürecinde pasaport fotokopisi, not dökümanı ve motivasyon mektubu istenecektir. Ön başvuruyu tamamlamak için aşağıdaki formu doldurmanız yeterlidir; ardından değerlendirme ekibimiz sizinle iletişime geçecektir.

Burs Ön Başvuru Formu: {_link()}

Saygılarımızla,
Uluslararası Burs Danışmanlık Merkezi""",

    lambda: f"""{_unvan()} {_isim()},

Kariyer danışmanlarımızın hazırladığı değerlendirme sonucunda profilinizin {_pozisyon()} alanında hızlı ilerlemeye uygun olduğu belirlenmiştir. Size özel tasarlanan {random.randint(4, 12)} haftalık yoğun mentorluk programı ile sektördeki konumunuzu güçlendirebilirsiniz.

Program kapsamında bire bir mentorluk seansları, sektör ağı oluşturma etkinlikleri ve CV güncelleme desteği sunulmaktadır. İlk danışma görüşmesi tamamen ücretsizdir.

Ücretsiz Danışma Randevusu: {_link()}

Saygılarımızla,
Kariyer Gelişim Merkezi""",
]

# ── 12. SAHTE BAĞIŞ / YARDIM ─────────────────────────────────

SAHTE_BAGIS = [

    lambda: f"""{_unvan()} {_isim()},

{_sehir()} merkezli yardım vakfımız, deprem bölgelerindeki ailelere yönelik acil destek kampanyası başlatmıştır. Bağışlarınız doğrudan ihtiyaç sahiplerine ulaştırılmakta; her kuruşun hesabı şeffaf biçimde kamuoyuyla paylaşılmaktadır.

Bağışınızı güvenle iletmek için aşağıdaki kampanya sayfamızı ziyaret edebilirsiniz. Kredi kartı, havale veya EFT yoluyla dilediğiniz tutarda destek olabilirsiniz.

Bağış Kampanyası: {_link()}

Destekleriniz için şimdiden teşekkür ederiz.
{_sehir()} İnsani Yardım Vakfı""",

    lambda: f"""{_unvan()} {_isim()},

Çocuk hastaneleri için tıbbi cihaz bağış kampanyamız başladı. Toplanan bağışlar; {random.choice(['yoğun bakım ünitesi', 'çocuk onkoloji servisi', 'acil servis', 'nöroloji kliniği'])} için kritik öneme sahip tıbbi ekipman alımında kullanılacaktır.

Bağışınız, vergi indiriminden yararlanmanızı sağlayan yasal dekontla belgelenecektir. 100 TL ve üzeri bağışlar için teşekkür belgesi hazırlanmaktadır.

Bağış Sayfası: {_link()}

Saygılarımızla,
Sağlıkta Umut Derneği Bağış Koordinatörlüğü""",

    lambda: f"""{_unvan()} {_isim()},

Sokak hayvanlarının rehabilitasyonu ve sahiplendirilmesi için yürüttüğümüz proje {_tarih()} tarihi itibarıyla yeni döneme girmiştir. Barınaklarımızda {random.randint(50, 300)} hayvan bakım altında olup her ay {_tutar()} TL'lik temel ihtiyaç gideri ortaya çıkmaktadır.

Düzenli bağışçı olarak aylık {random.choice(['50', '100', '200', '500'])} TL ile proje ortağı olabilir ya da tek seferlik destek verebilirsiniz. Bağışçılarımız aylık hayvan sağlık raporlarına erişim hakkına sahiptir.

Bağışçı Portalı: {_link()}

Saygılarımızla,
Can Dostlar Derneği""",
]

# ── 13. SAHTE EMLAK ──────────────────────────────────────────

SAHTE_EMLAK = [

    lambda: f"""{_unvan()} {_isim()},

{_sehir()} bölgesinde geliştirilen konut projesinde yatırım fırsatı sunan sınırlı sayıda daire bulunmaktadır. Ön satış fiyatlarıyla sunulan bu daireler, bölgenin hızla gelişen yapısı sayesinde kısa sürede değer kazanması öngörülmektedir.

{_tutar()} TL kaparo ile tercih ettiğiniz daireyi rezerve etme imkânı bulunmaktadır. Proje detayları, kat planları ve fiyat listesine ulaşmak için aşağıdaki formu doldurmanızı rica ederiz.

Proje Tanıtım ve Rezervasyon Formu: {_link()}

Saygılarımızla,
Gayrimenkul Proje Satış Ofisi""",

    lambda: f"""{_unvan()} {_isim()},

Kira gelirinizi en üst düzeye taşımak isteyen yatırımcılara yönelik özel bir fırsat sunuyoruz. {_sehir()} merkezinde tam donanımlı, kiracısı hazır daireler {_tutar()} TL başlayan fiyatlarla satışa çıkmıştır.

Satın alma sürecinde tapu ve hukuki işlemleri ücretsiz olarak yönetiyoruz. İlk 6 ay kira geliri garantisi de sunduğumuz bu teklif için detaylı bilgi almak amacıyla aşağıdaki formu doldurabilirsiniz.

Yatırım Danışmanlık Formu: {_link()}

Saygılarımızla,
Gayrimenkul Yatırım Danışmanlığı""",

    lambda: f"""{_unvan()} {_isim()},

Mülk sahibi olma hedefinize ulaşmanıza yardımcı olmak için özel mortgage danışmanlığı hizmeti sunuyoruz. {_banka()} iş birliğiyle hazırlanan özel kredi paketinde {_tutar()} TL'ye kadar %{random.randint(1, 3)},{random.randint(10, 99)} sabit faizle konut kredisi kullanabilirsiniz.

Ön başvurunuzu tamamlamanız durumunda 48 saat içinde kesin onay alabilir ve ev satın alma sürecinizi başlatabilirsiniz. Aşağıdaki form üzerinden gelir ve mülk bilgilerinizi girerek ön değerlendirme yaptırabilirsiniz.

Mortgage Ön Başvuru Formu: {_link()}

Saygılarımızla,
Konut Finansmanı Danışmanlık Ekibi""",
]

# ── 14. SAHTE SAĞLIK / İLAÇ ──────────────────────────────────

SAHTE_SAGLIK = [

    lambda: f"""{_unvan()} {_isim()},

Online sağlık platformumuz kapsamında uzman doktorlarımız tarafından hazırlanan kişisel sağlık değerlendirmesi sonuçlarınız hazır. Genel sağlık durumunuza yönelik hazırlanan rapor ve öneriler aşağıdaki bağlantı üzerinden görüntülenebilmektedir.

Rapora erişmek için üyelik bilgilerinizle giriş yapmanız gerekmektedir. Raporunuzu inceleyerek önerilen takviye ve vitamin paketlerini platforma entegre eczanelerimizden temin edebilirsiniz.

Sağlık Raporuma Eriş: {_link()}

Saygılarımızla,
Online Sağlık Platformu""",

    lambda: f"""{_unvan()} {_isim()},

{random.choice(['Diyabet', 'Tansiyon', 'Kolesterol', 'Eklem'])} yönetimine yönelik yeni nesil takviye ürünümüz klinik testlerde başarılı sonuçlar vermiştir. {random.randint(3, 6)} ay düzenli kullanımda %{random.randint(60, 90)} oranında iyileşme rapor edilmiştir.

Ürünümüz şu an sınırlı tanıtım kampanyası kapsamında sunulmakta olup ilk kutunuzu yalnızca {_tutar()} TL'ye sipariş edebilirsiniz. Memnun kalmazsanız 30 gün içinde koşulsuz iade garantisi sunulmaktadır.

Sipariş Formu: {_link()}

Saygılarımızla,
Sağlık ve Wellness Ürünleri""",

    lambda: f"""{_unvan()} {_isim()},

Özel sağlık sigortanız kapsamında yaptırılan son check-up tetkiklerinizin sonuçları sisteme yüklenmiştir. Sonuçların bir kısmı referans değerlerinin dışında çıkmış olup ilgili uzman hekimle görüşme planlanması önerilmektedir.

Tetkik sonuçlarınıza erişmek ve online randevu oluşturmak için hasta portalına giriş yapmanızı rica ederiz. Portalda ayrıca ilaç ve takviye önerileriniz de yer almaktadır.

Hasta Portalı: {_link()}

Saygılarımızla,
Sağlık Yönetim Sistemi""",
]

# ── 15. SAHTE KREDİ / BORÇ ───────────────────────────────────

SAHTE_KREDI = [

    lambda: f"""{_unvan()} {_isim()},

Finansal geçmişiniz incelenmiş ve {_tutar()} TL tutarında hızlı bireysel kredi için ön onayınız verilmiştir. Kredi başvurunuzu bugün tamamlarsanız para {random.randint(1, 3)} iş günü içinde hesabınıza aktarılacaktır.

Başvuru sürecinde yalnızca kimlik fotokopiniz ve son 3 aylık banka ekstreniz yeterlidir. Faiz oranımız aylık %{random.randint(1, 3)},{random.randint(10, 99)} olup {random.randint(12, 60)} aya kadar esnek ödeme planı seçenekleri mevcuttur.

Kredi Başvuru Formu: {_link()}

Saygılarımızla,
Hızlı Kredi Çözümleri Birimi""",

    lambda: f"""{_unvan()} {_isim()},

{_banka()} bireysel bankacılık değerlendirme ekibi, profilinizi incelemiş ve size özel {_tutar()} TL limitli bireysel kredi kartı teklifini hazırlamıştır. Kart; yurt içi ve yurt dışı alışverişlerinizde %{_yuzde()} nakit iade avantajı sunmaktadır.

Tekliften yararlanmak için başvurunuzu {_tarih()} tarihine kadar tamamlamanız gerekmektedir. Kart onayı, fiziksel şubeye gitmenize gerek kalmadan dijital olarak gerçekleştirilmektedir.

Kart Başvuru Formu: {_link()}

Saygılarımızla,
{_banka()} Bireysel Bankacılık ve Kart Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Mevcut kredi borcunuzu tek bir düşük faizli kredide birleştirerek aylık taksit ödemelerinizi önemli ölçüde azaltabilirsiniz. Borç yapılandırma hizmetimiz kapsamında toplam {_tutar()} TL'ye kadar olan borcunuz %{random.randint(1, 2)},{random.randint(10, 99)} aylık faizle yeniden düzenlenebilir.

İşlem için yalnızca kimlik bilgileriniz ve mevcut kredi belgeleriniz yeterlidir. Ücretsiz danışmanlık görüşmesi için aşağıdaki formu doldurabilirsiniz.

Borç Yapılandırma Başvurusu: {_link()}

Saygılarımızla,
Finansal Danışmanlık ve Yapılandırma Birimi""",
]

# ── 16. SAHTE ARAÇ / OTOMOTİV ───────────────────────────────

SAHTE_ARAC = [

    lambda: f"""{_unvan()} {_isim()},

Sahibinden.com üzerinden incelediğiniz araç ilanı hâlâ satışta olup satıcı, belirli bir süre için fiyatı {_tutar()} TL olarak sabitlemek istediğini belirtmiştir. Bu fiyatı güvence altına almak için ön rezervasyon yapmanızı öneririz.

Aracı yerinde görmeden önce kaparo ödemesi yapılması zorunlu olmamakla birlikte ciddi alıcılar için öncelikli görüşme hakkı sunulabilmektedir. Araç fotoğrafları ve teknik belgeler aşağıdaki linkte paylaşılmıştır.

Araç Detayları ve Rezervasyon: {_link()}

Saygılarımızla,
Araç Satış ve Danışmanlık Platformu""",

    lambda: f"""{_unvan()} {_isim()},

Aracınıza ait {_tarih()} tarihli periyodik bakımının zamanının geldiğini hatırlatmak istiyoruz. Ayrıca son araç muayenesinde tespit edilen {random.choice(['fren balataları', 'ön süspansiyon', 'filtre seti', 'rot-balans'])} değişiminin yapılması önerilmiştir.

Yetkili servisimizde randevu oluşturarak bu işlemleri aynı seansta tamamlatabilirsiniz. Online randevu alanlara %{_yuzde()} işçilik indirimi uygulanmaktadır. Servis geçmişinize ve randevu formuna ulaşmak için aşağıdaki bağlantıyı kullanabilirsiniz.

Servis Randevusu: {_link()}

Saygılarımızla,
Yetkili Araç Servis Merkezi""",
]


# ═════════════════════════════════════════════════════════════
# NORMAL (HAM)  (label = 0)
# ═════════════════════════════════════════════════════════════

NORMAL = [

    # ── Sipariş onayı ────────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} üzerinden verdiğiniz siparişiniz başarıyla alınmış ve hazırlık sürecine girmiştir. Siparişiniz hazırlandıktan sonra anlaşmalı kargo firmamıza teslim edilecek ve takip bilgileri size iletilecektir.

Sipariş No: {_siparis_no()}
Ürün: {random.choice(['Kablosuz Kulaklık', 'Spor Ayakkabı', 'Laptop Çantası', 'Kitap Seti', 'Mutfak Robotu', 'Akıllı Saat'])}
Tahmini Teslimat: {_tarih()}
Toplam Tutar: {_tutar()} TL

Siparişinizi {_glink()} adresinden takip edebilirsiniz. Sorularınız için müşteri hizmetlerimiz 7/24 hizmetinizdedir.

İyi alışverişler dileriz.
{_marka()} Müşteri Hizmetleri""",

    # ── Kargo teslim edildi ──────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_siparis_no()} numaralı siparişiniz {_tarih()} tarihinde teslimat adresinize başarıyla ulaştırılmıştır. Kargonuzu teslim alan kişi: {random.choice(['Alıcının kendisi', 'Kapı komşusu', 'Güvenlik görevlisi'])}.

Kargo Firması: {_kargo()}
Takip No: {_kargo_no()}

Ürününüzden memnun kalmadığınız bir durum söz konusuysa {_glink()} adresinden 14 gün içinde iade talebinde bulunabilirsiniz. Deneyiminizi puanlamanız bizim için büyük değer taşımaktadır.

İyi kullanımlar dileriz.
{_marka()} Müşteri Hizmetleri""",

    # ── Banka ekstre ─────────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} dönemi hesap ekstreniz hazırlanmıştır. Ekstrenizde bu döneme ait tüm işlem kayıtları yer almaktadır.

Hesap No: **** {random.randint(1000, 9999)}
Dönem: {_tarih()} - {_tarih()}
Toplam İşlem: {random.randint(5, 30)}
Kapanış Bakiyesi: {_tutar()} TL

Ekstrenizi {_glink()} adresi üzerinden görüntüleyebilir ve PDF olarak indirebilirsiniz. Hesabınıza ilişkin sorularınız için müşteri hizmetlerimizle iletişime geçebilirsiniz.

Saygılarımızla,
{_banka()} Dijital Bankacılık Hizmetleri""",

    # ── Fatura ödeme onayı ───────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde gerçekleştirdiğiniz {_tutar()} TL tutarındaki ödeme başarıyla işlenmiştir. Ödemenize ait bilgiler aşağıda yer almaktadır.

İşlem Tarihi: {_tarih()}
Referans No: {_kargo_no()}
Ödenen Tutar: {_tutar()} TL
Ödeme Yöntemi: {random.choice(['Kredi Kartı', 'EFT', 'Havale', 'Online Bankacılık'])}

Ödemeniz için teşekkür ederiz. Herhangi bir sorunuz bulunması halinde {_glink()} adresinden veya müşteri hizmetlerimiz aracılığıyla bize ulaşabilirsiniz.

Saygılarımızla,
{_banka()} Ödeme Hizmetleri""",

    # ── Operatör fatura ──────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_operator()} olarak {_tarih()} dönemi faturanızın hazır olduğunu bildirmek isteriz. Faturanızı dijital kanallarımız üzerinden görüntüleyebilir ve ödeme yapabilirsiniz.

Fatura Dönemi: {_tarih()}
Fatura Tutarı: {random.choice(['89,90', '129,90', '149,90', '199,90', '249,90'])} TL
Son Ödeme Tarihi: {_tarih()}
Otomatik Ödeme: {random.choice(['Aktif', 'Pasif'])}

Faturanızı {_glink()} adresinden, mobil uygulamamızdan veya en yakın satış noktamızdan ödeyebilirsiniz.

Saygılarımızla,
{_operator()} Müşteri Hizmetleri""",

    # ── Toplantı daveti ──────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde saat {_saat()}'de gerçekleştirilecek {random.choice(['proje değerlendirme', 'aylık durum raporu', 'bütçe planlama', 'strateji geliştirme'])} toplantısına davetlisiniz. Toplantıya katılımınız büyük önem taşımaktadır.

Platform: {random.choice(['Zoom', 'Microsoft Teams', 'Google Meet'])}
Gündem: {random.choice(['Q3 sonuçlarının değerlendirilmesi', 'Yeni ürün lansmanı planlaması', 'Müşteri geri bildirim analizi', 'Süreç iyileştirme önerileri'])}
Tahmini Süre: {random.randint(1, 2)} saat

Toplantıya katılacaksanız en geç {_tarih()} tarihine kadar onayınızı bu e-postayı yanıtlayarak iletmenizi rica ederiz.

Saygılarımızla,
{random.choice(ISIMLER)}
{random.choice(['Proje Koordinatörü', 'Departman Müdürü', 'İş Geliştirme Sorumlusu'])}""",

    # ── İş başvurusu yanıtı ──────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_pozisyon()} pozisyonuna ilettiğiniz başvuruyu aldık ve ilginiz için teşekkür ederiz. Başvurunuz İnsan Kaynakları ekibimiz tarafından titizlikle değerlendirilmektedir.

Değerlendirme süreci yaklaşık {random.randint(1, 3)} hafta sürmekte olup sonuç hakkında en kısa sürede bilgilendirileceksiniz. Bu süreç içinde başvurunuzu {_glink()} adresinden takip edebilirsiniz.

Portföy veya referans mektuplarınızı da aynı platform üzerinden yükleyebilirsiniz. Sorularınız için bu e-postayı yanıtlayabilirsiniz.

Başarılar dileriz.
İnsan Kaynakları Departmanı""",

    # ── Etkinlik bileti ──────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Satın aldığınız etkinlik biletiniz onaylanmıştır. Keyifli bir etkinlik geçirmenizi dileriz.

Etkinlik: {random.choice(['Rock Konseri', 'Caz Festivali', 'Tiyatro Oyunu', 'Stand-Up Gösterisi'])}
Tarih: {_tarih()} — Saat: {_saat()}
Mekan: {_sehir()} {random.choice(['Açık Hava Amfitiyatrosu', 'Kongre Merkezi', 'Kültür Merkezi', 'Arena'])}
Koltuk: Bölge {random.randint(1, 10)} / Sıra {random.randint(1, 30)} / No {random.randint(1, 50)}
Bilet No: {_kargo_no()}

Biletinizi {_glink()} adresinden de görüntüleyebilirsiniz. Lütfen etkinliğe 20 dakika önceden kapıda bulunun.

Saygılarımızla,
Bilet Hizmetleri""",

    # ── Okul veli bildirimi ──────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde saat {_saat()}'de okulumuzda veli toplantısı düzenlenmektedir. Toplantıda çocuğunuzun akademik gelişimi, dönem sonu notları ve bir sonraki dönem planları paylaşılacaktır.

Her veli için yaklaşık 10-15 dakika görüşme süresi ayrılmıştır. Toplantı gündemine dahil edilmesini istediğiniz özel bir konu varsa önceden okul sekreterliğimizi bilgilendirmenizi öneririz.

Katılım onayı için {_glink()} adresini veya okul sekreterliğimizi kullanabilirsiniz.

Saygılarımızla,
Okul Müdürlüğü""",

    # ── Üniversite ders duyurusu ─────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_ders()} dersiyle ilgili ara sınav ve ödev teslim tarihleri hakkında önemli bilgileri paylaşmak istiyorum.

Ara Sınav: {_tarih()} — Saat {_saat()} - {_saat()}
Sınav Kapsamı: İlk 6 haftalık konular (çoktan seçmeli + açık uçlu)

Ödev Teslimi: {_tarih()} tarihine kadar öğrenci bilgi sistemi üzerinden yapılmalıdır. Geç teslimler %20 puan kesintisiyle değerlendirilecektir.

Ders notları ve güncel duyurular için {_glink()} adresini düzenli olarak kontrol etmenizi öneririm.

Başarılar,
{random.choice(ISIMLER)}, Öğretim Görevlisi — {_uni()}""",

    # ── Rezervasyon onayı ────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Gerçekleştirdiğiniz rezervasyon başarıyla onaylanmıştır. Aşağıda rezervasyon detaylarınızı bulabilirsiniz.

Rezervasyon No: {_kargo_no()}
Tesis: {random.choice(['Sheraton', 'Hilton', 'Marriott', 'Divan', 'Ramada'])} {_sehir()}
Giriş: {_tarih()} — Çıkış: {_tarih()}
Oda Tipi: {random.choice(['Standart Oda', 'Deluxe Oda', 'Süit', 'Deniz Manzaralı Oda'])}
Kişi Sayısı: {random.randint(1, 4)}

İptal veya değişiklik için giriş tarihinden 48 saat önce {_glink()} üzerinden işlem yapmanızı öneririz. İyi tatiller dileriz.

Saygılarımızla,
Rezervasyon Hizmetleri""",

    # ── Burs bildirimi ───────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_uni()} Burs Komisyonu değerlendirme süreci tamamlanmış olup akademik başarı ve sosyoekonomik kriter değerlendirmesi sonucunda burs almaya hak kazandığınız belirlenmiştir.

Burs Türü: {random.choice(['Kısmi Burs', 'Tam Burs', 'Yüksek Başarı Bursu'])}
Dönem: {_tarih()} - {_tarih()}
Aylık Tutar: {_tutar()} TL

Bursunuzu onaylamak ve banka bilgilerinizi sisteme işlemek için öğrenci işleri ofisine {_tarih()} tarihine kadar başvurmanız gerekmektedir. Gerekli belgeler için {_glink()} adresini ziyaret edin.

Başarılarınızın devamını dileriz.
{_uni()} Burs ve Öğrenci Hizmetleri""",

    # ── Seminer daveti ───────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde {_sehir()}'de düzenlenecek "{random.choice(['Yapay Zeka ve İş Dünyası', 'Dijital Dönüşüm Zirvesi', 'Siber Güvenlik Konferansı', 'Veri Bilimi Buluşması', 'Girişimcilik Forumu'])}" etkinliğine katılım davetiyeniz hazır.

Etkinlik kapsamında sektör liderlerinin keynote konuşmaları, panel tartışmaları ve networking etkinlikleri yer alacaktır. Kayıt ücretsiz olmakla birlikte katılım için ön kayıt zorunludur; kontenjan sınırlıdır.

Kayıt ve program için {_glink()} adresini ziyaret edebilirsiniz.

Görüşmek dileğiyle,
Organizasyon Komitesi""",

    # ── Elektrik / doğalgaz fatura ───────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} dönemine ait {random.choice(['elektrik', 'doğalgaz', 'su'])} faturanız oluşturulmuştur.

Abonelik No: {_kargo_no()}
Fatura Dönemi: {_tarih()} - {_tarih()}
Tüketim: {random.randint(80, 600)} {random.choice(['kWh', 'm³'])}
Fatura Tutarı: {_tutar()} TL
Son Ödeme Tarihi: {_tarih()}

Faturanızı {_glink()} adresinden, yetkili ödeme noktalarından veya bankanızın ödeme kanallarından ödeyebilirsiniz.

Saygılarımızla,
Dağıtım Hizmetleri Müşteri Birimi""",

    # ── Kariyer / iş ilanı ───────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Profilinizle uyumlu yeni iş ilanları sisteme eklenmiştir. Bu fırsatları değerlendirmenizi öneririz.

Önerilen İlanlar:
— {_pozisyon()} / {_sehir()} / Tam Zamanlı
— {_pozisyon()} / Uzaktan veya Hibrit
— {_pozisyon()} / {_sehir()} / Sözleşmeli

Başvurmak için özgeçmişinizin güncel olduğundan emin olun ve {_glink()} adresini ziyaret edin. Güncel profil, görünürlüğünüzü önemli ölçüde artıracaktır.

Başarılar dileriz.
Kariyer Platformu Öneri Sistemi""",

    # ── Sağlık randevusu ─────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde planlanan randevunuzu hatırlatmak istiyoruz.

Doktor: {random.choice(['Dr.', 'Prof. Dr.', 'Uzm. Dr.'])} {random.choice(ISIMLER)}
Branş: {random.choice(['Dahiliye', 'Kardiyoloji', 'Ortopedi', 'Göz Hastalıkları', 'Nöroloji'])}
Saat: {_saat()}
Kurum: {random.choice(['Şehir Hastanesi', 'Özel Klinik', 'Tıp Merkezi'])} — {_sehir()}

Kimlik belgenizi, sigorta kartınızı ve varsa önceki tetkik sonuçlarınızı yanınızda getirmenizi rica ederiz. Randevu iptal ya da değişiklik taleplerinizi en az 24 saat önce iletmenizi öneririz.

Saygılarımızla,
Hasta Hizmetleri Koordinatörlüğü""",

    # ── Abonelik yenileme ────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{random.choice(['Spotify', 'YouTube Premium', 'iCloud', 'Microsoft 365', 'Adobe Creative Cloud'])} aboneliğiniz {_tarih()} tarihinde otomatik olarak yenilenecektir.

Plan: {random.choice(['Bireysel', 'Aile', 'Öğrenci'])}
Yenileme Tutarı: {random.choice(['29,99', '49,99', '79,99', '119,99', '189,99'])} TL/ay
Ödeme: Kayıtlı kart

Aboneliğinizi yönetmek, planınızı değiştirmek veya iptal etmek için {_glink()} adresindeki hesap ayarlarınızı kullanabilirsiniz. İptal işlemini yenileme tarihinden en az 24 saat önce yapmanız gerekmektedir.

Saygılarımızla,
Abonelik Yönetim Ekibi""",

    # ── Maaş bordro bildirimi ────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} dönemine ait maaş bordronuz İnsan Kaynakları sistemine yüklenmiştir. Bordronuzu incelemek ve PDF olarak indirmek için kurumsal portala giriş yapabilirsiniz.

Ödeme Tarihi: {_tarih()}
Net Tutar: {_tutar()} TL
Ödeme Kanalı: Banka Havalesi

Bordronuzda herhangi bir hata ya da eksiklik tespit etmeniz durumunda {_tarih()} tarihine kadar muhasebe departmanına bildirimde bulunmanızı öneririz. Detaylar için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
İnsan Kaynakları ve Bordro Servisi""",

    # ── İade onayı ───────────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_siparis_no()} numaralı siparişe ait iade talebiniz onaylanmıştır. İade süreci aşağıdaki takvimde ilerleyecektir.

İade Edilen Ürün: {random.choice(['Spor Ayakkabı', 'Gömlek', 'Çanta', 'Elektronik Aksesuar'])}
İade Nedeni: {random.choice(['Beden uyumsuzluğu', 'Ürün hasarlı', 'Yanlış ürün', 'Fikir değişikliği'])}
İade Tutarı: {_tutar()} TL
Tahmini Süre: {random.randint(3, 10)} iş günü

İade tutarı onaylanan ödeme yönteminize aktarılacaktır. Süreç hakkında {_glink()} adresinden güncel bilgiye ulaşabilirsiniz.

Saygılarımızla,
{_marka()} İade Hizmetleri""",

    # ── İndirim kampanyası ───────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} mevsimlik indirim kampanyası başladı. Seçili ürün kategorilerinde cazip fırsatlar sizi bekliyor.

— {_urun_kat()}: %{_yuzde()} indirim
— {_urun_kat()}: %{_yuzde()} indirim
— {_urun_kat()}: %{_yuzde()} indirim

Kampanya {_tarih()} tarihine kadar geçerli olup stoklar sınırlıdır. Tüm fırsatlar için {_glink()} adresini ziyaret edebilirsiniz. Mobil uygulamadan alışveriş yapanlara ek %{random.randint(5, 10)} indirim uygulanmaktadır.

İyi alışverişler dileriz.
{_marka()} Kampanya Ekibi""",

    # ── Uçuş / seyahat onayı ────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Uçuş rezervasyonunuz onaylanmıştır. Yolculuğunuzun keyifli geçmesini dileriz.

Sefer No: TK{random.randint(100, 999)}
Kalkış: {_sehir()} — {_tarih()} — {_saat()}
Varış: {random.choice(['İstanbul', 'Ankara', 'İzmir', 'Antalya', 'Londra', 'Berlin', 'Dubai'])}
Koltuk: {random.choice(['12A', '23B', '7C', '34D', '15F'])}
Rezervasyon Kodu: {_kargo_no()[:6].upper()}

Uçuşa en az 2 saat önce havalimanında bulunmanızı öneririz. Online check-in için {_glink()} adresini veya mobil uygulamamızı kullanabilirsiniz.

Saygılarımızla,
Havayolu Müşteri Hizmetleri""",

    # ── Şirket içi duyuru ────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Bilgi güvenliği politikamız gereği tüm çalışanların kurumsal hesap parolalarını {_tarih()} tarihine kadar güncellemeleri gerekmektedir. Bu zorunluluk, son dönemde artan siber saldırı vakalarına karşı alınan bir önlem olarak hayata geçirilmiştir.

Yeni parola gereksinimleri: En az 12 karakter, büyük-küçük harf kombinasyonu ve en az bir özel karakter. Aynı parolanın birden fazla sistemde kullanılmaması da önemle tavsiye edilmektedir.

Parola güncelleme için kurumsal portala {_glink()} üzerinden giriş yapabilirsiniz.

Saygılarımızla,
Bilgi İşlem Departmanı""",

    # ── Proje güncelleme bildirimi ───────────────────────────
    lambda: f"""{_unvan()} {_isim()},

"{random.choice(['Dijital Dönüşüm', 'Yeni Platform Geliştirme', 'Müşteri Deneyimi İyileştirme', 'ERP Entegrasyon'])} Projesi" kapsamındaki {_tarih()} haftası ilerleme raporu hazırlanmıştır.

Bu hafta tamamlanan başlıca görevler:
— {random.choice(['Gereksinimlerin belirlenmesi', 'Kullanıcı testlerinin tamamlanması', 'API entegrasyonunun yapılması', 'UAT sürecinin başlatılması'])}
— {random.choice(['Teknik dokümantasyon güncellendi', 'Paydaş geri bildirimleri alındı', 'Sprint retrospektifi yapıldı'])}

Bir sonraki sprint hedefleri ve detaylı rapor için {_glink()} adresini inceleyebilirsiniz. Sorularınız ve katkılarınız için bu e-postayı yanıtlayabilirsiniz.

Saygılarımızla,
{random.choice(ISIMLER)}
Proje Yöneticisi""",

    # ── Müşteri anket daveti (gerçek) ────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} olarak müşteri memnuniyetini sürekli iyileştirme amacıyla gerçekleştirdiğimiz dönemsel anket çalışmamıza katılmanızı rica ediyoruz. Geri bildirimleriniz ürün ve hizmet kalitemiz için büyük önem taşımaktadır.

Anket yalnızca 3-5 dakika sürmektedir. Katılımcılar arasından çekilişle belirlenecek 10 kişiye {_marka()} hediye çeki kazandırılacaktır.

Ankete Katıl: {_glink()}

Değerli zamanınız için şimdiden teşekkür ederiz.

Saygılarımızla,
{_marka()} Müşteri Deneyimi Ekibi""",

    # ── Teknik destek bildirimi ──────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde açtığınız destek talebiniz (Talep No: {_kargo_no()}) incelemeye alınmıştır. Ekibimiz en kısa sürede çözüm sağlamak için çalışmaktadır.

Talebinize ait ön değerlendirme bilgileri:
Konu: {random.choice(['Bağlantı sorunu', 'Hesap erişim problemi', 'Ödeme işlemi hatası', 'Ürün iade talebi'])}
Öncelik: {random.choice(['Normal', 'Yüksek'])}
Tahmini Çözüm Süresi: {random.randint(1, 5)} iş günü

Talebinizin güncel durumunu {_glink()} adresinden takip edebilirsiniz. Ek bilgi gerekirse sizinle iletişime geçeceğiz.

Saygılarımızla,
Teknik Destek Ekibi""",

    # ── Sigorta poliçe yenileme (gerçek) ────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_sigorta()} poliçeniz {_tarih()} tarihinde yenilenecektir. Poliçe koşullarınız ve prim tutarınız hakkında önceden bilgilendirmek istedik.

Poliçe No: {_kargo_no()}
Poliçe Türü: {_sigorta()}
Yeni Dönem: {_tarih()} - {_tarih()}
Yıllık Prim: {_tutar()} TL

Poliçe detaylarını incelemek, teminat kapsamını güncellemek veya teklif karşılaştırması yapmak için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
Sigorta Müşteri Hizmetleri""",

    # ── Staj teklifi ─────────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_uni()} kariyer merkeziyle iş birliği çerçevesinde {_marka()} olarak bu dönem stajyer alımı yapıyoruz. {_pozisyon()} departmanımızda {random.randint(2, 6)} aylık ücretli staj fırsatı sunulmaktadır.

Stajyerlerimize gerçek proje deneyimi kazandırmayı, mentorluk desteği sağlamayı ve başarılı adaylar için tam zamanlı iş teklifinde bulunmayı hedefliyoruz. Başvurunuzu {_tarih()} tarihine kadar iletmenizi rica ederiz.

Başvuru ve Detaylı Bilgi: {_glink()}

Saygılarımızla,
{_marka()} İnsan Kaynakları ve Yetenek Geliştirme Ekibi""",

    # ── Banka kredi limiti artışı (gerçek) ───────────────────
    lambda: f"""{_unvan()} {_isim()},

Hesap kullanım geçmişiniz ve kredi notunuz değerlendirilmiş; kredi kartı limitinizin {_tutar()} TL olarak güncellenmesi uygun görülmüştür. Limit artışı {_tarih()} tarihi itibarıyla otomatik olarak uygulanacaktır.

Yeni limitiniz, anlık bildirim gönderen mobil uygulamamız üzerinden takip edilebilir. Limit artışını kabul etmek ya da mevcut limitinizi korumak için {_glink()} adresindeki kart yönetim panelinizi kullanabilirsiniz.

Saygılarımızla,
{_banka()} Kart Hizmetleri""",

    # ── Dernek / vakıf duyurusu ──────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_sehir()} {random.choice(['Girişimcilik', 'Teknoloji', 'Çevre', 'Eğitim', 'Kültür-Sanat'])} Derneği olarak {_tarih()} tarihinde düzenleyeceğimiz genel kurul toplantısına davetlisiniz. Toplantıda {random.choice(['yönetim kurulu seçimi', 'yıllık faaliyet raporu', 'bütçe planlaması', 'yeni proje teklifleri'])} gündeme alınacaktır.

Toplantıya katılabilmek için {_tarih()} tarihine kadar dernek sekreteryasına bildirimde bulunmanızı ve üyelik aidatınızı tamamlamanızı rica ederiz. Toplantıya katılamayacaksanız vekaletnamenizi iletebilirsiniz.

Toplantı yeri ve saati hakkında detaylı bilgiye {_glink()} adresinden ulaşabilirsiniz.

Saygılarımızla,
{_sehir()} Derneği Yönetim Kurulu""",

    # ── Ürün geri çağırma bildirimi ──────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} olarak müşteri güvenliğini her şeyin önünde tutuyoruz. Yaptığımız iç kalite denetimi sonucunda {_tarih()} - {_tarih()} tarihleri arasında üretilen belirli seri numaralı ürünlerde potansiyel bir güvenlik riski tespit edilmiştir.

Bu nedenle söz konusu ürünü {_siparis_no()} numaralı siparişinizle satın almış olmanız durumunda, ürünü kullanmayı durdurmanızı ve aşağıdaki geri çağırma prosedürünü başlatmanızı önemle rica ederiz. Tüm giderler tarafımızca karşılanacak ve ürün değişimi veya iadesi sağlanacaktır.

Geri Çağırma Başvurusu: {_glink()}

Saygılarımızla,
{_marka()} Kalite ve Müşteri Güvenliği Birimi""",

    # ── Kütüphane kitap iade hatırlatma (gerçek) ─────────────
    lambda: f"""{_unvan()} {_isim()},

{_uni()} Kütüphane Hizmetleri olarak, ödünç aldığınız yayınların iade tarihini hatırlatmak istiyoruz.

İade Tarihi: {_tarih()}
Ödünç Alınan Eser Sayısı: {random.randint(1, 4)}
Günlük Gecikme Ücreti: {random.choice(['1,00', '1,50', '2,00'])} TL / eser

Eserleri zamanında iade edemeyecekseniz {_glink()} üzerinden veya kütüphane hizmet masasında süre uzatma işlemi yaptırabilirsiniz. Başka bir üye tarafından rezerve edilmiş eserler için süre uzatma yapılamamaktadır.

Saygılarımızla,
{_uni()} Kütüphane Hizmetleri""",

    # ── Akademik yayın / makale kabulü ───────────────────────
    lambda: f"""{_unvan()} {_isim()},

Dergimize gönderdiğiniz "{random.choice(['Makine Öğrenmesi ile Spam Tespiti', 'Derin Öğrenme Tabanlı NLP Uygulamaları', 'Siber Güvenlikte Anomali Tespiti', 'Büyük Veri Analizi Yöntemleri'])}" başlıklı makaleniz hakem değerlendirme sürecini tamamlamıştır.

Hakem görüşleri doğrultusunda makalenizde küçük revizyonlar yapılması talep edilmektedir. Revize edilmiş sürümü {_tarih()} tarihine kadar sistemimize yüklemenizi bekliyoruz. Hakem raporlarına {_glink()} üzerinden erişebilirsiniz.

Başarılar dileriz.
{random.choice(['Bilişim Teknolojileri', 'Mühendislik Bilimleri', 'Sosyal Bilimler'])} Dergisi — Editörler Kurulu""",

    # ── Şikayet yanıtı ────────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde ilettiğiniz şikayet ve öneriniz (Referans No: {_kargo_no()}) tarafımızca incelenmiştir. Yaşadığınız olumsuz deneyim için özür diler, anlayışınıza teşekkür ederiz.

Şikayetiniz: {random.choice(['Geç teslimat', 'Hasarlı ürün', 'Müşteri hizmetleri iletişim sorunu', 'Yanlış ürün gönderimi'])}
Çözüm: {random.choice(['Yeni ürün gönderildi', 'Tam iade yapıldı', 'İlgili birim uyarıldı', 'Kargo firmasıyla görüşme yapıldı'])}

Sizi daha iyi hizmet etmek için geri bildiriminiz büyük değer taşımaktadır. Deneyiminizi {_glink()} üzerinden puanlayabilirsiniz.

Saygılarımızla,
{_marka()} Müşteri Deneyimi ve Kalite Birimi""",

    # ── İhale / tedarikçi bildirimi ──────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Şirketimiz, {_tarih()} tarihinde tamamlanması planlanan {random.choice(['ofis malzemesi temini', 'IT altyapı yenileme', 'yazılım lisanslama', 'lojistik hizmet'])} ihalesi için teklif almaktadır. Tedarikçi havuzumuza kayıtlı firmanızın bu ihaleye katılımını değerlendirmenizi rica ederiz.

İhale şartnamesi ve teknik dokümanlar {_glink()} adresinden indirilebilir. Teklif zarflarının {_tarih()} saat {_saat()}'ye kadar teslim edilmesi gerekmektedir. Geç teslim edilen teklifler değerlendirmeye alınmayacaktır.

Saygılarımızla,
Satın Alma ve Tedarik Müdürlüğü""",

    # ── Konut / kira sözleşmesi (gerçek) ────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde başlayan kira sözleşmeniz kapsamında {_tarih()} ayı kira ödemesini hatırlatmak istiyoruz.

Kira Tutarı: {_tutar()} TL
Ödeme Son Tarihi: {_tarih()}
IBAN: TR{_kargo_no()}{_kargo_no()[:4]}

Ödemenizi gerçekleştirdikten sonra dekontunuzu bu e-postayı yanıtlayarak iletebilirsiniz. Kira sözleşmesi ve diğer belgelerinize {_glink()} üzerinden erişebilirsiniz.

Saygılarımızla,
{random.choice(ISIMLER)} — Mülk Sahibi""",

    # ── Uçuş / seyahat onayı ────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Rezervasyonunuz onaylanmıştır. Seyahat detaylarınız aşağıda yer almaktadır.

Sefer: TK{random.randint(100,999)} | {_sehir()} → {random.choice(['İstanbul', 'Ankara', 'Londra', 'Dubai', 'Amsterdam'])}
Tarih: {_tarih()} — Kalkış: {_saat()}
Koltuk: {random.choice(['12A', '23B', '7C', '34D', '15F'])} | Sınıf: {random.choice(['Ekonomi', 'Business'])}
Rezervasyon Kodu: {_kargo_no()[:6].upper()}

Online check-in için {_glink()} adresini veya mobil uygulamamızı kullanabilirsiniz. Havalimanında en az 2 saat önce bulunmanızı öneririz. Keyifli uçuşlar dileriz.

Saygılarımızla,
Havayolu Müşteri Hizmetleri""",

    # ── Yeni işe alım hoş geldin ─────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} ailesine katıldığınız için hepimiz adına hoş geldiniz. {_tarih()} tarihi itibarıyla {_pozisyon()} rolünde göreviniz resmî olarak başlayacaktır.

İlk gününüze hazırlıklı gelebilmeniz için bazı önemli bilgileri paylaşmak istiyoruz. Kurumsal e-posta hesabınız, erişim kartınız ve bilgisayar kurulumunuz hazır olacaktır. İlk hafta boyunca bir mentor size eşlik edecektir.

İnsan kaynakları sisteminize {_glink()} adresinden erişebilirsiniz. Sorularınız için doğrudan bize yazabilirsiniz.

Saygılarımızla,
{_marka()} İnsan Kaynakları Departmanı""",

    # ── İzin / tatil onayı ───────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} - {_tarih()} tarihleri arasında talep ettiğiniz {random.randint(3, 14)} günlük yıllık izin talebiniz onaylanmıştır. İzin sürenizde işlerinizi teslim alacak kişi {random.choice(ISIMLER)} olacaktır.

İzne çıkmadan önce devam eden görevlerinizi ilgili arkadaşınıza devretmenizi ve yöneticinizi bilgilendirmenizi rica ederiz. İzin belgenize {_glink()} üzerindeki İK portalından erişebilirsiniz.

Saygılarımızla,
İnsan Kaynakları Departmanı""",

    # ── Vergi beyannamesi hatırlatma (gerçek) ────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} dönemi {random.choice(['gelir vergisi', 'kurumlar vergisi', 'KDV', 'geçici vergi'])} beyannamesinin verilmesi için son tarih {_tarih()}'dir. Beyannameyi zamanında vermemeniz durumunda usulsüzlük cezası uygulanabilir.

Beyannamenizi {_glink()} üzerindeki e-Beyanname sistemine giriş yaparak veya mali müşaviriniz aracılığıyla iletebilirsiniz. Beyan ve ödeme süreçlerine ilişkin sorularınız için vergi dairenizle iletişime geçebilirsiniz.

Saygılarımızla,
Gelir İdaresi Başkanlığı — Mükellef Hizmetleri""",

    # ── Okul not / transkript bildirimi ──────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihi itibarıyla {random.choice(['birinci dönem', 'ikinci dönem', 'yıl sonu'])} not değerlendirmeleri sisteme işlenmiştir. Öğrencimizin bu döneme ait akademik performansını aşağıda özetlemekteyiz.

Genel Not Ortalaması: {random.choice(['3.20', '3.45', '2.87', '3.78', '2.65'])}/4.00
Devam Durumu: %{random.randint(80, 100)}
Davranış Değerlendirmesi: {random.choice(['Çok İyi', 'İyi', 'Geliştirilmeli'])}

Transkript ve detaylı not dökümüne {_glink()} üzerinden ulaşabilirsiniz. Notlara itiraz için {_tarih()} tarihine kadar sınıf öğretmeniyle iletişime geçilmesi gerekmektedir.

Saygılarımızla,
Okul Öğrenci İşleri""",

    # ── Toplantı tutanağı ────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde gerçekleştirilen {random.choice(['proje değerlendirme', 'yönetim kurulu', 'departman', 'bütçe planlama'])} toplantısının tutanağı hazırlanmıştır. Toplantıya katılan tüm paydaşlarla paylaşılmak üzere bu e-posta iletilmektedir.

Toplantıda alınan kararlar ve aksiyon planları özet olarak tutanakta yer almaktadır. Tutanak metninde hata veya eksiklik tespit etmeniz durumunda {_tarih()} tarihine kadar bu e-postayı yanıtlayarak bildirimde bulunabilirsiniz.

Toplantı tutanağına {_glink()} adresinden erişebilirsiniz.

Saygılarımızla,
{random.choice(ISIMLER)} — Toplantı Sekreteri""",

    # ── Fatura itiraz onayı ───────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde ilettiğiniz fatura itirazınız (Referans No: {_kargo_no()}) incelemeye alınmıştır. {_tutar()} TL tutarındaki hatalı ücretin tarafınıza iade edilmesi uygun görülmüştür.

İade işlemi {random.randint(3, 10)} iş günü içinde kayıtlı ödeme yönteminize yansıtılacaktır. İtiraz sürecine ilişkin detaylı bilgiye {_glink()} üzerinden ulaşabilirsiniz.

İtirazınızı değerlendirdiğimiz için teşekkür ederiz. Hizmet kalitemizi artırmamıza katkı sağladınız.

Saygılarımızla,
Fatura İtiraz ve Çözüm Birimi""",

    # ── Kongre / workshop daveti ─────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} - {_tarih()} tarihleri arasında {_sehir()}'de düzenlenecek {random.choice(['"Ulusal Bilgisayar Mühendisliği Sempozyumu"', '"Yönetim Bilişim Sistemleri Konferansı"', '"Siber Güvenlik Zirvesi"', '"Veri Analitiği ve YZ Kongresi"'])} etkinliğine bildiri sunmak veya dinleyici olarak katılmak için davet edildiniz.

Etkinlik kapsamında {random.randint(2, 5)} gün boyunca paralel oturumlar, atölye çalışmaları ve akademisyenlerle birebir ağ oluşturma fırsatları sunulacaktır. Erken kayıt ücreti {_tarih()} tarihine kadar geçerlidir.

Kayıt ve Program Bilgisi: {_glink()}

Saygılarımızla,
Organizasyon Komitesi""",

    # ── Genel kurul daveti (gerçek) ──────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_isim()} A.Ş. / Ltd. Şti. {_tarih()} tarihli Olağan Genel Kurul Toplantısı'na ortak / hissedar sıfatıyla davetlisiniz. Toplantı {_sehir()} adresindeki şirket merkezinde saat {_saat()}'de gerçekleştirilecektir.

Toplantı gündeminde yönetim kurulu faaliyet raporu, bilanço onayı, kâr dağıtımı ve yeni dönem bütçesi görüşülecektir. Toplantıya bizzat katılamayanlar için vekaleten temsil imkânı mevcuttur.

Vekâletname formu ve gündem detayları için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
Yönetim Kurulu Başkanlığı""",

    # ── Sosyal yardım başvuru sonucu (gerçek) ────────────────
    lambda: f"""{_unvan()} {_isim()},

{_sehir()} Sosyal Yardımlaşma ve Dayanışma Vakfı'na ilettiğiniz yardım başvurunuz sonuçlanmıştır. Başvurunuz kapsamlı bir değerlendirme sürecinden geçmiş ve aşağıdaki sonuca ulaşılmıştır.

Başvuru Sonucu: {random.choice(['Uygun Bulundu', 'Ek Belge Talep Edildi', 'Bütçe Yetersizliği Nedeniyle Sonraki Döneme Ertelendi'])}
Başvuru No: {_kargo_no()}
Bildirim Tarihi: {_tarih()}

Başvurunuza ilişkin itiraz ve soru için {_glink()} adresini ziyaret edebilir ya da vakfımızı mesai saatleri içinde arayabilirsiniz.

Saygılarımızla,
{_sehir()} SYDV Koordinatörlüğü""",

    # ── İş teklifi (gerçek, resmi) ───────────────────────────
    lambda: f"""{_unvan()} {_isim()},

Gerçekleştirilen mülakat süreçlerinin ardından {_pozisyon()} pozisyonu için tarafınıza resmi iş teklifi sunmaktan mutluluk duyarız.

Teklif Detayları:
Pozisyon: {_pozisyon()}
Başlangıç Tarihi: {_tarih()}
Çalışma Şekli: {random.choice(['Tam zamanlı / Ofis', 'Hibrit', 'Uzaktan'])}
Ücret: {_maas()} TL brüt / ay + performans primi

Teklifi kabul etmek için {_tarih()} tarihine kadar bu e-postayı yanıtlamanızı ya da İK temsilcimizle iletişime geçmenizi bekliyoruz. Detaylı sözleşme ve sosyal haklar paketi için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
{_isim()} — İnsan Kaynakları Direktörü""",

    # ── Kurs / sertifika tamamlama ───────────────────────────
    lambda: f"""{_unvan()} {_isim()},

"{random.choice(['Python ile Veri Analizi', 'Proje Yönetimi Temelleri', 'Dijital Pazarlama', 'Siber Güvenlik Temelleri'])}" programını başarıyla tamamladığınızı bildirmekten mutluluk duyuyoruz. Sertifikanız dijital ortamda hazırlanmış olup aşağıdaki bilgiler içermektedir.

Sertifika No: {_kargo_no()}
Tamamlanma Tarihi: {_tarih()}
Geçerlilik Süresi: {random.randint(1, 3)} yıl
Başarı Puanınız: %{random.randint(75, 99)}

Sertifikanızı PDF olarak indirmek ve LinkedIn profilinize eklemek için {_glink()} adresini ziyaret edebilirsiniz.

Tebrikler,
Eğitim ve Gelişim Koordinatörlüğü""",

    # ── Yıllık performans değerlendirme ──────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} dönemi yıllık performans değerlendirme süreci tamamlanmıştır. Değerlendirmenize ilişkin özet aşağıda paylaşılmaktadır.

Genel Performans Puanı: {random.randint(3, 5)}/5
Hedef Gerçekleştirme Oranı: %{random.randint(80, 115)}
Yetkinlik Değerlendirmesi: {random.choice(['Beklentilerin Üzerinde', 'Beklentileri Karşılıyor', 'Gelişim Alanı Mevcut'])}
Değerlendiren Yönetici: {random.choice(ISIMLER)}

Detaylı değerlendirme raporuna ve gelecek dönem hedeflerinize {_glink()} üzerinden erişebilirsiniz. İtiraz süreciniz {_tarih()} tarihine kadar açık kalacaktır.

Saygılarımızla,
İnsan Kaynakları Departmanı""",

    # ── Araç muayene hatırlatma (gerçek) ─────────────────────
    lambda: f"""{_unvan()} {_isim()},

Tescil bilgilerinize göre aracınızın zorunlu periyodik muayene tarihi {_tarih()} olup bu tarihe kadar muayene yaptırılması gerekmektedir. Muayene süresini aşmak trafikte para cezasına neden olabilir.

İstasyon seçimi ve randevu almak için {_glink()} adresini ziyaret edebilirsiniz. Online randevu ile bekleme süresini minimuma indirebilirsiniz. Gerekli belgeler: Trafik sigortası, ruhsat ve kimlik.

Saygılarımızla,
Araç Muayene Hizmetleri Bilgilendirme Sistemi""",

    # ── Öğrenci harç bildirimi ───────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_uni()} Öğrenci İşleri Müdürlüğü olarak, {_tarih()} dönemi öğrenim harç ücretinin ödeme bilgilerini paylaşmak istiyoruz.

Harç Tutarı: {_tutar()} TL
Son Ödeme Tarihi: {_tarih()}
Ödeme Yöntemi: Banka havalesi / EFT veya {_banka()} şubeleri

Ödemenizi gerçekleştirdikten sonra dekontunuzu öğrenci portalına yüklemenizi rica ederiz. Zamanında ödeme yapılmaması durumunda ders kaydınız onaylanmayabilir.

Saygılarımızla,
{_uni()} Öğrenci İşleri Müdürlüğü""",

    # ── Planlı bakım / elektrik kesinti (gerçek) ─────────────
    lambda: f"""{_unvan()} {_isim()},

{_sehir()} Elektrik Dağıtım A.Ş. olarak, bölgenizdeki elektrik altyapısında gerçekleştirilecek planlı bakım çalışması hakkında önceden bilgi vermek istiyoruz.

Kesinti Tarihi: {_tarih()}
Kesinti Saati: {_saat()} — {_saat()}
Etkilenen Mahalleler: {_sehir()} merkezi ve çevresi

Çalışma süresince önlem almanızı öneririz. Kesinti süresi uzarsa veya beklenmedik arıza çıkarsa ilgili ekiplerimiz en kısa sürede müdahale edecektir. Güncel bilgi için {_glink()} adresini takip edebilirsiniz.

Saygılarımızla,
{_sehir()} Elektrik Dağıtım A.Ş.""",

    # ── Kurumsal bülten ──────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} {_tarih()} dönemi kurumsal bültenine hoş geldiniz. Bu ayki öne çıkan gelişmeleri ve duyuruları sizinle paylaşmaktan mutluluk duyuyoruz.

Öne Çıkanlar:
— {random.choice(['Yeni ürün lansmanımız büyük ilgi gördü', 'Müşteri memnuniyet skorumuz rekor kırdı', 'Yeni ofisimiz açıldı', 'Sürdürülebilirlik hedeflerimize ulaştık'])}
— Çalışan sayımız {random.randint(500, 5000)}'e ulaştı
— {_tarih()} tarihinde gerçekleşecek yıllık şirket buluşmasına davetlisiniz

Tüm detaylar ve geçmiş bültenler için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
{_marka()} Kurumsal İletişim Ekibi""",

    # ── E-posta depolama uyarısı (gerçek) ────────────────────
    lambda: f"""{_unvan()} {_isim()},

Kurumsal e-posta hesabınızın depolama alanı %{random.randint(85, 95)} oranında dolmuş bulunmaktadır. Depolama limitine ulaşıldığında yeni e-posta alamazsınız ve gönderme işlemleriniz engellenebilir.

Depolama alanınızı temizlemek için eski e-postaları ve büyük ekli dosyaları silmenizi öneririz. Kurumsal depolama planı yükseltme talepleri için BT departmanıyla iletişime geçebilirsiniz.

Hesap yönetim paneline {_glink()} üzerinden erişebilirsiniz.

Saygılarımızla,
Bilgi Teknolojileri ve Altyapı Departmanı""",

    # ── Çalışan teşekkür / başarı belgesi ────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} döneminde sergilediğiniz üstün performans ve takım çalışmasına verdiğiniz katkı nedeniyle sizi tebrik etmek istiyoruz. Yönetim kurulumuz tarafından "Ayın Çalışanı" ödülüne layık görüldünüz.

Ödülünüz; {_tutar()} TL değerinde alışveriş çeki ve özel teşekkür belgesidir. Ödül takdim töreni {_tarih()} tarihinde {_sehir()} ofisimizde gerçekleştirilecektir.

Tören daveti ve detaylı bilgi için {_glink()} adresini inceleyebilirsiniz.

Saygılarımızla,
{_marka()} İnsan Kaynakları ve Yönetim Ekibi""",

    # ── Sözleşme yenileme bildirimi (gerçek) ─────────────────
    lambda: f"""{_unvan()} {_isim()},

Şirketimizle imzaladığınız hizmet sözleşmesi {_tarih()} tarihinde sona erecektir. Hizmetlerimizden memnun kaldıysanız sözleşmenizi yenileyerek iş birliğimizin devam etmesini memnuniyetle karşılarız.

Yeni dönem koşulları ve fiyat güncellemeleri aşağıda özetlenmiştir:
— Hizmet kapsamı genişletildi: {random.choice(['7/24 teknik destek eklendi', 'Bulut yedekleme dahil edildi', 'Raporlama modülü güncellendi'])}
— Dönem: {_tarih()} - {_tarih()}
— Yıllık Ücret: {_tutar()} TL

Sözleşme teklifini incelemek ve imzalamak için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
Satış ve Müşteri İlişkileri Ekibi""",

    # ── Banka kredi kartı ekstresi (gerçek) ──────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} dönemi kredi kartı ekstreniz hazırlanmıştır. Bu döneme ait harcama özetinizi aşağıda bulabilirsiniz.

Toplam Harcama: {_tutar()} TL
Asgari Ödeme Tutarı: {random.choice(['500', '750', '1.200', '2.000'])} TL
Son Ödeme Tarihi: {_tarih()}
Puan Bakiyesi: {random.randint(1000, 50000)} puan

Ekstrenizdeki harcama detaylarını {_glink()} üzerinden inceleyebilir, itiraz başlatabilir veya puan kullanım seçeneklerini görebilirsiniz.

Saygılarımızla,
{_banka()} Kart Hizmetleri""",

    # ── İş seyahati onayı ────────────────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} - {_tarih()} tarihleri arasında {_sehir()} seyahatiniz için gerekli onaylar alınmıştır. Seyahat detayları ve harcama limitleri aşağıda özetlenmiştir.

Kalkış: {_tarih()} — {_saat()}
Konaklama: {random.choice(['Sheraton', 'Hilton', 'Marriott', 'Divan'])} {_sehir()}
Günlük Harcama Limiti: {random.choice(['500', '750', '1.000', '1.500'])} TL
Ulaşım: Şirket kredi kartıyla karşılanacaktır

Seyahat belgelerinize ve masraf formuna {_glink()} üzerinden erişebilirsiniz. Seyahat sonrası masraf raporunuzu 5 iş günü içinde ibraz etmenizi hatırlatırız.

Saygılarımızla,
İnsan Kaynakları ve Seyahat Koordinasyon""",

    # ── Platform / uygulama güncelleme bildirimi (gerçek) ────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} mobil uygulamasının yeni sürümü ({random.choice(['v3.2.1', 'v4.0.0', 'v2.8.5'])}) {_tarih()} tarihi itibarıyla kullanıma sunulmuştur. Bu güncellemeyle birlikte performans iyileştirmeleri, yeni özellikler ve güvenlik yamaları hayata geçirilmiştir.

Yeni özellikler:
— {random.choice(['Karanlık mod desteği eklendi', 'Ödeme akışı yenilendi', 'Bildirim yönetimi geliştirildi'])}
— {random.choice(['Erişilebilirlik iyileştirmeleri yapıldı', 'Hata raporlama sistemi güncellendi'])}

Uygulamanızı güncellemek için {_glink()} adresini veya cihazınızın uygulama mağazasını ziyaret edebilirsiniz.

Saygılarımızla,
{_marka()} Ürün ve Teknoloji Ekibi""",

    # ── Yönetici / organizasyon değişikliği ──────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} yönetim yapısında gerçekleşen organizasyonel değişikliği paylaşmak istiyoruz. {random.choice(ISIMLER)}, {random.choice(['Genel Müdür', 'Pazarlama Direktörü', 'Finans Direktörü', 'Operasyon Direktörü'])} görevinden {_tarih()} tarihi itibarıyla ayrılmış; yerine {random.choice(ISIMLER)} atanmıştır.

Yeni yöneticimiz, {random.randint(10, 25)} yıllık sektör deneyimiyle birlikte şirketimizin büyüme hedeflerine önemli katkı sağlayacaktır. Görev devri süreci {_tarih()} tarihinde tamamlanacaktır.

Detaylı bilgi için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
{_marka()} Yönetim Kurulu""",

    # ── Okul kayıt dönemi bilgilendirme ──────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} - {_tarih()} tarihleri arasında {random.choice(['2024-2025', '2025-2026'])} eğitim öğretim yılı kayıt işlemleri başlayacaktır. Mevcut öğrenciler için kayıt yenileme, yeni öğrenciler için ise ilk kayıt işlemleri bu dönemde gerçekleştirilecektir.

Kayıt için gerekli belgeler:
— Nüfus cüzdanı fotokopisi
— İkametgâh belgesi
— Önceki yıl karne veya tasdiknamesi (yeni öğrenciler için)

Randevu ve detaylı bilgi için {_glink()} adresini ziyaret edebilirsiniz. Belirtilen süre içinde kayıt yaptırılmayan öğrencilerin kayıtları yapılmayabilir.

Saygılarımızla,
Okul Kayıt ve Öğrenci İşleri""",

    # ── Çalışan iç anket (gerçek HR) ─────────────────────────
    lambda: f"""{_unvan()} {_isim()},

{_marka()} İnsan Kaynakları departmanı olarak, çalışan memnuniyeti ve kurumsal kültür araştırmamıza katılımınızı rica ediyoruz. Bu araştırma yılda iki kez gerçekleştirilmekte olup sonuçlar çalışma koşullarımızın iyileştirilmesinde doğrudan kullanılmaktadır.

Anket yaklaşık 8-10 dakika sürmekte olup yanıtlarınız tamamen anonim tutulmaktadır. Katılım oranı hedefimiz %{random.randint(75, 95)}'tir; katkınız için şimdiden teşekkür ederiz.

Çalışan Memnuniyet Anketi: {_glink()}

Saygılarımızla,
{_marka()} İnsan Kaynakları Departmanı""",

    # ── Banka şube / ATM değişikliği (gerçek) ────────────────
    lambda: f"""{_unvan()} {_isim()},

{_banka()} olarak hizmet ağımızda gerçekleştirdiğimiz yeniden yapılanma kapsamında {_sehir()} {random.choice(['Merkez', 'Bağcılar', 'Kadıköy', 'Çankaya', 'Konak'])} Şubemiz {_tarih()} tarihi itibarıyla yeni adresine taşınmaktadır.

Yeni Adres: {_sehir()} {random.choice(['Atatürk Cad.', 'İnönü Blv.', 'Cumhuriyet Mah.', 'Bağlar Sok.'])} No:{random.randint(1, 200)}
Yeni Telefon: 0{random.randint(200, 500)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}
Taşınma Tarihi: {_tarih()}

Eski şube {_tarih()} tarihine kadar hizmet vermeye devam edecektir. En yakın şube ve ATM bilgileri için {_glink()} adresini ziyaret edebilirsiniz.

Saygılarımızla,
{_banka()} Şube Ağı ve Operasyonlar""",

    # ── Teşekkür / geri bildirim talebi (gerçek) ─────────────
    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde {random.choice(['müşteri hizmetlerimizi aradığınız', 'şubemizi ziyaret ettiğiniz', 'online hizmetlerimizi kullandığınız'])} için teşekkür ederiz. Deneyiminizi birkaç soruyla değerlendirmenizi rica ediyoruz.

Geri bildiriminiz, hizmet kalitemizi artırmak ve ekiplerimizi geliştirmek için kritik önem taşımaktadır. Değerlendirme yalnızca {random.randint(1, 3)} dakikanızı alacaktır.

Geri Bildirim Formu: {_glink()}

Değerli zamanınız için teşekkür ederiz.

Saygılarımızla,
{_marka()} Müşteri Deneyimi Ekibi""",
]


# ── 17. SAHTE DEVLET YARDIMI / SOSYAL DESTEK ─────────────────

SAHTE_SOSYAL = [

    lambda: f"""{_unvan()} {_isim()},

Aile ve Sosyal Hizmetler Bakanlığı tarafından yürütülen sosyal destek programı kapsamında hanenize {_tutar()} TL tutarında nakdi yardım tanımlanmıştır. Bu yardım, gelir düzeyi belirli eşiğin altında olan hanelere otomatik olarak tahsis edilmektedir.

Yardımın banka hesabınıza aktarılabilmesi için IBAN bilgilerinizin doğrulanması ve kimlik teyidinin yapılması gerekmektedir. İşlemi {_tarih()} tarihine kadar tamamlamazsanız tahsisat bir sonraki dönemde yeniden değerlendirilecektir.

Yardım Başvuru ve Doğrulama Portalı: {_link()}

Saygılarımızla,
Aile ve Sosyal Hizmetler Bakanlığı — e-Hizmetler Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Türkiye İş Kurumu (İŞKUR) kayıtlarına göre işsizlik ödeneği başvurunuz değerlendirme aşamasına geçmiştir. Başvurunuzun sonuçlanabilmesi için güncel banka hesap bilgilerinizin ve son iş yerinize ait belgelerinizin sisteme yüklenmesi gerekmektedir.

Ödenek miktarınız aylık {_tutar()} TL olarak hesaplanmış olup onay verilmesi durumunda ilk ödeme {_tarih()} tarihinde gerçekleştirilecektir.

Başvuru Tamamlama Portalı: {_link()}

Saygılarımızla,
İŞKUR Dijital Hizmetler Birimi""",

    lambda: f"""{_unvan()} {_isim()},

{_sehir()} Büyükşehir Belediyesi Sosyal Yardım Birimi olarak, hane bazlı değerlendirme sistemimiz kapsamında adresinize {_tutar()} TL tutarında gıda ve yakıt yardımı tahsis edildiğini bildirmek istiyoruz.

Yardımın karta yüklenmesi için e-devlet şifreniz veya T.C. kimlik numaranızla aşağıdaki sisteme giriş yapmanız yeterlidir. Kart teslimatı {_tarih()} tarihinde başlayacaktır.

Yardım Doğrulama ve Kart Aktivasyonu: {_link()}

Saygılarımızla,
{_sehir()} Büyükşehir Belediyesi Sosyal Yardım Birimi""",

    lambda: f"""{_unvan()} {_isim()},

COVID-19 döneminde işletmenize sağlanan hibe ve destek ödemelerine ilişkin Hazine ve Maliye Bakanlığı tarafından geri ödeme talebi iletilmiştir. Yapılan denetimde {_tutar()} TL tutarındaki desteğin usule aykırı kullanıldığı tespit edilmiş olup bu tutarın {_tarih()} tarihine kadar iade edilmesi beklenmektedir.

Denetim sonuçlarına itiraz etmek veya taksit planı oluşturmak için aşağıdaki portala erişebilirsiniz. Belirtilen tarihte ödeme yapılmaması halinde hukuki süreç başlatılacaktır.

İtiraz ve Ödeme Planı Portalı: {_link()}

Saygılarımızla,
Hazine ve Maliye Bakanlığı — Denetim ve Geri Kazanım Birimi""",
]

# ── 18. SAHTE YAZILIM / TEKNOLOJİ ────────────────────────────

SAHTE_YAZILIM = [

    lambda: f"""{_unvan()} {_isim()},

Windows lisansınızın {_tarih()} tarihinde süresi dolacağı tespit edilmiştir. Lisans yenilenmediği takdirde bilgisayarınız kısıtlı modda çalışmaya başlayacak; belge düzenleme, yazdırma ve bazı uygulamalara erişim engellenecektir.

Lisansınızı aşağıdaki Microsoft Lisans Merkezi üzerinden yenileyebilirsiniz. Mevcut müşterilerimize özel %{_yuzde()} indirim geçerli olup işlem yalnızca birkaç dakika sürmektedir.

Microsoft Lisans Merkezi: {_link()}

Saygılarımızla,
Microsoft Türkiye Lisans Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Kullandığınız bulut depolama hesabınızın kapasitesi %{random.randint(90, 99)} oranında dolmuştur. Mevcut planınız {random.choice(['5 GB', '15 GB', '50 GB'])} ile sınırlı olup yeni dosya yükleme ve senkronizasyon işlemleri artık çalışmayabilir.

Depolama alanınızı genişletmek için aylık {random.choice(['29,99', '49,99', '79,99'])} TL'den başlayan Premium planlarımıza geçiş yapabilirsiniz. İlk 3 ay yarı fiyatla deneme fırsatını kaçırmayın.

Plan Yükseltme: {_link()}

Saygılarımızla,
Bulut Depolama Müşteri Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Cihazınızda gerçekleştirilen otomatik güvenlik taraması, {random.randint(3, 12)} adet yüksek öncelikli tehdidi tespit etmiştir. Bu tehditler; reklam yazılımı, casus yazılım ve potansiyel olarak istenmeyen programları (PUP) kapsamaktadır.

Tespit edilen tehditleri temizlemek ve cihazınızı koruma altına almak için güvenlik yazılımımızın tam sürümünü etkinleştirmeniz gerekmektedir. Ücretsiz deneme sürümüyle yalnızca tespit yapılabilmekte; temizleme işlemi Premium lisans gerektirmektedir.

Temizleme ve Lisans Aktivasyonu: {_link()}

Saygılarımızla,
Güvenlik Yazılımı Destek Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Kurumsal yazılım aboneliğiniz {_tarih()} tarihinde yenilenecektir. Bu dönemde lisans fiyatlarında %{_yuzde()} artış yapılmış olup yeni dönem ücreti {_tutar()} TL olarak güncellenmiştir.

Mevcut fiyat avantajını koruyabilmek için yenileme işlemini {_tarih()} tarihinden önce tamamlamanız gerekmektedir. Erken yenileme için özel sabit fiyat teklifi sunulmaktadır.

Erken Yenileme ve Fiyat Kilitleme: {_link()}

Saygılarımızla,
Kurumsal Lisans Yönetim Ekibi""",
]

# ── 19. SAHTE HUKUKİ BİLDİRİM ────────────────────────────────

SAHTE_HUKUK = [

    lambda: f"""{_unvan()} {_isim()},

Adınıza açılmış bir hukuki dava dosyası oluşturulmuş olup duruşma tarihi {_tarih()} olarak belirlenmiştir. Davanın konusu, karşı tarafın öne sürdüğü {random.choice([f'{_tutar()} TL tutarındaki alacak talebi', 'sözleşme ihlali iddiası', 'fikri mülkiyet ihlali', 'tazminat talebi'])}dir.

Duruşmaya katılmamanız veya yasal süre içinde savunma sunmamanız durumunda mahkeme gıyabi karar verebilir. Hukuki haklarınızı korumak için aşağıdaki e-tebligat sisteminden dosyaya erişmenizi öneririz.

Dava Dosyası ve e-Tebligat: {_link()}

Saygılarımızla,
e-Tebligat Sistemi — Adalet Bakanlığı""",

    lambda: f"""{_unvan()} {_isim()},

Bağlı olduğunuz vergi dairesinin yürüttüğü inceleme kapsamında {_tarih()} - {_tarih()} dönemine ait vergi beyannamelerinizde usulsüzlük tespit edilmiştir. {_tutar()} TL tutarındaki eksik beyan nedeniyle vergi ziyaı cezası uygulanması gündemdedir.

Cezadan kaçınmak ve uzlaşma sürecini başlatmak için {_tarih()} tarihine kadar ilgili vergi dairesine başvurmanız ya da aşağıdaki dijital uzlaşma portalını kullanmanız gerekmektedir.

Uzlaşma Başvuru Portalı: {_link()}

Saygılarımızla,
Vergi Dairesi Müdürlüğü — Denetim Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Tüketici hakları kapsamında {_marka()} aleyhine açılan toplu davaya katılım süreciniz başlatılmıştır. Dava; {random.choice(['yanıltıcı reklam', 'gizli ücret uygulaması', 'sözleşme ihlali', 'ayıplı ürün satışı'])} gerekçesiyle açılmış olup kazanılması halinde her katılımcı {_tutar()} TL'ye kadar tazminat alabilecektir.

Davaya katılmak ve haklarınızı korumak için {_tarih()} tarihine kadar kayıt yaptırmanız gerekmektedir. Avukatlık ücreti dahil tüm süreç tarafımızca üstlenilmektedir.

Toplu Dava Katılım Formu: {_link()}

Saygılarımızla,
Tüketici Hakları Hukuk Bürosu""",
]

# ── 20. SAHTE YATIRIM / BORSA ─────────────────────────────────

SAHTE_YATIRIM = [

    lambda: f"""{_unvan()} {_isim()},

Analistlerimizin yürüttüğü piyasa araştırması kapsamında kısa vadede %{random.randint(40, 120)} getiri potansiyeli taşıyan bir yatırım fırsatı tespit edilmiştir. {random.choice(['Borsa endeks fonu', 'Emtia sertifikası', 'Yapılandırılmış ürün', 'Özel girişim fonu'])} kategorisindeki bu enstrüman, sınırlı yatırımcıya sunulmaktadır.

Portföyünüze {_tutar()} TL ile dahil olarak bu fırsatı değerlendirmek isterseniz yatırım danışmanımızla bağlantı kurmanızı öneririz. Ön kayıt için aşağıdaki formu doldurmanız yeterlidir.

Yatırım Ön Kayıt Formu: {_link()}

Saygılarımızla,
Yatırım Danışmanlığı ve Portföy Yönetim Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Platformumuzda tanımlı yatırım hesabınızda {_tarih()} tarihinde gerçekleştirilen işlem nedeniyle {_tutar()} TL tutarında kâr elde edilmiştir. Bu tutarı hesabınıza çekmek için kimlik doğrulama işlemini tamamlamanız gerekmektedir.

Platform güvenlik politikamız uyarınca {_tutar()} TL üzerindeki çekim işlemlerinde ikinci aşama doğrulama zorunludur. İşlemi {_tarih()} tarihine kadar gerçekleştirmezseniz kârınız otomatik olarak portföyde kalmaya devam edecektir.

Kâr Çekimi ve Kimlik Doğrulama: {_link()}

Saygılarımızla,
Yatırım Platformu Operasyon Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Altın ve döviz bazlı yatırım ürünlerimizde {_tarih()} tarihine özel tanıttığımız kampanya kapsamında minimum {_tutar()} TL yatırımla sabit %{random.randint(15, 35)} yıllık getiri garantisi sunulmaktadır. Bu oran mevcut mevduat faizinin yaklaşık {random.randint(2, 4)} katına denk gelmektedir.

Yatırım miktarınızı ve vade tercihinizi belirlemek için ücretsiz danışmanlık görüşmesi talep edebilirsiniz. Kampanya kontenjanı sınırlı tutulmuş olup {_tarih()} tarihinden sonra başvurular kabul edilmeyecektir.

Kampanya Başvuru Formu: {_link()}

Saygılarımızla,
Alternatif Yatırım Danışmanlığı""",
]

# ── 21. SAHTE ABONELİK / ÜYELİK ─────────────────────────────

SAHTE_UYELIK = [

    lambda: f"""{_unvan()} {_isim()},

{random.choice(['Premium üyelik', 'VIP abonelik', 'Altın üyelik'])} hesabınız {_tarih()} tarihinde otomatik olarak yenilenmiş ve {_tutar()} TL ücret kredi kartınızdan tahsil edilmiştir. Eğer bu yenilemeyi iptal etmek isterseniz {_tarih()} tarihine kadar başvurmanız halinde tam iade yapılacaktır.

İptal işlemini gerçekleştirmek için üye panelinize giriş yapmanız ve iptal talebini onaylamanız gerekmektedir. Aşağıdaki bağlantıdan hesabınıza erişebilirsiniz.

Üye Paneli ve İptal Talebi: {_link()}

Saygılarımızla,
Abonelik Yönetim Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

{_marka()} platformuna üyeliğinizi aktif tutabilmek için {_tarih()} tarihine kadar hesap doğrulama işlemini tamamlamanız gerekmektedir. Bu zorunluluk, sahte hesapların önlenmesine yönelik yeni güvenlik politikamız kapsamında getirilmiştir.

Doğrulama yapılmaması durumunda hesabınız geçici olarak askıya alınacak ve biriktirdiğiniz {random.randint(500, 5000)} puan ile satın alma geçmişinize erişiminiz kısıtlanacaktır.

Hesap Doğrulama: {_link()}

Saygılarımızla,
{_marka()} Üye Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Ücretsiz deneme süreniz {_tarih()} tarihinde sona ermekte olup bu tarihten itibaren {_tutar()} TL aylık ücret otomatik olarak tahsil edilecektir. Ücretlendirmeden haberdar olmak isteyenler için önceden bildirim yapmak politikamız gereğidir.

Aboneliği iptal etmek veya farklı bir plan seçmek için hesap ayarlarınıza erişmenizi öneririz. Ücretsiz planla devam etmek isterseniz kredi kartı bilgilerinizi sistemden kaldırmanız gerekmektedir.

Abonelik Yönetimi: {_link()}

Saygılarımızla,
Platform Abonelik Ekibi""",
]

# ── 22. SAHTE HEDİYE KARTI / KUPON ───────────────────────────

SAHTE_HEDIYE = [

    lambda: f"""TEBRİKLER {_isim().upper()}!

{_marka()} Sadakat Programı kapsamında hesabınıza {_tutar()} TL değerinde dijital hediye kartı tanımlanmıştır. Bu kartı tüm ürün kategorilerinde ve kampanyalı ürünlerde kullanabilirsiniz.

Kartınızı aktive etmek ve bakiyenizi görüntülemek için üye panelinize giriş yaparak "Hediyelerim" bölümünü ziyaret etmeniz gerekmektedir. Kart {_tarih()} tarihine kadar geçerlidir; bu tarihten sonra bakiye sıfırlanacaktır.

Hediye Kartı Aktivasyonu: {_link()}

Saygılarımızla,
{_marka()} Sadakat Programı Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

{_marka()} işbirliğiyle sunulan özel kupon kodunuz hazır. Aşağıdaki kodu kullanarak {_tarih()} tarihine kadar yapacağınız alışverişlerde %{_yuzde()} indirimden yararlanabilirsiniz.

Kupon geçerlilik koşulları: Minimum {_tutar()} TL alışveriş, kişi başı tek kullanım, seçili kategorilerde geçerlidir. Kodu aktive etmek ve detaylı kuralları görmek için aşağıdaki bağlantıyı kullanabilirsiniz.

Kupon Aktivasyon Sayfası: {_link()}

Saygılarımızla,
{_marka()} Kampanya Ekibi""",
]


# ── 23. SAHTE ECZANE / ONLINE SAĞLIK ─────────────────────────

SAHTE_ECZANE = [

    lambda: f"""{_unvan()} {_isim()},

Online eczane sistemimiz aracılığıyla doktorunuz tarafından düzenlenen reçeteniz onaylanmıştır. Reçetenizdeki ilaçlar stokta mevcuttur ve siparişiniz hazırlanmaya başlanabilir.

Toplam İlaç Tutarı: {_tutar()} TL
Teslimat Süresi: {random.randint(1, 3)} iş günü
Ödeme Seçenekleri: Kredi kartı, havale veya kapıda ödeme

Siparişi onaylamak ve teslimat adresinizi belirlemek için aşağıdaki bağlantıya tıklayabilirsiniz. İlk siparişinizde %{_yuzde()} indirim uygulanmaktadır.

Sipariş Onay ve Ödeme: {_link()}

Saygılarımızla,
Online Eczane Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

{random.choice(['Diyabet', 'Hipertansiyon', 'Astım', 'Migren'])} rahatsızlığınız için doktorunuzun önerdiği yeni nesil tedavi protokolü hakkında bilgilendirmek istiyoruz. Klinik çalışmalarda %{random.randint(70, 95)} etkinlik gösteren bu ürün şu an yalnızca online kanalımız üzerinden temin edilebilmektedir.

Ürün hakkında detaylı bilgi almak, doktorunuzun önerisiyle karşılaştırmanızı sağlayan raporu incelemek ve sipariş vermek için hasta portalına giriş yapabilirsiniz.

Hasta Portalı ve Sipariş: {_link()}

Saygılarımızla,
Sağlık Danışmanlık Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Yıllık sağlık tarama sonuçlarınız değerlendirilerek kişiselleştirilmiş vitamin ve takviye programınız hazırlanmıştır. Programınız; yaşınız, cinsiyetiniz ve laboratuvar değerleriniz esas alınarak uzman hekim tarafından oluşturulmuştur.

Kişiselleştirilmiş paketiniz aylık {_tutar()} TL olup her ay adresinize gönderilmektedir. İlk ay ücretsiz deneme fırsatını değerlendirmek için aşağıdaki bağlantıyı kullanabilirsiniz.

Ücretsiz Deneme Paketi: {_link()}

Saygılarımızla,
Kişiselleştirilmiş Sağlık Programları""",
]

# ── 24. SAHTE RESMİ BELGE / PASAPORT / EHLİYET ───────────────

SAHTE_RESMI = [

    lambda: f"""{_unvan()} {_isim()},

T.C. Nüfus ve Vatandaşlık İşleri Genel Müdürlüğü sistemleri, pasaportunuzun geçerlilik süresinin {_tarih()} tarihinde dolacağını tespit etmiştir. Yurt dışı seyahatlerinizin aksamaması için pasaport yenileme işlemini zamanında başlatmanızı öneririz.

Online ön başvuru ile randevu bekleme süresini önemli ölçüde azaltabilirsiniz. T.C. kimlik numaranız ve güncel fotoğrafınızla ön başvuruyu aşağıdaki sistemden tamamlayabilirsiniz.

Pasaport Yenileme Ön Başvurusu: {_link()}

Saygılarımızla,
Nüfus ve Vatandaşlık İşleri Genel Müdürlüğü""",

    lambda: f"""{_unvan()} {_isim()},

Emniyet Genel Müdürlüğü kayıtlarına göre sürücü belgenizin yenileme tarihi {_tarih()} olup bu tarihten itibaren geçerliliğini yitirecektir. Sürücü belgesi olmaksızın araç kullanmak trafikte cezai işleme neden olabilir.

Yenileme işlemini e-Devlet üzerinden gerçekleştirebilir ya da aşağıdaki sistemi kullanarak randevu oluşturabilirsiniz. Online başvurularda işlem süresi ortalama 3 iş günüdür.

Ehliyet Yenileme Başvurusu: {_link()}

Saygılarımızla,
Emniyet Genel Müdürlüğü — Sürücü Belgesi Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Yurt dışı vize başvurunuz {_tarih()} tarihinde {random.choice(['İngiltere', 'Almanya', 'ABD', 'Kanada', 'Avustralya'])} Büyükelçiliği tarafından ön onaya alınmıştır. Başvurunuzun tamamlanabilmesi için ek belgeler talep edilmekte ve biyometrik randevu planlanması gerekmektedir.

Eksik belgeler ve randevu için aşağıdaki vize başvuru portalını kullanabilirsiniz. Randevu almadan önce tüm belgelerinizi hazırlamanızı ve gerekli onay işlemlerini tamamlamanızı öneririz.

Vize Başvuru Portalı: {_link()}

Saygılarımızla,
Vize Danışmanlık Hizmetleri""",

    lambda: f"""{_unvan()} {_isim()},

Araç tescil belgenizde kayıtlı zorunlu trafik sigortanızın bitiş tarihi {_tarih()} olarak görünmekte olup bu tarihten sonra sigortasız araç kullanmak ağır para cezasına yol açacaktır.

Poliçenizi çevrimiçi ortamda en uygun fiyata yenilemek için çok sayıda sigorta şirketinin tekliflerini karşılaştırabilirsiniz. Ödemenizi tamamlarsanız poliçeniz anında aktive edilir ve dijital kopya e-posta adresinize iletilir.

Sigorta Karşılaştırma ve Yenileme: {_link()}

Saygılarımızla,
Online Sigorta Hizmetleri""",
]

# ── 25. SAHTE ENERJİ / KESİNTİ ───────────────────────────────

SAHTE_ENERJI = [

    lambda: f"""{_unvan()} {_isim()},

{_sehir()} Elektrik Dağıtım A.Ş. olarak, {_tutar()} TL tutarındaki elektrik borcunuzun {_tarih()} tarihine kadar ödenmediğini ve {_tarih()} tarihi itibarıyla aboneliğinize kesinti uygulanacağını bildirmek üzere bu yazıyı iletiyoruz.

Kesintinin önüne geçmek için borcunuzu aşağıdaki e-ödeme sistemi üzerinden ödeyebilir ya da ödeme planı talebinde bulunabilirsiniz. Taksit seçenekleri hakkında detaylı bilgiye de aynı platform üzerinden ulaşabilirsiniz.

e-Ödeme ve Ödeme Planı Talebi: {_link()}

Saygılarımızla,
{_sehir()} Elektrik Dağıtım A.Ş. Tahsilat Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Doğalgaz aboneliğinize ait {_tutar()} TL tutarındaki gecikmiş faturanız nedeniyle {_tarih()} tarihinde gaz akışı durdurulacaktır. Kesinti gerçekleşmeden önce borcunuzu ödemenizi ve kesinti işlemini iptal ettirmenizi öneririz.

Ödeme işlemi tamamlandıktan sonra 4 saat içinde gaz akışı yeniden başlatılacaktır. Ödeme ve yeniden bağlantı talepleri için aşağıdaki sistemi kullanabilirsiniz.

Ödeme ve Yeniden Bağlantı Talebi: {_link()}

Saygılarımızla,
Doğalgaz Dağıtım Şirketi Tahsilat ve Bağlantı Birimi""",

    lambda: f"""{_unvan()} {_isim()},

İnternet aboneliğinizde aylık {random.randint(100, 500)} GB veri limitinizin %{random.randint(90, 99)}'ine ulaşılmıştır. Kalan dönem boyunca hız kısıtlamasıyla karşılaşmamak için veri paketinizi genişletmenizi öneririz.

Ek veri paketi satın almak veya sınırsız plana geçmek için müşteri panelinize erişebilirsiniz. Şu an geçerli kampanyalar kapsamında ek paket fiyatlarında %{_yuzde()} indirim uygulanmaktadır.

Veri Paketi Yönetimi: {_link()}

Saygılarımızla,
{_operator()} Müşteri Hizmetleri""",
]

# ── 26. SAHTE MÜŞTERİ HİZMETLERİ ────────────────────────────

SAHTE_MUSTERI = [

    lambda: f"""{_unvan()} {_isim()},

{_marka()} müşteri memnuniyeti ekibi olarak, hesabınızda alışılmadık bir işlem örüntüsü gözlemlendiğini ve sizinle iletişime geçmemiz gerektiğini bildirmek istiyoruz. Hesabınızı korumak için kimliğinizi doğrulamanızı ve bilgilerinizi güncellemenizi talep ediyoruz.

İşlemi {_tarih()} tarihine kadar tamamlamanız önem taşımaktadır. Doğrulama işlemi tamamlanmadan hesabınızdaki bazı özellikler kısıtlı çalışmaya devam edecektir.

Hesap Doğrulama: {_link()}

Saygılarımızla,
{_marka()} Müşteri Koruma Birimi""",

    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde {_marka()} müşteri hizmetleriyle gerçekleştirdiğiniz görüşme sonucunda hesabınıza {_tutar()} TL iade tanımlanmıştır. İadenin banka hesabınıza aktarılabilmesi için IBAN bilgilerinizin doğrulanması gerekmektedir.

İşlemi {_tarih()} tarihine kadar tamamlamazsanız iade talebi iptal edilecektir. IBAN doğrulamasını aşağıdaki güvenli form üzerinden tamamlayabilirsiniz.

IBAN Doğrulama ve İade Talebi: {_link()}

Saygılarımızla,
{_marka()} İade ve Ödeme Birimi""",

    lambda: f"""{_unvan()} {_isim()},

{_banka()} müşteri şikayetleri değerlendirme birimi olarak, tarafınızca daha önce iletilen şikayetin çözüme kavuşturulabilmesi için ek bilgi ve belge talep edildiğini bildiriyoruz.

Lütfen aşağıdaki güvenli şikayet portalına giriş yaparak istenen belgeleri yükleyiniz. Süreç tamamlandıktan sonra başvurunuz 5 iş günü içinde sonuçlanacak ve tarafınıza bildirim yapılacaktır.

Şikayet Portalı: {_link()}

Saygılarımızla,
{_banka()} Müşteri Şikayetleri Değerlendirme Birimi""",
]

# ── 27. SAHTE KURUMSAL / İÇ İLETİŞİM ────────────────────────

SAHTE_KURUMSAL = [

    lambda: f"""{_unvan()} {_isim()},

Şirketimizin {_tarih()} tarihli yönetim kurulu kararı uyarınca tüm çalışanların kurumsal iletişim verilerinin güncellenmesi zorunlu kılınmıştır. Bu güncelleme; acil durum iletişim planımızın ve güvenlik politikamızın güncel tutulması için gereklidir.

Güncelleme formunu doldurmanız yaklaşık 5 dakika sürmekte olup {_tarih()} tarihine kadar tamamlanması beklenmektedir. Güncelleme yapılmaması halinde kurumsal sistem erişiminiz kısıtlanabilir.

Veri Güncelleme Formu: {_link()}

Saygılarımızla,
Kurumsal İletişim ve İK Departmanı""",

    lambda: f"""{_unvan()} {_isim()},

{_tarih()} tarihinde gerçekleştirilen iç denetim kapsamında departmanınıza ait harcama kayıtlarında {_tutar()} TL tutarında tutarsızlık tespit edilmiştir. Bu farkın açıklanması için ilgili dönem belgelerinin sisteme yüklenmesi gerekmektedir.

Belgeleri {_tarih()} tarihine kadar denetim portalına yüklemenizi rica ederiz. Aksi hâlde konu üst yönetime iletilecektir.

Denetim Belgesi Yükleme Portalı: {_link()}

Saygılarımızla,
İç Denetim ve Uyum Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Şirket ağımızda gerçekleştirilen planlı bakım çalışması kapsamında tüm çalışanların VPN ve uzak erişim kimlik bilgilerini {_tarih()} tarihine kadar yenilemesi gerekmektedir. Bu yenileme yapılmadığı takdirde uzaktan çalışma sistemlerine erişiminiz kesilecektir.

Kimlik bilgisi yenileme işlemi için kurumsal kimliğiniz ve mevcut şifrenizle aşağıdaki IT portalına erişmeniz yeterlidir.

IT Portalı — Kimlik Yenileme: {_link()}

Saygılarımızla,
Bilgi Teknolojileri Departmanı""",
]


# ═════════════════════════════════════════════════════════════
# ÜRETİCİ
# ═════════════════════════════════════════════════════════════

# ── 28. SAHTE SOSYAL MEDYA ───────────────────────────────────

SAHTE_SOSYAL_MEDYA = [

    lambda: f"""{_unvan()} {_isim()},

YouTube kanalınız içerik politikamız kapsamında incelemeye alınmıştır. Kanalınızdaki {random.randint(1, 5)} videoda telif hakkı ihlali tespit edilmiş olup hesabınıza kısıtlama uygulanmıştır.

Kanal gelir elde etme özelliğiniz geçici olarak askıya alınmıştır. İtiraz sürecini başlatmak ve kanalınızı kurtarmak için aşağıdaki içerik stüdyosu bağlantısını kullanmanızı öneririz.

İtiraz ve Kanal Kurtarma: {_link()}

Saygılarımızla,
YouTube İçerik Politikaları Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Twitter/X hesabınız, toplu mention ve otomatik içerik paylaşımına ilişkin platform kurallarını ihlal ettiği gerekçesiyle askıya alınmıştır. Hesabınızı yeniden aktive etmek için kimlik doğrulama sürecini tamamlamanız gerekmektedir.

Askıya alma işlemi {_tarih()} tarihinde gerçekleştirilmiş olup itiraz hakkınız {_tarih()} tarihine kadar geçerlidir. Süreyi kaçırmanız halinde hesabınız kalıcı olarak kapatılabilir.

Hesap Kurtarma ve İtiraz: {_link()}

Saygılarımızla,
Twitter/X Güvenlik ve Politika Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

TikTok hesabınız mavi tik (doğrulanmış hesap) başvurunuz değerlendirmeye alınmıştır. Başvurunuzun sonuçlandırılabilmesi için kimlik belgesi ve ek hesap doğrulama belgelerinin sisteme yüklenmesi gerekmektedir.

Doğrulama belgelerini yüklemek ve başvurunuzu tamamlamak için aşağıdaki yaratıcı portalına erişebilirsiniz. Eksik belgeler yüklenmediği takdirde başvurunuz otomatik olarak reddedilecektir.

Yaratıcı Portalı — Doğrulama: {_link()}

Saygılarımızla,
TikTok İçerik Yaratıcıları Ekibi""",

    lambda: f"""{_unvan()} {_isim()},

Facebook Business hesabınıza bağlı reklam hesabı, şüpheli ödeme faaliyeti nedeniyle geçici olarak durdurulmuştur. Aktif kampanyalarınız yayınlanmayı durdurmuş olup bütçenizde kullanılmayan tutar iade sürecine alınmıştır.

Reklam hesabınızı yeniden aktive etmek ve iade sürecini başlatmak için kimliğinizi doğrulamanız gerekmektedir. İşlemi tamamlamak için iş hesabı yöneticinizi kullanabilirsiniz.

Reklam Hesabı Kurtarma: {_link()}

Saygılarımızla,
Meta Business Destek Ekibi""",
]

# ── 29. SAHTE POLİS / GÜVENLİK BİLDİRİMİ ────────────────────

SAHTE_POLIS = [

    lambda: f"""{_unvan()} {_isim()},

Siber Suçlarla Mücadele Daire Başkanlığı olarak, IP adresinizden gerçekleştirilen internet trafiğinde yasadışı içeriğe erişim girişimi tespit edildiğini bildirmek istiyoruz. Söz konusu trafik kayıtları adınıza açılan soruşturma dosyasına eklenmiştir.

Soruşturmanın tarafınızı etkilememesi için dijital kimliğinizi doğrulamanız ve beyanda bulunmanız gerekmektedir. İşlemi {_tarih()} tarihine kadar tamamlamazsanız evinize tebligat gönderilecektir.

Dijital Kimlik Doğrulama ve Beyan: {_link()}

Saygılarımızla,
Siber Suçlarla Mücadele Daire Başkanlığı""",

    lambda: f"""{_unvan()} {_isim()},

{_sehir()} Cumhuriyet Savcılığı adına yapılan incelemede, adınıza kayıtlı bir banka hesabından şüpheli işlemler tespit edilmiş ve dosya savcılığa sevk edilmiştir. Hakkınızdaki soruşturmanın kapatılabilmesi için beyan formunu doldurmanız zorunludur.

Formun doldurulmaması ve {_tarih()} tarihine kadar savcılığa başvurulmaması durumunda haklarınızı kullanamayabilirsiniz.

Savcılık Beyan Formu: {_link()}

Saygılarımızla,
{_sehir()} Cumhuriyet Savcılığı — Dijital Tebligat Sistemi""",

    lambda: f"""{_unvan()} {_isim()},

INTERPOL Türkiye İrtibat Bürosu tarafından yürütülen uluslararası soruşturma kapsamında adınız kara para aklamayla ilgili bir davada tanık olarak anılmaktadır. Bu süreçte iş birliği yapmanız hem kendinizi korumanız hem de soruşturmanın hızlı sonuçlanması için önem taşımaktadır.

Beyanınızı vermek ve kimliğinizi doğrulamak için aşağıdaki güvenli portala erişebilirsiniz. Bu konuda herhangi bir kuruluşla iletişime geçmeden önce bu adımı tamamlamanızı öneririz.

Güvenli Beyan Portalı: {_link()}

Saygılarımızla,
INTERPOL Türkiye İrtibat Bürosu""",
]

# ── 30. SAHTE OKUL / ÜNİVERSİTE KAYIT ───────────────────────

SAHTE_OKUL = [

    lambda: f"""{_unvan()} {_isim()},

{_uni()} {random.choice(['Lisans', 'Yüksek Lisans', 'Doktora'])} programına yaptığınız başvuru ön değerlendirme aşamasını geçmiş olup kesin kabul için son belgelerin sisteme yüklenmesi gerekmektedir.

Eksik belgeler: Diploma onaylı fotokopisi, transkript, referans mektubu ve banka dekontu. Belgelerin {_tarih()} tarihine kadar sisteme yüklenmemesi durumunda kontenjanınız bir sonraki adaya devredilecektir.

Belge Yükleme Portalı: {_link()}

Saygılarımızla,
{_uni()} Öğrenci Kabul ve Kayıt Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Yurt dışı üniversite başvuru danışmanlık hizmetimiz kapsamında profiliniz değerlendirilmiş; {random.choice(['Oxford', 'MIT', 'Harvard', 'ETH Zürich', 'TU Berlin'])} üniversitesine kabul şansınızın yüksek olduğu tespit edilmiştir.

Başvuru sürecini profesyonel destek alarak yönetmek isterseniz aşağıdaki danışmanlık formunu doldurabilirsiniz. İlk görüşme ücretsiz olup başvuru takvimi ve burs olanakları hakkında detaylı bilgi paylaşılacaktır.

Danışmanlık Başvuru Formu: {_link()}

Saygılarımızla,
Uluslararası Eğitim Danışmanlık Merkezi""",

    lambda: f"""{_unvan()} {_isim()},

YKS / ALES / DGS sınav sonuçlarınız açıklanmış ve tercih ettiğiniz {_uni()} programına yerleştiğiniz belirlenmiştir. Kesin kaydınızı tamamlamanız için {_tarih()} - {_tarih()} tarihleri arasında aşağıdaki kayıt sistemine girmeniz gerekmektedir.

Kayıt için gerekli belgeler: Nüfus cüzdanı, lise diploması, sınav sonuç belgesi. Kayıt süresi içinde işlem yapılmaması halinde yeriniz başka bir adaya aktarılacaktır.

Kayıt Sistemi: {_link()}

Saygılarımızla,
{_uni()} Öğrenci İşleri Daire Başkanlığı""",
]

# ── 31. SAHTE FRANCHISE / ORTAKLIK TEKLİFİ ───────────────────

SAHTE_IS2 = [

    lambda: f"""{_unvan()} {_isim()},

Türkiye genelinde hızla büyüyen franchise ağımıza yatırımcı arıyoruz. {_sehir()} bölgesinde henüz bayiimiz bulunmadığından bu bölge için özel franchise hakkı sunmaktayız.

Toplam yatırım tutarı {_tutar()} TL olup 18-24 ay içinde geri dönüş sağlamaktadır. Başarılı franchise sahiplerimiz aylık ortalama {_maas()} TL net gelir elde etmektedir. Ücretsiz bilgilendirme toplantısına katılmak için aşağıdaki formu doldurabilirsiniz.

Franchise Bilgi Formu: {_link()}

Saygılarımızla,
Franchise Geliştirme ve Bayi Koordinasyon Merkezi""",

    lambda: f"""{_unvan()} {_isim()},

Yurt dışı merkezli şirketimizin Türkiye distribütörlüğü için uygun partner arayışındayız. Ürünlerimiz {random.choice(['15', '22', '30'])} ülkede satılmakta olup Türkiye pazarı için özel fiyatlandırma ve pazarlama desteği sunulmaktadır.

Distribütörlük anlaşması kapsamında aylık minimum sipariş taahhüdü {_tutar()} TL olup karşılığında bölgesel satış yetkisi verilmektedir. Daha fazla bilgi almak için aşağıdaki partner başvuru formunu doldurabilirsiniz.

Partner Başvuru Formu: {_link()}

Saygılarımızla,
Uluslararası Satış ve Dağıtım Ortaklıkları""",

    lambda: f"""{_unvan()} {_isim()},

Evden çalışma imkânı sunan e-ticaret ortaklık programımıza katılarak ek gelir elde edebilirsiniz. Programımız; ürün listelemesi, müşteri takibi ve sosyal medya paylaşımlarından oluşmaktadır.

Aylık {_maas()} TL'ye kadar kazanma potansiyeli olan bu program için herhangi bir ön yatırım gerekmemektedir. Tek yapmanız gereken kayıt formunu doldurmak ve eğitim sürecini tamamlamaktır.

Ortaklık Kayıt Formu: {_link()}

Saygılarımızla,
Dijital Girişim ve Ortaklık Programı""",
]

# ── 32. SAHTE ANKET / ARAŞTIRMA ──────────────────────────────

SAHTE_ANKET = [

    lambda: f"""{_unvan()} {_isim()},

{_uni()} Sosyal Bilimler Araştırma Merkezi tarafından yürütülen "{random.choice(['Dijital Alışkanlıklar ve Güvenlik', 'Tüketici Davranışları', 'Finansal Okuryazarlık', 'Sosyal Medya Kullanımı'])}" konulu akademik araştırmaya katılımınız için davet aldınız.

Araştırma, T.C. Bilim Akademisi tarafından desteklenmekte olup sonuçlar yalnızca akademik amaçla kullanılacaktır. Anketi tamamlayan katılımcılar {_tutar()} TL değerinde e-ticaret hediye kodu alacaktır.

Araştırma Anketine Katıl: {_link()}

Saygılarımızla,
{_uni()} Araştırma ve Geliştirme Merkezi""",

    lambda: f"""{_unvan()} {_isim()},

{_operator()} müşteri araştırma ekibi olarak, hizmet kalitemizi değerlendirmeniz için sizinle iletişime geçiyoruz. Yaklaşık 10 dakika sürecek bu araştırmaya katılımınız karşılığında hesabınıza {_tutar()} TL değerinde hediye paketi tanımlanacaktır.

Araştırma kapsamında internet hızı, müşteri hizmetleri deneyimi ve tarife memnuniyeti sorgulanacaktır. Yanıtlarınız tamamen gizli tutulacak ve yalnızca hizmet iyileştirme amacıyla kullanılacaktır.

Araştırmaya Katıl: {_link()}

Saygılarımızla,
{_operator()} Müşteri Araştırma Birimi""",
]

# ── 33. SAHTE KİŞİSEL VERİ / GDPR ───────────────────────────

SAHTE_KVKK = [

    lambda: f"""{_unvan()} {_isim()},

Kişisel Verileri Koruma Kurumu (KVKK) denetimleri kapsamında {_marka()} nezdinde kayıtlı kişisel verilerinizin güncelliği sorgulanmaktadır. Verilerinizin doğru ve güncel tutulması yasal zorunluluk olup bu konudaki talebinizi {_tarih()} tarihine kadar iletmeniz gerekmektedir.

Kişisel verilerinizi görüntülemek, güncellemek veya silinmesini talep etmek için aşağıdaki veri sahibi başvuru portalını kullanabilirsiniz.

KVKK Veri Sahibi Başvuru Portalı: {_link()}

Saygılarımızla,
{_marka()} Kişisel Verilerin Korunması Birimi""",

    lambda: f"""{_unvan()} {_isim()},

Avrupa Birliği Genel Veri Koruma Tüzüğü (GDPR) kapsamında üye olduğunuz platformun veri işleme politikaları güncellenmiştir. Yeni politikaları onaylamanız halinde hizmetlerimizden yararlanmaya devam edebilirsiniz.

Onay vermemeniz durumunda hesabınız {_tarih()} tarihi itibarıyla silinecek ve tüm verileriniz sistemden kaldırılacaktır. Onay için aşağıdaki bağlantıyı kullanabilirsiniz.

Veri İşleme Onay Formu: {_link()}

Saygılarımızla,
Veri Koruma ve Gizlilik Birimi""",
]


PHISHING_GRUPLARI = [
    FINANSAL, KIMLIK, KOTU_LINK, ODUL,
    KARGO_P, MARKA_TAKLIT, SAHTE_IS, SAHTE_SIGORTA, SAHTE_DEVLET,
    SAHTE_TATIL, SAHTE_EGITIM, SAHTE_BAGIS,
    SAHTE_EMLAK, SAHTE_SAGLIK, SAHTE_KREDI, SAHTE_ARAC,
    SAHTE_SOSYAL, SAHTE_YAZILIM, SAHTE_HUKUK,
    SAHTE_YATIRIM, SAHTE_UYELIK, SAHTE_HEDIYE,
    SAHTE_ECZANE, SAHTE_RESMI, SAHTE_ENERJI,
    SAHTE_MUSTERI, SAHTE_KURUMSAL,
    SAHTE_SOSYAL_MEDYA, SAHTE_POLIS, SAHTE_OKUL,
    SAHTE_IS2, SAHTE_ANKET, SAHTE_KVKK,
]


def _uret_phishing() -> str:
    grup   = random.choice(PHISHING_GRUPLARI)
    sablon = random.choice(grup)
    return sablon()


def _uret_normal() -> str:
    sablon = random.choice(NORMAL)
    return sablon()


def generate(phishing_count: int = 25000, normal_count: int = 25000) -> list[dict]:
    rows = []
    for _ in range(phishing_count):
        rows.append({"body": _uret_phishing(), "label": 1})
    for _ in range(normal_count):
        rows.append({"body": _uret_normal(), "label": 0})
    random.shuffle(rows)
    return rows


def main() -> None:
    print("=" * 60)
    print("  TURKCE E-POSTA URETICI")
    print("  Her e-posta: selamlama + paragraf + imza")
    print("=" * 60)

    rows = generate(phishing_count=25000, normal_count=25000)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["body", "label"])
        writer.writeheader()
        writer.writerows(rows)

    phishing = sum(1 for r in rows if r["label"] == 1)
    normal   = len(rows) - phishing

    print(f"Uretildi  : {len(rows):,} e-posta  ->  {OUTPUT_PATH.name}")
    print(f"Phishing  : {phishing:,}")
    print(f"Normal    : {normal:,}")
    print()
    print("Sonraki adimlar:")
    print("  python src/prepare_dataset.py")
    print("  python src/train_model.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
