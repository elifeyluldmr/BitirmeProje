"""
Türkçe sentetik e-posta veri üreteci.
Çalıştır: python src/generate_turkish_data.py
"""

import random
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

random.seed(42)

# ── Değişken havuzları ────────────────────────────────────────────────────────

ISIMLER = [
    "Ahmet Yılmaz", "Fatma Kaya", "Mehmet Demir", "Ayşe Çelik", "Mustafa Şahin",
    "Zeynep Arslan", "Ali Öztürk", "Elif Aydın", "Hasan Doğan", "Merve Yıldız",
    "Emre Güneş", "Selin Koç", "Burak Polat", "Dilan Erdoğan", "Serkan Aslan",
    "Büşra Çavuş", "Kemal Güler", "Gamze Aksoy", "Okan Bulut", "Hülya Tekin",
    "Tarık Çetin", "Nurcan Bozkurt", "Volkan Şimşek", "Pınar Güven", "Caner Aktaş",
    "Sibel Yıldırım", "Murat Özdemir", "Ece Karaca", "Tolga Demirtaş", "Gül Sarı",
    "Berk Avcı", "Neslihan Tunç", "Furkan Özkan", "Derya Kılıç", "Uğur Çakır",
    "Serap Ateş", "Barış Korkmaz", "Tuğba Güngör", "Onur Başer", "Melis Yıldız",
    "Alper Şen", "Hatice Akın", "Çağlar Topal", "Arzu Kaplan", "Sinan Doğru",
    "Yasemin Kurt", "Koray Güler", "Sevda Arslan", "Erdem Öz", "Cansu Bilgin",
    "İbrahim Çalık", "Reyhan Tok", "Selçuk Yılmaz", "Deniz Aydoğan", "Özge Karataş",
    "Taner Aslan", "Filiz Koç", "Hakan Keskin", "Seda Çelik", "Cem Öztürk",
]

BANKALAR = [
    "Ziraat Bankası", "İş Bankası", "Garanti BBVA", "Akbank", "Yapı Kredi",
    "Halkbank", "Vakıfbank", "Denizbank", "QNB Finansbank", "TEB",
    "HSBC Türkiye", "ING Bank", "Şekerbank", "Fibabanka", "Odeabank",
]

KARGO_FIRMALARI = [
    "PTT Kargo", "Yurtiçi Kargo", "MNG Kargo", "Aras Kargo",
    "Sürat Kargo", "UPS Türkiye", "DHL Türkiye", "Fedex Türkiye",
    "Horoz Lojistik", "Sendeo", "Kolay Gelsin",
]

ETICARET_SITELERI = [
    "Trendyol", "Hepsiburada", "N11", "GittiGidiyor", "Amazon Türkiye",
    "Morhipo", "Boyner", "Zara Türkiye", "LC Waikiki", "Çiçeksepeti",
    "Sahibinden", "Letgo", "Dolap", "Kariyer.net", "Migros Sanal Market",
]

TECH_SIRKETLER = [
    "Google", "Apple", "Microsoft", "Meta", "Instagram",
    "Facebook", "Twitter/X", "LinkedIn", "Netflix", "Spotify",
    "Amazon", "Dropbox", "PayPal", "Zoom", "TikTok",
]

TUTARLAR = [
    "49,90 TL", "89,99 TL", "149,90 TL", "199,00 TL", "249,00 TL",
    "299,00 TL", "350,00 TL", "499,50 TL", "625,00 TL", "750,00 TL",
    "980,00 TL", "1.250,00 TL", "1.500,00 TL", "2.000,00 TL", "2.500,00 TL",
    "3.000,00 TL", "3.750,00 TL", "5.000,00 TL", "7.500,00 TL", "10.000,00 TL",
    "12.000,00 TL", "15.000,00 TL", "20.000,00 TL", "25.000,00 TL", "50.000,00 TL",
    "120,00 TL", "450,00 TL", "875,00 TL", "4.200,00 TL", "8.900,00 TL",
]

KARGO_NO = lambda: f"TR{random.randint(100000000, 999999999)}"
SIPARIS_NO = lambda: f"#{random.randint(10000000, 99999999)}"
TARIHLER = [
    "05.01.2025", "12.01.2025", "20.01.2025", "03.02.2025", "14.02.2025",
    "28.02.2025", "10.03.2025", "22.03.2025", "01.04.2025", "15.04.2025",
    "28.04.2025", "05.05.2025", "15.05.2025", "26.05.2025", "04.06.2025",
    "20.06.2025", "03.07.2025", "18.07.2025", "01.08.2025", "10.08.2025",
    "25.08.2025", "07.09.2025", "20.09.2025", "05.10.2025", "14.10.2025",
    "28.10.2025", "10.11.2025", "22.11.2025", "30.11.2025", "15.12.2025",
    "05.01.2026", "20.01.2026", "10.02.2026", "01.03.2026", "15.04.2026",
]
SAATLER = [
    "08:15", "08:51", "09:14", "09:45", "10:00", "10:29", "10:55",
    "11:20", "11:47", "12:10", "13:00", "13:22", "14:05", "14:30",
    "15:05", "15:45", "16:10", "16:38", "17:03", "17:30", "18:00",
]
IP_ADRESLERI = [
    "185.234.56.78", "91.107.34.21", "46.20.198.5", "178.62.55.33",
    "95.211.32.44", "212.58.197.11", "82.221.105.6", "109.74.193.98",
    "37.148.209.54", "5.26.145.33", "77.92.106.20", "194.165.16.11",
    "45.133.1.45", "103.21.244.0", "198.41.128.0", "31.13.65.36",
    "216.58.206.46", "142.250.74.46", "151.101.1.69", "104.26.10.0",
]
SAHTE_LINKLER = [
    "https://guvenli-dogrula.net/hesap",
    "https://bankagiris-turkiye.com/verify",
    "https://hesap-dogrulama.org/login",
    "https://odeme-onay.net/islem",
    "https://kargotakip-guncelle.com/paket",
    "https://edevlet-giris.net/dogrula",
    "https://vergiade-basvuru.org/form",
    "https://guvenlik-merkezi.net/onayla",
    "https://kimlik-dogrulama.com/giris",
    "https://acil-islem.net/hesap",
    "https://banka-guvenlik.org/verify",
    "https://hizli-odeme.net/islem",
    "https://sistem-guncelleme.com/kayit",
    "https://hesap-koruma.net/dogrula",
    "https://odeme-sistemi.org/giris",
    "https://guvenli-islem.net/onayla",
    "https://kripto-guvenlik.com/wallet",
    "https://destek-merkezi.net/form",
    "https://ucretsiz-hediye.org/talep",
    "https://piyango-kazan.net/odul",
]

# ── Yardımcı ─────────────────────────────────────────────────────────────────

def r(lst):
    return random.choice(lst)

def link():
    return r(SAHTE_LINKLER)

def tutar():
    return r(TUTARLAR)

def isim():
    return r(ISIMLER)

def tarih():
    return r(TARIHLER)

def saat():
    return r(SAATLER)

def ip():
    return r(IP_ADRESLERI)

# ══════════════════════════════════════════════════════════════════════════════
# PHİSHİNG ŞABLONLARI
# ══════════════════════════════════════════════════════════════════════════════

def _phishing_banka():
    banka = r(BANKALAR)
    templates = [
        f"Sayın {isim()}, {banka} hesabınıza {ip()} IP adresinden yetkisiz giriş denemesi tespit edilmiştir. Hesabınızı korumak için {tarih()} tarihine kadar kimliğinizi doğrulamanız zorunludur. Doğrulama için: {link()}",
        f"{banka} GÜVENLİK UYARISI: Kartınızda {tutar()} tutarında şüpheli işlem algılandı. İşlemi siz yapmadıysanız hesabınız askıya alınacaktır. Hemen doğrulayın: {link()}",
        f"Hesabınız geçici olarak kısıtlandı. {banka} güvenlik ekibimiz, {tarih()} tarihinde hesabınızda olağandışı aktivite tespit etti. 24 saat içinde bilgilerini güncellemeyen hesaplar kalıcı olarak kapatılacaktır. İşlem linki: {link()}",
        f"{banka} müşterisi olarak sistemi yenileme sürecinde kimlik doğrulamanızı tamamlamanız gerekmektedir. Doğrulama yapılmayan hesaplar {tarih()} itibarıyla erişime kapatılacaktır. Tıklayın: {link()}",
        f"DİKKAT: {banka} internet bankacılığı şifreniz {saat()} itibarıyla 3 kez yanlış girildi. Hesabınızın güvenliği için şifrenizi sıfırlamanız gerekmektedir: {link()}",
        f"{banka}'dan önemli bildirim: {tutar()} tutarında EFT işlemi gerçekleştirilmek üzere. Bu işlemi siz başlatmadıysanız aşağıdaki bağlantıdan iptal edin: {link()}",
        f"Sevgili müşterimiz, {banka} mobil uygulamanızın güvenlik sertifikası sona ermiştir. Hesabınıza erişim sağlamak için uygulamanızı {tarih()} tarihine kadar güncellemeniz gerekmektedir: {link()}",
        f"{banka} ACIL: Kredinizin son ödeme tarihi geçmiştir. {tutar()} borcunuz için hemen ödeme yapmazsanız yasal işlem başlatılacaktır. Ödeme linki: {link()}",
        f"Hesabınıza ekstra güvenlik katmanı eklenmesi zorunlu hale gelmiştir. {banka} olarak SMS doğrulamayı aktif etmenizi istiyoruz. Aktivasyon: {link()}",
        f"{banka}: Vergi iadesi başvurunuz onaylandı. {tutar()} tutarındaki iadenizi almak için bilgilerinizi güncellemeniz gerekmektedir: {link()}",
    ]
    return r(templates)


def _phishing_kargo():
    firma = r(KARGO_FIRMALARI)
    no = KARGO_NO()
    templates = [
        f"{firma}: {no} takip numaralı paketiniz gümrükte beklemektedir. {tutar()} gümrük vergisini ödemeden teslim gerçekleştirilemez. Ödeme için: {link()}",
        f"Paketiniz teslim edilemedi! {firma} - {no} numaralı gönderiniz için adres güncellemesi yapmanız gerekmektedir. Güncelleme linki: {link()}",
        f"{firma} BİLDİRİM: Kargonuz {tarih()} tarihinde 3. dağıtım denemesine çıkacaktır. Teslimat tercihlerinizi güncelleyin: {link()}",
        f"Önemli: {no} numaralı paketiniz hasar riskiyle karşı karşıya. {firma} olarak onayınızı almanız gerekiyor. Hemen tıklayın: {link()}",
        f"{firma}: Yurt dışından gelen paketiniz için ek belge gerekiyor. {tutar()} ücret karşılığında takas belgesi alabilirsiniz: {link()}",
        f"Kargonuz depodan iade edilmek üzere. {no} takip kodlu gönderinizi kurtarmak için {tarih()} tarihine kadar işlem yapın: {link()}",
        f"{firma} - Paketiniz dağıtıma çıktı fakat adresiniz eksik. Teslimat için adres doğrulaması gerekiyor: {link()}",
        f"Teslimat uyarısı: {no} kodlu paketiniz için gümrük onayı bekleniyor. {tutar()} vergisini ödeyerek işlemi tamamlayın: {link()}",
    ]
    return r(templates)


def _phishing_hesap_guvenligi():
    sirket = r(TECH_SIRKETLER)
    templates = [
        f"{sirket} Güvenlik Merkezi: Hesabınıza {ip()} adresinden {tarih()} {saat()} saatinde giriş yapıldı. Bu siz değilseniz şifrenizi hemen değiştirin: {link()}",
        f"Hesabınız askıya alındı! {sirket} kullanım koşullarını ihlal ettiğiniz tespit edildi. Hesabınızı kurtarmak için kimlik doğrulama yapın: {link()}",
        f"{sirket}: Şifrenizin süresi dolmak üzere. Hesabınıza erişimi kaybetmemek için {tarih()} tarihine kadar şifrenizi yenileyin: {link()}",
        f"Güvenlik uyarısı: {sirket} hesabınız bilinmeyen bir cihazdan açıldı. Hesabınızı korumak için iki faktörlü doğrulamayı etkinleştirin: {link()}",
        f"{sirket} destek ekibi: Hesabınızda anormal aktivite algılandı. 48 saat içinde kimliğinizi doğrulamazsanız hesabınız kalıcı olarak silinecektir: {link()}",
        f"Son uyarı: {sirket} hesabınız {tarih()} tarihinde devre dışı bırakılacak. Hesabınızı aktif tutmak için aşağıdaki adımları tamamlayın: {link()}",
        f"{sirket} bildirimi: Hesabınıza bağlı telefon numarası değiştirilmeye çalışıldı. Onaylamak veya engellemek için: {link()}",
        f"Kritik uyarı: {sirket} hesabınız hacklenmiş olabilir. Güvenliğiniz için parolanızı acilen sıfırlayın: {link()}",
        f"{sirket}: Hesabınıza giriş yapan {ip()} IP adresi kara listede. Güvenliğiniz için hesabınızı doğrulayın: {link()}",
        f"{sirket} güvenlik bildirimi: Hesabınızdan {tutar()} değerinde işlem gerçekleştirilmek isteniyor. Onaylamak veya reddetmek için: {link()}",
    ]
    return r(templates)


def _phishing_odul():
    templates = [
        f"Tebrikler {isim()}! {r(ETICARET_SITELERI)} yılsonu çekilişinde {tutar()} değerinde hediye kazandınız. Ödülünüzü talep etmek için son 24 saatiniz var: {link()}",
        f"Seçildiniz! Haftalık çekilişimizde isminiz belirlendi. {tutar()} nakit ödülünüzü almak için bilgilerinizi doğrulayın: {link()}",
        f"KAZANAN SİZSİNİZ: Piyango çekilişinde büyük ikramiyeyi kazandınız. {tutar()} tutarındaki ödülünüzü talep edin: {link()}",
        f"Özel anket katılımı için teşekkürler! {tutar()} değerinde alışveriş çeki kazandınız. Kodunuzu almak için: {link()}",
        f"Sizi özel müşterilerimizden biri olarak belirledik. Ücretsiz {tutar()} değerinde ürün hediyenizi talep edin: {link()}",
        f"{r(TECH_SIRKETLER)} kullanıcı memnuniyeti anketini doldurduğunuz için {tutar()} değerinde hediye çeki kazandınız: {link()}",
        f"500.000. ziyaretçi sizsiniz! Web sitemizi ziyaret ettiğiniz için {tutar()} nakit ödül kazandınız. Hemen talep edin: {link()}",
        f"Tebrikler! Sosyal medya yarışmamızın büyük ödülü {tutar()} sizin oldu. 48 saat içinde talep etmezseniz ödül başka bir kişiye aktarılacak: {link()}",
    ]
    return r(templates)


def _phishing_fatura():
    templates = [
        f"ÖDEME UYARISI: {tutar()} tutarındaki faturanızın son ödeme tarihi {tarih()} olup geçmiştir. Gecikme faizi uygulanmadan önce ödemenizi gerçekleştirin: {link()}",
        f"Elektrik faturanız ödenmedi. {tutar()} borcunuz nedeniyle {tarih()} tarihinde aboneliğiniz kesilecektir. Ödeme için: {link()}",
        f"Doğalgaz hesabınızda {tutar()} gecikmiş ödeme bulunmaktadır. Kesinti işlemine girmemek için bugün ödeyin: {link()}",
        f"Vergi borcunuz hakkında: Gelir İdaresi kayıtlarına göre {tutar()} vergi borcunuz bulunmaktadır. Cezasız ödeme için son gün {tarih()}: {link()}",
        f"SGK prim borcunuz: {tutar()} tutarındaki piriminiz ödenmemiştir. İşlem başlatılmadan önce ödemenizi tamamlayın: {link()}",
        f"Abonelik yenileme hatası: {r(TECH_SIRKETLER)} aboneliğiniz {tutar()} ödeme alınamadığı için askıya alındı. Ödeme bilgilerinizi güncelleyin: {link()}",
        f"Fatura ödemesi başarısız oldu. {tutar()} tutarındaki işleminiz reddedildi. Ödeme yönteminizi güncellemek için: {link()}",
        f"SON UYARI: {tutar()} tutarındaki borcunuz için icra işlemi başlatılmak üzere. Hemen ödeme yaparak süreci durdurun: {link()}",
    ]
    return r(templates)


def _phishing_devlet():
    templates = [
        f"e-Devlet Kapısı: Kimlik bilgilerinizin güncellenmesi zorunlu hale gelmiştir. {tarih()} tarihine kadar güncelleme yapılmayan hesaplar askıya alınacaktır: {link()}",
        f"Gelir İdaresi Başkanlığı: {tutar()} tutarında vergi iadesi hakkı doğmuştur. İadenizi almak için başvurunuzu tamamlayın: {link()}",
        f"SGK Bildirimi: Emeklilik hakkınız oluşmuştur. {tutar()} tutarındaki emeklilik ikramiyenizi almak için başvurun: {link()}",
        f"Trafik cezası bildirimi: Plakası kayıtlı araç sahipleri için {tutar()} tutarında trafik cezası bildirilmiştir. İtiraz veya ödeme için: {link()}",
        f"Nüfus Müdürlüğü: Kimlik kartınızın yenilenmesi gerekmektedir. Randevu almak ve işlemi başlatmak için: {link()}",
        f"Sağlık Bakanlığı: Zorunlu sağlık taramanızı {tarih()} tarihine kadar yaptırmanız gerekmektedir. Randevu için: {link()}",
        f"e-Devlet uyarısı: Hesabınıza yetkisiz erişim denemesi tespit edildi. Hesabınızı güvence altına almak için: {link()}",
        f"Vergi dairesi bildirimi: Beyan etmediğiniz {tutar()} gelir tespit edilmiştir. Cezai işlem başlamadan önce beyanda bulunun: {link()}",
        f"PTT: Adınıza tescilli kargo mevcut fakat adresiniz eksik. {tarih()} tarihine kadar bilgi güncellemezseniz iade edilecektir: {link()}",
        f"Mahkeme tebligatı: Aleyhinize açılan dava hakkında bilgilendirilmeniz gerekmektedir. Detaylar için: {link()}",
    ]
    return r(templates)


def _phishing_eticaret():
    site = r(ETICARET_SITELERI)
    templates = [
        f"{site}: {SIPARIS_NO()} numaralı siparişinizde sorun oluştu. {tutar()} iade işleminizi tamamlamak için hesap bilgilerinizi doğrulayın: {link()}",
        f"{site} GÜVENLİK: Hesabınıza {ip()} adresinden giriş yapıldı. Şüpheli ise hesabınızı hemen kilitleyin: {link()}",
        f"{site}: Hesabınızdaki {tutar()} değerinde hediye çeki {tarih()} tarihinde sona erecek. Kullanmak için tıklayın: {link()}",
        f"{site} Müşteri Hizmetleri: Siparişinizin iadesi onaylandı ancak banka bilgileriniz eksik. {tutar()} iadenizi almak için: {link()}",
        f"Acil: {site} hesabınız şüpheli aktivite nedeniyle donduruldu. Hesabınızı aktifleştirmek için kimlik doğrulama yapın: {link()}",
        f"{site}: VIP üyeliğiniz için {tutar()} ek indirim kazandınız. Kampanyadan yararlanmak için hesabınızı doğrulayın: {link()}",
        f"{site} bildirimi: Sepetinizdeki ürünlerin fiyatı düştü. {tutar()} tasarruf etmek için hemen satın alın: {link()}",
        f"{site}: Hesabınızın güvenliği için iki aşamalı doğrulamayı etkinleştirmeniz gerekmektedir. Aksi takdirde hesabınız kısıtlanacak: {link()}",
    ]
    return r(templates)


def _phishing_genel():
    templates = [
        f"Acil mesaj: Hesabınız tehlikede! {ip()} IP adresinden şüpheli giriş tespit edildi. Hemen işlem yapın: {link()}",
        f"Son dakika: {tutar()} tutarında ödeme talebiniz var. Onaylamak veya reddetmek için: {link()}",
        f"Parolanız sıfırlanmak üzere. Siz talep etmediyseniz aşağıdaki linke tıklayarak iptal edin: {link()}",
        f"Hesabınız {tarih()} tarihinde silinecek. Korumak için kimlik doğrulaması yapın: {link()}",
        f"Özel teklif süresi dolmak üzere! {tutar()} değerindeki avantajınızı kaçırmayın: {link()}",
        f"Bilgileriniz güncellenmemiş. {tarih()} tarihine kadar güncelleme yapmazsanız hizmetleriniz durabilir: {link()}",
        f"Şüpheli işlem tespit edildi: {saat()} saatinde {tutar()} tutarında işlem gerçekleştirildi. Onaylıyor musunuz? {link()}",
        f"Hesabınız doğrulanmamış. Doğrulama yapmadan servislerimizden yararlanamayacaksınız: {link()}",
    ]
    return r(templates)


# ══════════════════════════════════════════════════════════════════════════════
# NORMAL E-POSTA ŞABLONLARI
# ══════════════════════════════════════════════════════════════════════════════

def _normal_is_yazismasi():
    templates = [
        f"Merhaba, yarınki toplantı için hatırlatma yapıyorum. Saat 10:00'da konferans odasında buluşuyoruz. Gündem dosyasını ekledim, lütfen öncesinde inceleyebilir misin?",
        f"Selam, geçen haftaki projeyle ilgili güncelleme paylaşmak istedim. Tasarım aşaması tamamlandı, şimdi geliştirme sürecine geçiyoruz. Bu hafta içinde brief dökümanı göndereceğim.",
        f"Merhaba, {tarih()} tarihli raporunuzu aldım. Genel olarak iyi görünüyor, sadece 3. bölümdeki veriler için kaynak belirtmeniz yeterli olacak.",
        f"İyi günler, izin talebiniz onaylandı. {tarih()} - {tarih()} tarihleri arasında yıllık izninizi kullanabilirsiniz. İyi tatiller dilerim.",
        f"Merhaba ekip, sprint review toplantısı {tarih()} Cuma saat 14:00'te yapılacak. Katılım zorunludur. Zoom linki ayrıca gönderilecek.",
        f"Sayın {isim()}, CV'nizi inceledik ve sizi mülakata davet etmek istiyoruz. {tarih()} tarihinde uygun musunuz? Randevuyu onaylamanız için lütfen bu e-postaya yanıt verin.",
        f"Merhaba, aylık performans değerlendirme dönemine giriyoruz. Hedeflerinizi sisteme girmeniz için son tarih {tarih()}. Lütfen bölüm yöneticinizle görüşmeyi planlayın.",
        f"Bilgi için: Ofis klima sistemi {tarih()} tarihinde bakıma alınacak. O gün uzaktan çalışma opsiyonu mevcut.",
        f"Merhaba, proje bütçe onayı geldi. Toplam {tutar()} bütçeyle işe başlayabiliriz. Tedarikçi görüşmelerini bu hafta ayarlayalım.",
        f"Selam, müşteri sunumu için hazırladığın slaytu gördüm. Harika iş çıkarmışsın. Sadece son slayttaki grafiği biraz daha sade yapabilir misin?",
        f"Merhaba herkese, şirket pikniği {tarih()} tarihinde Belgrad Ormanı'nda yapılacak. Katılım formu yarın paylaşılacak.",
        f"Merhaba, staj başvurunuz olumlu değerlendirildi. {tarih()} tarihi itibarıyla ekibimize katılabilirsiniz. Detaylar için İK birimiyle iletişime geçin.",
        f"Bilgi notu: Sistem bakımı nedeniyle {tarih()} Cumartesi 02:00-06:00 saatleri arasında erişim kesintisi yaşanacak.",
        f"Merhaba, çeyrek raporunu hazırlamam için satış verilerini {tarih()} tarihine kadar gönderebilir misin?",
        f"Selam, yeni işe başlayan {isim()} için oryantasyon programı {tarih()} tarihinde başlıyor. Departman tanıtım sunumu için 15 dakikan var mı?",
    ]
    return r(templates)


def _normal_alisveris():
    site = r(ETICARET_SITELERI)
    templates = [
        f"{site}: {SIPARIS_NO()} numaralı siparişiniz hazırlanıyor. Tahmini teslimat {tarih()}. Siparişinizi takip etmek için uygulamamızı kullanabilirsiniz.",
        f"{r(KARGO_FIRMALARI)}: {KARGO_NO()} takip numaralı paketiniz {tarih()} tarihinde kargoya verildi. Bugün dağıtıma çıkması beklenmektedir.",
        f"{site} siparişiniz teslim edildi. Alışveriş deneyiminiz nasıldı? Değerlendirme yapmak birkaç dakikanızı alacak.",
        f"Satın alma işleminiz başarıyla tamamlandı. Sipariş numaranız: {SIPARIS_NO()}. Toplam tutar: {tutar()}. Faturanız e-posta ekinde yer almaktadır.",
        f"{site}: Takip listenizdeki ürün indirime girdi! {tutar()} olan ürün artık daha uygun fiyatta.",
        f"İadeniz onaylandı. {tutar()} tutarındaki iade işlemi 3-5 iş günü içinde kartınıza yansıyacaktır.",
        f"{site} üyelik yenileme bildirimi: Yıllık üyeliğiniz {tarih()} tarihinde otomatik yenilenecektir. Değişiklik yapmak isterseniz hesabım sayfasını ziyaret edin.",
        f"Favorilerinizden {SIPARIS_NO()} numaralı ürün stokta kaldı. Kaçırmamak için sepete ekleyebilirsiniz.",
    ]
    return r(templates)


def _normal_kisisel():
    templates = [
        f"Merhaba! Nasılsın? Uzun zamandır görüşemedik. Bu hafta sonu buluşmak ister misin? Cumartesi öğleden sonra müsaitim.",
        f"Selam, geçen haftaki doğum günü partisi çok güzeldi. Organizasyon için teşekkürler! Çektiğim fotoğrafları paylaşmak istedim.",
        f"Merhaba, taşınma haberinizi duydum. Yeni eviniz hayırlı olsun! Yerleşince uğramak isterim.",
        f"Selam, kitabı bitirdim ve harika buldum. Tavsiyene teşekkürler. Bir sonraki önerinizi bekliyorum.",
        f"Merhaba, dün akşam restoranı denedim. Haklıymışsın, gerçekten çok iyiydi. Bir dahaki sefere beraber gidebiliriz.",
        f"Selam! Konser biletlerini aldım. {tarih()} akşamı için hazır ol, çok eğlenceli geçecek.",
        f"Merhaba, annem seninle ilgili soruyor. Bayrama geliyor musun? Haber ver de ona bildireyim.",
        f"Selam, futbol maçı için planımız değişti mi? Hangi kafede izleyeceğiz? Arkadaşlara da haber vermem lazım.",
        f"Merhaba! Tebrikler, mezuniyet haberi çok sevindirdi. Kutlamak için bir yemek ayarlayalım mı?",
        f"Selam, kamerayı bir haftalığına ödünç alabilir miyim? Hafta sonu kamp fotoğrafı çekmek istiyorum.",
        f"Merhaba, annemin reçetesini göndereceğim dedim, unuttum. Şimdi yazıyorum: 2 su bardağı un, 3 yumurta, yarım litre süt...",
        f"Selam! Film listesini güncelliyorum. Yeni çıkan filmleri izledin mi? Önerin varsa paylaş.",
    ]
    return r(templates)


def _normal_haber_bulten():
    templates = [
        f"Teknoloji özeti: Bu haftanın en önemli gelişmeleri arasında yapay zeka alanındaki yeni araştırmalar ve elektrikli araç pazarındaki büyüme öne çıkıyor. Detayları okumak için bülteni açın.",
        f"Günlük haber özeti: Ekonomi gündeminde döviz hareketleri, iş dünyasında yeni yatırım kararları ve spor haberlerinde milli takım kampı haberleri yer alıyor.",
        f"Haftalık kültür-sanat bülteni: Yeni sinema filmleri, sanat galerileri ve müzik etkinlikleri bu haftaki önerilerimiz arasında. Detaylı program eklidir.",
        f"Dijital dönüşüm haberleri: Şirketlerin yapay zeka entegrasyonu hızlanıyor. Bu ayki raporumuzda sektör bazında dönüşüm istatistiklerine yer verdik.",
        f"Spor bülteni: Süper Lig'de heyecan dorukta. Bu hafta oynanan maçların sonuçları ve puan tablosu için bülteni inceleyin.",
        f"Finans bülteni: Piyasalar bu hafta oynaklığını korudu. Altın, döviz ve borsa gelişmeleri için haftalık analizimizi okuyun.",
        f"Yemek ve yaşam bülteni: Bu hafta mevsimlik tarifler, sağlıklı beslenme önerileri ve ev dekorasyonu ipuçları var.",
        f"Bilim ve teknoloji: Uzay araştırmalarındaki son gelişmeler, iklim değişikliğiyle mücadelede yeni projeler ve tıp dünyasından önemli bulgular bu sayıda.",
        f"Eğitim haberleri: Üniversite sınav takvimleri açıklandı. YKS, ALES ve yabancı dil sınavları için başvuru tarihleri bu bültenin ekinde yer almaktadır.",
        f"Girişimcilik ve kariyer: Bu haftaki bültenimizde başarılı girişimcilerle röportajlar, yeni iş fırsatları ve kariyer gelişimi için kaynaklar bulabilirsiniz.",
    ]
    return r(templates)


def _normal_bilgi_guncelleme():
    templates = [
        f"Sistemimiz {tarih()} tarihinde yeni özelliklerle güncellendi. Gizlilik politikamızdaki değişiklikleri incelemenizi öneririz.",
        f"Hizmet koşullarımız güncellendi. Önemli değişiklikler hakkında bilgi almak için hesabınıza giriş yaparak bildirimleri inceleyin.",
        f"Aylık hesap özetiniz hazır. {tarih()} - {tarih()} dönemine ait hareketlerinizi görüntülemek için hesabınıza giriş yapın.",
        f"Şifrenizi en son ne zaman değiştirdiniz? Hesap güvenliğinizi artırmak için 3 ayda bir şifre yenilemeni öneririz.",
        f"Merhaba, kullanıcı memnuniyeti anketimizi doldurmak için 5 dakikanızı ayırır mısınız? Görüşleriniz hizmetimizi geliştirmemize yardımcı oluyor.",
        f"Topluluk kurallarımız güncellendi. Güncel kuralları okumak ve onaylamak için profil sayfanızı ziyaret edin.",
        f"Hesabınızda kayıtlı telefon numarası güncel mi? Güvenlik bildirimlerini almaya devam etmek için iletişim bilgilerinizi doğrulayın.",
        f"Yeni uygulama sürümü yayınlandı. Bu güncellemede hız iyileştirmeleri ve küçük hata düzeltmeleri bulunuyor.",
    ]
    return r(templates)


# ── YENİ PHİSHİNG KATEGORİLERİ ───────────────────────────────────────────────

def _phishing_kripto():
    templates = [
        f"Kripto cüzdanınız risk altında! {tutar()} değerindeki varlıklarınız tehlikede. Cüzdanınızı kurtarmak için seed phrase'inizi doğrulayın: {link()}",
        f"Acil: {tutar()} değerinde kripto para transferi onay bekliyor. İşlemi onaylamak veya reddetmek için: {link()}",
        f"Tebrikler! Kripto airdrop'una seçildiniz. {tutar()} değerinde token hediyenizi talep etmek için cüzdanınızı bağlayın: {link()}",
        f"Borsanızdaki işlem doğrulaması gerekiyor. {tutar()} tutarındaki çekim işleminiz için kimliğinizi onaylayın: {link()}",
        f"Kripto yatırım platformu: Hesabınız {ip()} adresinden erişildi. Şüpheli ise varlıklarınızı hemen koruma altına alın: {link()}",
        f"DeFi platformundan acil bildirim: Likidite havuzunuzdaki {tutar()} değerindeki varlıklar {tarih()} tarihinde kilitlenecek. Çekmek için: {link()}",
        f"NFT çekilişi kazandınız! {tutar()} değerindeki NFT'nizi talep etmek için cüzdan adresinizi doğrulayın: {link()}",
        f"Bitcoin transferiniz askıya alındı. {tutar()} tutarındaki işlemin serbest bırakılması için kimlik doğrulama yapın: {link()}",
        f"Kripto borsası güvenlik uyarısı: Hesabınızdaki şüpheli aktivite nedeniyle çekim işlemleri durduruldu. Doğrulama için: {link()}",
        f"Özel yatırım fırsatı: Aylık %{random.randint(15,50)} getiri garantili kripto fona katılın. Ön kayıt için son gün {tarih()}: {link()}",
        f"Cüzdanınızın güvenlik sertifikası sona erdi. {tutar()} değerindeki kripto varlıklarınızı kaybetmemek için yenileyin: {link()}",
        f"Kripto swap işleminiz tamamlanamadı. {tutar()} tutarındaki işlemi tamamlamak için slippage ayarınızı güncelleyin: {link()}",
    ]
    return r(templates)


def _phishing_sahte_is():
    templates = [
        f"Uzaktan çalışma fırsatı! Günde 2-3 saat çalışarak aylık {tutar()} kazanın. Başvuru için: {link()}",
        f"İş başvurunuz değerlendirildi. Mülakat için {tarih()} tarihinde hazır olun. Onaylamak için: {link()}",
        f"Acil eleman aranıyor: Veri girişi operatörü. Tecrübe gerekmez, {tutar()} maaş. Başvurmak için bilgilerinizi doldurun: {link()}",
        f"Freelance proje teklifi: {tutar()} bütçeli, 2 haftalık proje için serbest çalışan arıyoruz. Detaylar için: {link()}",
        f"Yurt dışı iş fırsatı! Almanya'da {tutar()} maaşla çalışma vizesi. Ücretli uçak bileti dahil. Kayıt: {link()}",
        f"Müşteri temsilcisi aranıyor. Evden çalışma imkânı, {tutar()} maaş + prim. Başvuru formunu doldurun: {link()}",
        f"Sosyal medya yöneticisi iş ilanı: Ayda {tutar()} kazanın, sadece telefon yeterli. Detaylar: {link()}",
        f"Şirketimizin büyümesi nedeniyle {tutar()} maaşla muhasebe elemanı alıyoruz. CV göndermek için: {link()}",
        f"İş teklifiniz onaylandı. Sözleşmeyi imzalamak için {tarih()} tarihine kadar belgelerinizi gönderin: {link()}",
        f"Anket doldurun, {tutar()} kazanın! Günde 10 anket, 10 dakika ayırmanız yeterli: {link()}",
        f"Online eğitmen aranıyor. Uzmanlık alanınızda ders verin, saatlik {tutar()} kazanın: {link()}",
        f"Şirkete ortak ol: {tutar()} yatırımla kâr ortaklığı. Risk yok, güvenceli getiri. Detaylar: {link()}",
    ]
    return r(templates)


def _phishing_romantik():
    templates = [
        f"Merhaba, profilinizi gördüm ve tanışmak istedim. Ben şu an yurt dışında görevdeyim ama Türkiye'ye dönünce buluşabilir miyiz? Size küçük bir sürpriz göndermek istiyorum: {link()}",
        f"Size özel bir hediye gönderdim ama gümrükte takıldı. {tutar()} gümrük vergisini ödeyebilirseniz size ulaştırabilirim: {link()}",
        f"Merhaba, sosyal medyadan sizi takip ediyorum. Çok etkilendim. Size özel bir teklifim var, detaylar için: {link()}",
        f"Sevgili dostum, yurt dışındaki yatırımımdan {tutar()} komisyon geliyor ama hesabım donduruldu. Geçici olarak yardım eder misiniz? Geri ödeme garantili: {link()}",
        f"Uluslararası bir arkadaşlık sitesinden mesajım var. Türkiye'de biriyle tanışmak istiyorum. Profilimi görmek için: {link()}",
        f"Acil yardıma ihtiyacım var. Yurt dışında mahsur kaldım, {tutar()} göndersen eve dönebildikten sonra iade edebilirim: {link()}",
        f"Size özel video mesajı bıraktım. Görmek için profilinizi doğrulayın: {link()}",
        f"Uzun süredir yazışıyoruz, sizi gerçekten sevdim. Kavuşmak için uçak biletine {tutar()} eksik, yardımcı olabilir misiniz?",
    ]
    return r(templates)


def _phishing_sigorta():
    templates = [
        f"Kasko/trafik sigortanız sona eriyor. {tarih()} tarihine kadar yenileme yapmazsanız ceza alabilirsiniz. Hızlı yenileme: {link()}",
        f"Sağlık sigortanızdan {tutar()} geri ödeme hakkınız doğdu. İadenizi almak için başvurunuzu tamamlayın: {link()}",
        f"Hayat sigortası teklifiniz hazır: Aylık sadece {tutar()} prim ile {tutar()} teminatlı poliçe. Hemen başlayın: {link()}",
        f"Sigorta şirketiniz iflas etti! Poliçenizin geçerliliğini korumak için hemen transfer işlemi yapın: {link()}",
        f"Aracınız için hasar tazminatı onaylandı. {tutar()} tutarındaki ödemeyi almak için banka bilgilerinizi güncelleyin: {link()}",
        f"Zorunlu deprem sigortası (DASK) priminiz ödenmedi. {tarih()} tarihine kadar ödemezseniz poliçeniz iptal olacak: {link()}",
        f"Sağlık sigortanız kapsamı genişliyor! Ek prim ödemeden kanser teminatı eklemek için onaylayın: {link()}",
        f"Sigorta primlerinizde %{random.randint(20,60)} indirim kampanyası! Son başvuru tarihi {tarih()}: {link()}",
    ]
    return r(templates)


def _phishing_sosyal_medya():
    templates = [
        f"Hesabınız telif hakkı ihlali nedeniyle 24 saat içinde silinecek. İtiraz etmek için: {link()}",
        f"Takipçi sayınız düşüyor! Hesabınızı kurtarmak için doğrulama yapın: {link()}",
        f"Mavi tik başvurunuz onaylandı. Rozeti aktifleştirmek için kimliğinizi doğrulayın: {link()}",
        f"Hesabınız devre dışı bırakıldı. {tarih()} tarihine kadar itiraz etmezseniz kalıcı silinecek: {link()}",
        f"Viral içeriğiniz için telif talebi geldi. {tutar()} tazminat ödemeden önce itirazınızı bildirin: {link()}",
        f"Özel mesajınız spam olarak işaretlendi. Hesabınızın kısıtlanmaması için doğrulama yapın: {link()}",
        f"Hesabınıza {ip()} adresinden giriş yapıldı. Siz değilseniz hemen şifrenizi değiştirin: {link()}",
        f"Arkadaşınız sizi bir fotoğrafta etiketledi. Fotoğrafı görmek için giriş yapın: {link()}",
        f"Hesabınız yaş doğrulaması gerektiriyor. Doğrulama yapmadan içerik yükleyemezsiniz: {link()}",
        f"Profiliniz {random.randint(500,5000)} kişi tarafından görüntülendi bu hafta. Kim baktığını görmek için: {link()}",
    ]
    return r(templates)


# ── YENİ PHİSHİNG KATEGORİLERİ (2. TUR) ─────────────────────────────────────

def _phishing_teknik_destek():
    sirket = r(TECH_SIRKETLER)
    templates = [
        f"Microsoft Teknik Destek: Bilgisayarınızda virüs tespit edildi. Ücretsiz temizleme için şimdi arayın veya: {link()}",
        f"{sirket} destek ekibi: Cihazınız kötü amaçlı yazılım içeriyor. Uzaktan erişim ile temizleme için: {link()}",
        f"Güvenlik uyarısı: Windows lisansınız sona erdi. {tutar()} ödeyerek yenileyin, aksi hâlde bilgisayarınız kilitlenecek: {link()}",
        f"Teknik destek: {ip()} adresinden cihazınıza erişim sağlandı. Engelleme için uzman desteği alın: {link()}",
        f"UYARI: Tarayıcınız ele geçirildi. Hesap bilgilerinizi korumak için hemen teknik destek alın: {link()}",
        f"{sirket} güvenlik bildirimi: Yazılımınızın güncel olmaması nedeniyle {tutar()} zarara uğrayabilirsiniz. Ücretsiz güncelleme: {link()}",
        f"Apple Destek: iCloud depolama alanınız dolmak üzere. Verileriniz silinmeden önce planınızı yükseltin: {link()}",
        f"Antivirüs lisansınız sona erdi. Cihazınız korumasız! {tutar()} ile yenileyin: {link()}",
        f"Google Chrome güvenlik uyarısı: Şifreleriniz sızdırılmış olabilir. Kontrol etmek ve güvence altına almak için: {link()}",
        f"Uzak masaüstü bağlantı girişimi: {ip()} bilgisayarınıza bağlanmaya çalışıyor. Engellemek için hemen tıklayın: {link()}",
    ]
    return r(templates)


def _phishing_yatirim():
    templates = [
        f"Borsa fırsatı: Analistlerimizin önerdiği hisse senedi bu hafta %{random.randint(30,200)} değer kazandı. Hemen yatırım yapın: {link()}",
        f"Garantili getiri: {tutar()} yatırımla 3 ayda {tutar()} kazanın. Sınırlı kontenjan, son başvuru {tarih()}: {link()}",
        f"Altın yatırım platformu: Bugün {tutar()} yatırın, {tarih()} tarihinde {tutar()} geri alın. Güvenceli sistem: {link()}",
        f"Forex sinyali: Uzman ekibimizin analizleriyle günlük %{random.randint(5,20)} getiri. Ücretsiz deneme için kayıt: {link()}",
        f"Hisse senedi uyarısı: Portföyünüzdeki {tutar()} değer kaybetti. Zararı durdurmak için hemen işlem yapın: {link()}",
        f"VIP yatırım fırsatı: Sadece {random.randint(10,50)} kişilik özel fon. {tutar()} ile katılın, aylık %{random.randint(10,30)} getiri: {link()}",
        f"Kripto arbitraj botu: Otomatik alım-satım ile günde {tutar()} kazanın. Kurulum ücretsiz: {link()}",
        f"Emeklilik fonu teklifiniz hazır. {tutar()} aylık yatırımla güvenceli gelecek. Detaylar: {link()}",
        f"Borsa çöküyor! Uzmanlarımız {tutar()} değerindeki varlıklarınızı korumak için acil plan hazırladı: {link()}",
        f"Halka arz fırsatı: {r(['TechTR', 'NovaBist', 'AltınFon', 'KriptoBors'])} şirketi halka arzdan önce hisse alın. Son gün {tarih()}: {link()}",
    ]
    return r(templates)


def _phishing_tatil():
    templates = [
        f"Tebrikler! {r(['Antalya', 'Bodrum', 'Kapadokya', 'Maldivler', 'Dubai'])} tatili kazandınız. {tutar()} değerindeki paket için son 48 saat: {link()}",
        f"Uçak bileti kampanyası: {r(['İstanbul', 'Ankara', 'İzmir'])} - {r(['Londra', 'Paris', 'Roma', 'Dubai', 'Amsterdam'])} sadece {tutar()}. Koltuklar tükeniyor: {link()}",
        f"Otel rezervasyonunuzda sorun oluştu. {tarih()} tarihli rezervasyonunuzu korumak için ödeme bilgilerinizi güncelleyin: {link()}",
        f"Erken rezervasyon fırsatı: 5 yıldızlı otelde 7 gece {tutar()}. Bu fiyat sadece bugün geçerli: {link()}",
        f"Uçuşunuz iptal edildi. {tutar()} iade için banka bilgilerinizi girin: {link()}",
        f"Vize başvurunuz onaylandı. İşlemi tamamlamak için {tutar()} konsolosluk ücreti ödemeniz gerekiyor: {link()}",
        f"Tatil sigortanız için son gün. {tarih()} tarihli seyahatiniz için {tutar()} prim ödeyin: {link()}",
        f"Yolculuk ödülü: {random.randint(5000,50000)} mil puanınız var. Ücretsiz bilet almak için hesabınızı doğrulayın: {link()}",
    ]
    return r(templates)


def _phishing_kiralik():
    templates = [
        f"Kiralık daire ilanı: {r(['Kadıköy', 'Beşiktaş', 'Şişli', 'Bağcılar', 'Üsküdar'])} {random.randint(1,4)+1}+{random.randint(0,1)} daire, {tutar()} kira. Depozito yatırmak için: {link()}",
        f"Araç kiralama teklifi: 7 günlük {r(['SUV', 'sedan', 'minivan'])} kiralaması sadece {tutar()}. Rezervasyon için kart bilgilerinizi girin: {link()}",
        f"Daire rezervasyonunuz onaylandı. {tutar()} tutarındaki depozitoyu {tarih()} tarihine kadar yatırın: {link()}",
        f"Kiracı arıyoruz: Merkezi konumda eşyalı daire. İlk 3 ay {tutar()} indirim. Görüntüleme randevusu için: {link()}",
        f"Tatil evi kiralama: {r(['Çeşme', 'Fethiye', 'Sapanca', 'Abant'])} villa, haftalık {tutar()}. Kapora için: {link()}",
        f"Araç kiralama iptali: Rezervasyonunuz sistem hatası nedeniyle iptal edildi. {tutar()} iadenizi almak için: {link()}",
        f"İkinci el araç ilanı: {random.randint(2015,2022)} model {r(['Honda', 'Toyota', 'Ford', 'Renault', 'Volkswagen'])}, {tutar()} fiyat. Kapora için: {link()}",
        f"Ofis kiralama: {r(['Maslak', 'Levent', 'Ataşehir'])} açık ofis, aylık {tutar()}. Sözleşme için bilgilerinizi gönderin: {link()}",
    ]
    return r(templates)


def _phishing_kvkk():
    templates = [
        f"KVKK Uyarısı: Kişisel verileriniz 3. taraflarla paylaşıldı. Haklarınızı kullanmak için kimliğinizi doğrulayın: {link()}",
        f"TC Kimlik doğrulama zorunluluğu: {tarih()} itibarıyla kimlik doğrulaması yapılmayan hesaplar kısıtlanacak: {link()}",
        f"Veri ihlali bildirimi: Bilgileriniz sızdırılmış olabilir. Hesabınızı korumak için şimdi doğrulayın: {link()}",
        f"e-Devlet zorunlu güncellemesi: TC Kimlik numaranızı ve iletişim bilgilerinizi {tarih()} tarihine kadar güncelleyin: {link()}",
        f"Nüfus cüzdanı yenileme bildirimi: Yeni kimlik kartınızı almak için randevu oluşturun ve ön başvuruyu tamamlayın: {link()}",
        f"Dijital kimlik sistemi geçişi: {tarih()} tarihinden itibaren dijital kimlik zorunlu. Kayıt için: {link()}",
        f"Kişisel veri güncelleme talebi: Sistemimizde eksik bilgileriniz var. Tamamlamak için: {link()}",
        f"MASAK uyarısı: Mali bilgileriniz doğrulanmamış. Hesabınızın dondurulmaması için bilgilerinizi güncelleyin: {link()}",
    ]
    return r(templates)


# ── YENİ NORMAL KATEGORİLERİ ─────────────────────────────────────────────────

def _normal_saglik():
    templates = [
        f"Randevu hatırlatması: {tarih()} tarihinde saat {saat()}'de doktor randevunuz bulunmaktadır. İptal veya değişiklik için 0850 XXX XX XX numaralı hattı arayın.",
        f"Tahlil sonuçlarınız hazır. Sonuçlarınızı görmek için hastane portalına giriş yapabilir ya da doktorunuzla randevu alabilirsiniz.",
        f"Aşı hatırlatması: Grip aşısı mevsimi geldi. En yakın eczaneden veya aile hekiminizden aşınızı yaptırabilirsiniz.",
        f"Diş hekimi randevunuz {tarih()} tarihine alındı. Herhangi bir değişiklik için lütfen kliniğimizi arayın.",
        f"Sağlık taramanız için randevu aldınız. {tarih()} {saat()} - Kadıköy Devlet Hastanesi, İç Hastalıkları Polikliniği.",
        f"Reçeteniz eczaneye iletildi. İlaçlarınızı herhangi bir {r(['Seçkin', 'İstanbul', 'Gülhane', 'Lider'])} Eczanesi'nden alabilirsiniz.",
        f"Kontrol randevunuzu unutmayın! Son muayenenizden bu yana 6 ay geçti. Aile hekiminizle randevu almak için MHRS'yi kullanabilirsiniz.",
        f"Psikolog randevunuz onaylandı: {tarih()} {saat()}. Online görüşme için bağlantı bilgileri ayrıca gönderilecektir.",
        f"Kan tahlili için aç karnına gelmeniz gerekmektedir. {tarih()} sabahı su haricinde bir şey yemeyiniz.",
        f"Fizik tedavi seansınız {tarih()} günü saat {saat()}'de. Rahat kıyafet giymenizi öneririz.",
    ]
    return r(templates)


def _normal_okul():
    templates = [
        f"Veli toplantısı duyurusu: {tarih()} tarihinde saat {saat()}'de sınıf öğretmeninizle toplantı yapılacaktır. Lütfen katılım sağlayınız.",
        f"Öğrenci not bildirimi: {tarih()} tarihi itibarıyla dönem notları sisteme işlenmiştir. e-Okul üzerinden inceleyebilirsiniz.",
        f"Üniversite kaydınız tamamlandı. {tarih()} tarihinde oryantasyon programına katılmanız beklenmektedir. Detaylı program ekte sunulmuştur.",
        f"Burs başvuru sonuçları açıklandı. Başvurunuzun durumunu öğrenmek için öğrenci bilgi sistemine giriş yapınız.",
        f"Sınav programı güncellendi. {tarih()} tarihindeki sınav saat {saat()}'e alındı. Lütfen bilgilerinizi güncelleyiniz.",
        f"Mezuniyet töreni {tarih()} tarihinde gerçekleşecektir. Cübbe kiralama ve bilet işlemleri için öğrenci işleri birimiyle iletişime geçiniz.",
        f"Yurt başvuru dönemi açıldı. {tarih()} tarihine kadar başvurularınızı tamamlayabilirsiniz. Kontenjanlar sınırlıdır.",
        f"Staj başvurusu hatırlatması: Yaz stajı için son başvuru tarihi {tarih()}. Formu kariyer portalından indirebilirsiniz.",
        f"Ödev teslim tarihi yaklaşıyor: {tarih()} Cuma günü saat {saat()}'e kadar sisteme yüklemeniz gerekmektedir.",
        f"Dönem sonu sınav takvimi yayınlandı. {tarih()} - {tarih()} tarihleri arasında bütünleme sınavları yapılacaktır.",
        f"Ders kaydı dönemi başladı. {tarih()} tarihine kadar bir sonraki dönem derslerinizi seçmeniz gerekmektedir.",
        f"Kulüp etkinliği: Yazılım topluluğu olarak {tarih()} tarihinde hackathon düzenliyoruz. Katılmak isteyenler e-posta ile başvurabilir.",
    ]
    return r(templates)


def _normal_gercek_fatura():
    banka = r(BANKALAR)
    templates = [
        f"{banka} hesap ekstresi: {tarih()} - {tarih()} dönemi hesap özeti ekte sunulmuştur. Toplam {tutar()} harcama gerçekleşti.",
        f"Elektrik faturanız kesildi. {tarih()} son ödeme tarihli {tutar()} tutarındaki faturanızı şube, ATM veya internet bankacılığı ile ödeyebilirsiniz.",
        f"Doğalgaz faturası: {tarih()} - {tarih()} dönemine ait {tutar()} tutarındaki faturanız çıkarılmıştır.",
        f"İnternet abonelik yenileme: {tarih()} tarihinde {tutar()} tutarındaki aylık abonelik ücretiniz otomatik ödenecektir.",
        f"Telefon faturanız hazır. {tutar()} tutarındaki {tarih()} vadeli faturanızı operatör uygulaması üzerinden ödeyebilirsiniz.",
        f"Su faturası bildirimi: Bu dönem {tutar()} tutarında su faturanız oluştu. Ödeme için belirtilen son tarihe dikkat ediniz.",
        f"{banka} kredi kartı ekstresi: {tarih()} kesim tarihli ekstrenizde {tutar()} asgari ödeme tutarı bulunmaktadır.",
        f"Sigorta poliçe yenileme: {tarih()} tarihinde {tutar()} priminiz otomatik tahsil edilecektir. Değişiklik için şubenizi arayın.",
    ]
    return r(templates)


def _normal_sosyal_medya_gercek():
    templates = [
        f"Yeni takipçin var! {isim()} seni takip etmeye başladı. Profilini kontrol etmek için uygulamayı aç.",
        f"Gönderin beğenildi. Son paylaşımın {random.randint(10,500)} beğeni aldı.",
        f"Doğum günün kutlu olsun bildirimi: Bugün {isim()} arkadaşının doğum günü. Bir mesaj göndermek ister misin?",
        f"Anın hatırlatması: {random.randint(1,5)} yıl önce bugün bir anı paylaştın. Görmek ister misin?",
        f"Trend konular: Bugün gündemde olan {random.randint(3,10)} konu var. Takip ettiğin konulardaki gelişmeleri gör.",
        f"Grup daveti: {isim()} seni bir gruba davet etti. Daveti kabul etmek için uygulamayı aç.",
        f"Canlı yayın bildirimi: Takip ettiğin {isim()} şu an canlı yayında.",
        f"Haftalık özet: Bu hafta {random.randint(5,50)} yeni takipçi kazandın ve {random.randint(10,200)} beğeni aldın.",
        f"Yorum bildirimi: {isim()} gönderini yorumladı. Yanıtlamak ister misin?",
        f"Önerilen arkadaşlar: Tanıyor olabileceğin {random.randint(3,10)} kişi var. Bakmak ister misin?",
    ]
    return r(templates)


def _normal_seyahat():
    templates = [
        f"Uçuş hatırlatması: {tarih()} tarihli {r(['TK', 'PC', 'XQ'])} {random.randint(100,999)} sefer sayılı uçuşunuz için check-in açıldı. Web check-in yapabilirsiniz.",
        f"Otel rezervasyon onayı: {r(['Sheraton', 'Hilton', 'Marriott', 'Rixos', 'Swissôtel'])} - {tarih()} giriş, {tarih()} çıkış. Rezervasyon numaranız: {SIPARIS_NO()}",
        f"Seyahat sigortanız aktifleştirildi. {tarih()} - {tarih()} tarihleri arasındaki yolculuğunuz için poliçe numaranız: {SIPARIS_NO()}",
        f"Kiralık araç teslim hatırlatması: {tarih()} tarihinde {saat()}'de {r(['Avis', 'Budget', 'Hertz', 'Europcar'])} ofisinden aracınızı teslim alabilirsiniz.",
        f"Tur programı güncellendi: {tarih()} tarihli {r(['Kapadokya', 'Efes', 'Pamukkale', 'Nemrut'])} turunuza ait güncel program ekte sunulmuştur.",
        f"Seyahat sağlık sigortanız onaylandı. Poliçe detayları ve acil numaralar ekte yer almaktadır.",
        f"Valiz kayıp bildirimi çözüme kavuştu. Valiziniz {tarih()} tarihinde adresinize teslim edilecektir.",
        f"Müze kartınız {tarih()} tarihinde yenilendi. Türkiye genelinde tüm müzelere ücretsiz giriş hakkınız devam ediyor.",
        f"Hostel rezervasyonunuz onaylandı. {tarih()} tarihinde {saat()}'de check-in yapabilirsiniz. WiFi şifresi giriş sırasında verilecek.",
        f"Yurt dışı roaming paketi aktifleştirildi. {r(['Almanya', 'İtalya', 'İspanya', 'Fransa'])} seyahatiniz için {tutar()} paket tanımlandı.",
    ]
    return r(templates)


def _normal_spor():
    templates = [
        f"Spor salonu hatırlatması: Bugün antrenman gününüz! Saat {saat()}'deki {r(['yoga', 'pilates', 'crossfit', 'spinning', 'zumba'])} dersine kayıtlısınız.",
        f"Koşu kulübü etkinliği: {tarih()} Pazar sabahı saat {saat()}'de {r(['Maçka Parkı', 'Belgrad Ormanı', 'Yıldız Parkı'])} buluşması var. Katılıyor musun?",
        f"Spor izleme özeti: Bu hafta {random.randint(2,6)} antrenman yaptın, toplam {random.randint(1500,8000)} kalori yaktın. Harika gidiyorsun!",
        f"Maç hatırlatması: {tarih()} tarihinde {r(['Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'Trabzonspor'])} maçı var. Biletiniz onaylandı.",
        f"Fitness hedef bildirimi: {tarih()} tarihinde belirlediğin {r(['5 km koşu', '10 çekiş', '50 şınav'])} hedefine ulaştın. Tebrikler!",
        f"Beslenme planı güncellendi. Yeni haftalık programınız diyetisyeniniz tarafından hazırlandı, uygulamadan inceleyebilirsiniz.",
        f"Havuz sezon kartı yenileme: {tarih()} tarihinde kartınız sona eriyor. Yenileme için tesise uğrayabilirsiniz.",
        f"Turnuva kaydınız onaylandı. {tarih()} tarihli {r(['tenis', 'padel', 'masa tenisi', 'basketbol'])} turnuvası için fikstür ekte sunulmuştur.",
        f"Personal trainer randevunuz: {tarih()} {saat()} - {r(['Ahmet', 'Serkan', 'Kemal'])} hoca ile ölçüm ve program güncellemesi.",
        f"Spor mağazası siparişiniz hazır. Aldığınız {r(['koşu ayakkabısı', 'spor çantası', 'protein tozu', 'antrenman kıyafeti'])} teslim alınabilir.",
    ]
    return r(templates)


def _normal_apartman():
    templates = [
        f"Site yönetimi duyurusu: {tarih()} tarihinde asansör bakımı yapılacak. Sabah 09:00-12:00 saatleri arasında asansör kullanılamayacak.",
        f"Aidat hatırlatması: {tarih()} vadeli {tutar()} tutarındaki aidat ödemesini gerçekleştirmeyi unutmayın.",
        f"Su kesintisi bildirimi: {tarih()} tarihinde saat 08:00-14:00 arasında planlı su kesintisi uygulanacaktır.",
        f"Apartman toplantısı: {tarih()} tarihinde saat {saat()}'de kat malikleri kurulu toplantısı yapılacaktır. Gündem: çatı onarımı.",
        f"Güvenlik kamerası bildirimi: Ortak alanlarda yeni güvenlik kameraları kuruldu. Kamera konumları yönetim odasında mevcuttur.",
        f"Temizlik programı: {tarih()} tarihinde bina dış cephe temizliği yapılacak. Araçlarınızı park alanından çekmeniz rica olunur.",
        f"Deprem sigortası (DASK) toplu yenileme: Site yönetimimiz toplu DASK yenileme organizasyonu yapıyor. Katılmak için {tarih()} tarihine kadar bilgi verin.",
        f"Doğalgaz bakımı: {tarih()} tarihinde doğalgaz tesisat kontrolü yapılacak. Teknisyen saat 10:00-16:00 arasında kapınıza gelecek.",
        f"Çöp toplama saati değişti. Yeni düzenlemeyle çöpler her gün saat 20:00'dan itibaren toplanacaktır.",
        f"Ortak alan kullanım kuralları güncellendi. Yeni kurallar ilan panosuna asılmıştır, lütfen inceleyiniz.",
    ]
    return r(templates)


def _normal_evcil_hayvan():
    templates = [
        f"Veteriner randevu hatırlatması: {isim()}'in {tarih()} tarihinde saat {saat()}'de aşı randevusu var.",
        f"Evcil hayvan sağlık sigortası: {r(['köpeğinizin', 'kedinizin'])} yıllık sağlık kontrolü zamanı geldi. Veterinerinizle randevu alabilirsiniz.",
        f"Pet shop siparişiniz hazır. {r(['mama', 'kedi kumu', 'oyuncak', 'tasma'])} siparişiniz şubeye ulaştı, teslim alabilirsiniz.",
        f"Çip kaydı hatırlatması: {r(['köpeğinizin', 'kedinizin'])} kimlik çipi kaydının güncellenmesi gerekiyor. En yakın veterinere uğrayabilirsiniz.",
        f"Mama stok uyarısı: Düzenli sipariş verdiğiniz {r(['Hill\'s', 'Royal Canin', 'Purina', 'Whiskas'])} mama tükenmek üzere. Yeniden sipariş vermek ister misiniz?",
        f"Tırnak kesimi hatırlatması: {r(['köpeğinizin', 'kedinizin'])} son tırnak kesiminden 6 hafta geçti.",
        f"Barınak gönüllü etkinliği: {tarih()} Cumartesi sahipsiz hayvanları gezdirme etkinliğimize katılmak ister misiniz?",
        f"Veteriner raporu hazır: {r(['kan tahlili', 'röntgen', 'ultrason'])} sonuçları hazır. Kliniği arayarak öğrenebilirsiniz.",
    ]
    return r(templates)


def _normal_etkinlik():
    templates = [
        f"Konser hatırlatması: {tarih()} tarihinde {r(['Harbiye Açıkhava', 'Volkswagen Arena', 'KüçükÇiftlik Park'])} sahnesiyle {r(['Tarkan', 'Sezen Aksu', 'Haluk Levent', 'MFÖ'])} konseri var. Biletiniz onaylandı.",
        f"Tiyatro rezervasyonu: {tarih()} {saat()} - {r(['Kenter Tiyatrosu', 'Devlet Tiyatrosu', 'Şehir Tiyatroları'])} - {r(['Hamlet', 'Beklerken Godot', 'Çığlık'])} oyunu.",
        f"Festival biletiniz onaylandı: {tarih()} - {tarih()} tarihleri arasında {r(['İstanbul Müzik Festivali', 'Cappadox', 'Boğaziçi Film Festivali'])}.",
        f"Seminer davetiyesi: {tarih()} tarihinde {r(['yapay zeka', 'girişimcilik', 'finansal okuryazarlık', 'liderlik'])} konulu online seminere kayıt oldunuz.",
        f"Kitap fuarı hatırlatması: {tarih()} - {tarih()} tarihleri arasında {r(['TÜYAP', 'CNR'])} Kitap Fuarı başlıyor. Ücretsiz giriş, kayıt gerekmiyor.",
        f"Etkinlik iptal bildirimi: {tarih()} tarihli etkinlik hava koşulları nedeniyle {tarih()} tarihine ertelendi. Biletiniz geçerliliğini koruyor.",
        f"Sergi açılışı: {tarih()} tarihinde {r(['İstanbul Modern', 'Pera Müzesi', 'SALT Galata'])} yeni sergi açılıyor. Açılış etkinliğine davetlisiniz.",
        f"Workshop kaydınız onaylandı: {tarih()} tarihli {r(['fotoğrafçılık', 'seramik', 'yağlıboya', 'müzik'])} workshopuna katılıyorsunuz. Malzeme listesi ekte.",
    ]
    return r(templates)


def _normal_musteri_hizmetleri():
    templates = [
        f"Şikayetiniz alındı. {SIPARIS_NO()} numaralı başvurunuz incelemeye alındı. En geç {tarih()} tarihinde geri dönüş sağlanacaktır.",
        f"Memnuniyet anketimizi doldurduğunuz için teşekkür ederiz. Görüşleriniz hizmet kalitemizi artırmamıza yardımcı oluyor.",
        f"İade işleminiz tamamlandı. {tutar()} tutarındaki iade {tarih()} tarihinde kartınıza yansıyacaktır.",
        f"Teknik destek talebiniz çözüme kavuştu. Konuyla ilgili ek sorunuz olursa bize ulaşabilirsiniz.",
        f"Hesap güncelleme işleminiz başarıyla tamamlandı. Değişiklikler anında aktif oldu.",
        f"Abonelik iptal işleminiz alındı. {tarih()} tarihinden itibaren ücretlendirilmeyeceksiniz.",
        f"Ürün değişim talebiniz onaylandı. Yeni ürününüz {tarih()} tarihinde kargoya verilecektir.",
        f"Fatura itirazınız inceleniyor. Sonuç {tarih()} tarihine kadar bildirilecektir.",
        f"Kampanya başvurunuz onaylandı. {tutar()} indirim bir sonraki alışverişinizde geçerli olacak.",
        f"Üyelik yükseltme işleminiz tamamlandı. Yeni avantajlarınız hemen aktif oldu.",
    ]
    return r(templates)


def _normal_aile():
    templates = [
        f"Merhaba canım, bu hafta sonu gelecek misin? Annen çok özledi, yemek yapıyor. Haber ver.",
        f"Oğlum/Kızım, üniversite sınavı için başarılar diliyorum. Yanındayız, strese girme.",
        f"Abla/Kardeş, düğün hazırlıkları için {tarih()} günü buluşabilir miyiz? Kıyafet seçmeme yardım et.",
        f"Merhaba, amcanın {tarih()} doğum günü. Sürpriz yapmayı planlıyoruz, katılır mısın?",
        f"Sevgili annem, hastalığının geçtiğini duydum, çok sevindim. Yakında ziyarete geleceğim.",
        f"Kardeşim, arabayı bu hafta sonu ödünç alabilir miyim? Kısa bir yolculuk planlıyorum.",
        f"Çocuklar için hediye aldım, paket gelince açmayın. Sürpriz olsun!",
        f"Merhaba, ev arama sürecini biliyorsun. {r(['Kadıköy', 'Üsküdar', 'Beşiktaş'])} tarafında güzel bir daire bulduk. Ne düşünüyorsun?",
        f"Annemin ameliyatı başarıyla geçti. Şu an iyileşme sürecinde, endişelenme.",
        f"Bayram tatilinde ne yapıyorsunuz? Köye gidiyorsak erken çıkalım, yol kalabalık olur.",
        f"Kardeşim terhis oldu! {tarih()} günü karşılamaya gidiyoruz, sen de gel.",
        f"Torunumu okula kaydettirdim. İlk gün çok heyecanlandı, fotoğraf çektim gönderiyorum.",
    ]
    return r(templates)


def _normal_gunluk_yasam():
    templates = [
        f"Hava durumu uyarısı: Yarın {r(['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya'])} için {r(['yağmur', 'kar', 'fırtına', 'sis'])} bekleniyor. Dışarı çıkarken hazırlıklı olun.",
        f"Tarifim için teşekkürler! Keki denedim, gerçekten çok lezzetliydi. Bir dahaki buluşmada sana da yapacağım.",
        f"Komşudan not: Merdiven temizliği {tarih()} Cumartesi yapılacak. Kapı önündeki eşyaları içeri almanızı rica ederiz.",
        f"Araba bakımı hatırlatması: Aracınızın son yağ değişiminden {random.randint(8,15)}.000 km geçti. Bakım zamanı gelmiş olabilir.",
        f"Spor salonu üyeliğiniz {tarih()} tarihinde yenileniyor. {tutar()} tutarındaki ücret kayıtlı kartınızdan çekilecek.",
        f"Kitap kulübü toplantısı: {tarih()} Pazar saat {saat()}'de buluşuyoruz. Bu ay okuduğumuz kitap için notlarınızı getirmeyi unutmayın.",
        f"Market alışveriş listesi: Süt, ekmek, yumurta, domates, soğan, makarna, zeytinyağı, deterjan.",
        f"Otopark aboneliğiniz {tarih()} tarihinde sona eriyor. Yenileme için yönetim ofisine uğrayınız.",
        f"Terzi bildirimi: {isim()}, elbiseleriniz hazır. Hafta içi 09:00-19:00 saatleri arasında teslim alabilirsiniz.",
        f"Sevgili {isim()}, uzun zamandır haber alamadık. Nasılsın? Bir ara kahve içelim mi?",
    ]
    return r(templates)


# ══════════════════════════════════════════════════════════════════════════════
# VERİ ÜRETİCİ
# ══════════════════════════════════════════════════════════════════════════════

# ── YENİ PHİSHİNG KATEGORİLERİ (3. TUR) ─────────────────────────────────────

def _phishing_whatsapp():
    templates = [
        f"WhatsApp hesabınız başka bir cihaza taşınmak üzere. Onaylamıyorsanız doğrulama kodunuzu paylaşın: {link()}",
        f"Telegram güvenlik uyarısı: Hesabınıza {ip()} adresinden erişim sağlandı. Oturumu sonlandırmak için: {link()}",
        f"WhatsApp Business hesabınız askıya alındı. Yeniden aktifleştirmek için kimlik doğrulama yapın: {link()}",
        f"Arkadaşın seni bir gruba davet etti. Katılmak için bu linke tıkla: {link()}",
        f"WhatsApp: Hesabınızın depolama alanı doldu. Mesajlarınızı kaybetmemek için yedekleme yapın: {link()}",
        f"Telegram: Premium üyeliğiniz sona eriyor. Kesintisiz kullanmak için {tarih()} tarihine kadar yenileyin: {link()}",
        f"WhatsApp doğrulama: 6 haneli kodunuzu bu bağlantı üzerinden girin, aksi hâlde hesabınız kilitlenecek: {link()}",
        f"Mesajlaşma uygulamanız güvenlik açığı içeriyor. Güncellemek için: {link()}",
        f"WhatsApp grup yöneticisi değişti. Yeni kurallara uymak için onaylayın: {link()}",
        f"Telegram: {random.randint(10,50)} okunmamış mesajınız var ama hesabınız kısıtlandı. Erişmek için doğrulama yapın: {link()}",
    ]
    return r(templates)


def _phishing_bagis():
    templates = [
        f"Deprem yardım kampanyası: Afet bölgesindeki {random.randint(100,500)} aile yardım bekliyor. {tutar()} bağışınız hayat kurtarır: {link()}",
        f"Kanser hastası çocuk için yardım: Küçük {r(['Ahmet', 'Elif', 'Mehmet', 'Zeynep'])} ameliyat için {tutar()} muhtaç. Bağış yapmak için: {link()}",
        f"Hayvan barınağı acil yardım çağrısı: {random.randint(50,200)} hayvan aç ve hasta. {tutar()} bağışınızla fark yaratın: {link()}",
        f"Eğitime destek kampanyası: Köy çocuklarına kitap ve kırtasiye malzemesi. {tutar()} ile bir çocuğun geleceğine yatırım yapın: {link()}",
        f"Yetimhane desteği: {random.randint(20,100)} yetim çocuk sizin yardımınızı bekliyor. Bu ay {tutar()} bağışla onların yanında ol: {link()}",
        f"Mülteci yardım kampanyası: Yardıma muhtaç ailelere gıda ve giysi ulaştırıyoruz. Katkı için: {link()}",
        f"Hastalıklı köpek tedavisi için acil bağış: Veteriner ücreti {tutar()}. Katkıda bulunmak için: {link()}",
        f"Sel felaketi yardımı: {r(['Kastamonu', 'Sinop', 'Rize'])} bölgesinde {random.randint(100,1000)} aile evini kaybetti. Acil yardım: {link()}",
    ]
    return r(templates)


def _phishing_opertor():
    templates = [
        f"{r(['Turkcell', 'Vodafone', 'Türk Telekom'])} faturanızda hata tespit edildi. {tutar()} fazla ücret kesildi, iadenizi almak için: {link()}",
        f"Hat sahibi değişikliği talebi alındı. Numaranızı korumak istiyorsanız {tarih()} tarihine kadar itiraz edin: {link()}",
        f"{r(['Turkcell', 'Vodafone', 'Türk Telekom'])}: {tutar()} değerinde ücretsiz paket kazandınız. Aktifleştirmek için: {link()}",
        f"Numaranız başka bir operatöre taşınmak üzere. Engellemek için kimliğinizi doğrulayın: {link()}",
        f"Faturanız ödenmedi, hattınız {tarih()} tarihinde kapatılacak. Ödeme için: {link()}",
        f"Operatör güncelleme zorunluluğu: SIM kartınız yeni nesil eSIM ile değiştirilmeli. Ücretsiz değişim için: {link()}",
        f"{r(['Turkcell', 'Vodafone', 'Türk Telekom'])} sizi VIP müşteri olarak seçti. {tutar()} değerinde özel paket için: {link()}",
        f"Hattınıza erişim engellendi. Kimlik doğrulama yaparak erişiminizi yeniden açın: {link()}",
    ]
    return r(templates)


def _phishing_hukuki():
    templates = [
        f"Hukuki ihtar: Aleyhinize {tutar()} tutarında dava açılmıştır. Uzlaşma için {tarih()} tarihine kadar iletişime geçin: {link()}",
        f"İcra takibi başlatıldı: {tutar()} borcunuz için icra dairesi işlem başlattı. Durdurma talebi için: {link()}",
        f"Avukatlık bürosundan bildirim: Müvekkilimiz adına {tutar()} tazminat talebinde bulunulmuştur. Detaylar: {link()}",
        f"Mahkeme celbi: {tarih()} tarihinde duruşmaya katılmanız zorunludur. Gelmemeniz hâlinde gıyabi karar çıkarılacaktır: {link()}",
        f"Telif hakkı ihlali: Paylaştığınız içerik nedeniyle {tutar()} tazminat davası açılmıştır. İtiraz için: {link()}",
        f"Vergi incelemesi: Gelir İdaresi kayıtlarınızı incelemek istiyor. İşbirliği yapmazsanız cezai yaptırım uygulanacak: {link()}",
        f"Kara para aklamadan soruşturma: Hesabınızdaki hareketler şüpheli bulundu. Savunmanızı sunmak için: {link()}",
        f"Miras davası: Adınıza yurt dışından {tutar()} miras kaldı. Almak için hukuki işlemleri başlatın: {link()}",
    ]
    return r(templates)


# ── YENİ NORMAL KATEGORİLERİ (3. TUR) ────────────────────────────────────────

def _normal_hobi():
    templates = [
        f"Fotoğraf kulübü toplantısı: {tarih()} Cumartesi saat {saat()}'de buluşuyoruz. Bu ay konumuz uzun pozlama teknikleri. Tripodunu getirmeyi unutma.",
        f"Oyun grubu güncelleme: Yeni sezonda {r(['Catan', 'Wingspan', 'Azul', 'Ticket to Ride', 'Pandemic'])} oynayacağız. {tarih()} akşamı müsait misin?",
        f"Gitar dersi hatırlatması: {tarih()} {saat()} - Bu hafta {r(['barre akorlar', 'fingerpicking', 'blues scale', 'pentatonik'])} çalışıyoruz.",
        f"Kitap tavsiyesi: Bu ay okuduğum {r(['Tutunamayanlar', 'Şeker Portakalı', 'Kürk Mantolu Madonna', 'İnce Memed'])} gerçekten harikaydı, kesinlikle oku.",
        f"Bahçecilik ipucu: Şu sıralar {r(['domates', 'biber', 'patlıcan', 'salatalık'])} fideleri dikmek için ideal zaman. Toprak nemli olsun.",
        f"Satranç kulübü: {tarih()} günü turnuva var. Kayıt için bana yazabilirsin, kontenjan dolmadan yetişelim.",
        f"Resim kursu ödev teslimi: {tarih()} tarihine kadar natürmort çalışmamızı WhatsApp grubuna yükleyelim.",
        f"Koşu kulübü mesafe güncellemesi: Bu hafta toplam {random.randint(20,80)} km koştuk. {isim()} bu haftanın birincisi, tebrikler!",
        f"Yoga dersi yer değişikliği: Bu haftadan itibaren ders {r(['parkta', 'sahilde', 'yeni stüdyoda'])} yapılacak. Ayrıntılar için mesaj at.",
        f"Dil öğrenme grubu: Bu hafta {r(['İspanyolca', 'Almanca', 'Japonca', 'İtalyanca'])} B1 seviyesi alıştırmalar. Zaman bulursan düşün.",
    ]
    return r(templates)


def _normal_online_kurs():
    templates = [
        f"Kurs ilerleme bildirimi: {r(['Python Programlama', 'Veri Bilimi', 'Web Tasarım', 'Dijital Pazarlama'])} kursunda %{random.randint(30,90)} tamamladınız. Devam edin!",
        f"Yeni ders yüklendi: {r(['Makine Öğrenmesi', 'React', 'Photoshop', 'SEO'])} kursunuzda yeni bölüm mevcut. Hemen izleyin.",
        f"Sertifikanız hazır! {r(['SQL Temelleri', 'Proje Yönetimi', 'İngilizce B2'])} kursunu başarıyla tamamladınız. Sertifikanızı indirin.",
        f"Canlı ders hatırlatması: {tarih()} {saat()}'de {r(['eğitmeniniz', 'hocamız'])} ile canlı oturum var. Zoom linkini kontrol edin.",
        f"Ödev son gün: {r(['Algoritma', 'Veri tabanı', 'UI/UX tasarım'])} ödevini {tarih()} tarihine kadar teslim etmeyi unutmayın.",
        f"Kurs kampanyası: İlgilendiğiniz {r(['iOS Geliştirme', 'Blockchain', 'Siber Güvenlik'])} kursu %{random.randint(40,80)} indirimde.",
        f"Grup projesi eşleşmesi: {r(['Proje Yönetimi', 'Startup Kurma', 'UX Araştırma'])} kursunda takım arkadaşlarınız belirlendi.",
        f"Quiz sonucu: {r(['JavaScript', 'Veri Analizi', 'İngilizce Gramer'])} testinde {random.randint(60,100)}/100 aldınız. Tekrar etmek için önerilen konular ekte.",
    ]
    return r(templates)


def _normal_araba_servis():
    templates = [
        f"Araç servis randevusu hatırlatması: {tarih()} {saat()} - {r(['Toyota', 'Ford', 'Renault', 'Honda', 'Volkswagen'])} yetkili servisi. Periyodik bakım.",
        f"Servis tamamlandı: Aracınız hazır. Toplam {tutar()} tutarındaki işlem tamamlandı. Mesai saatleri içinde teslim alabilirsiniz.",
        f"Muayene hatırlatması: Aracınızın muayene tarihi {tarih()}. En yakın muayene istasyonuna randevu alabilirsiniz.",
        f"Sigorta yenileme: Aracınızın kasko/trafik sigortası {tarih()} tarihinde sona eriyor. Yenileme için sigorta acentenizi arayın.",
        f"Araç muayene sonucu: Araç muayenenizden geçti. Muayene belgesi {random.randint(1,3)} yıl geçerlidir.",
        f"Lastik mevsimi: Kış lastikleri takma zamanı geldi. {tutar()} değerinde lastik kampanyamız için servisi arayın.",
        f"Egzoz muayenesi başarısız: Aracınız egzoz testinden geçemedi. Bakım için servise uğrayın, aksi hâlde para cezası alabilirsiniz.",
        f"Trafik sigortası bildirimi: {tarih()} tarihli poliçeniz yenilendi. Yeni poliçe numaranız {SIPARIS_NO()}.",
    ]
    return r(templates)


def _normal_yemek():
    templates = [
        f"Yemek tarifi önerisi: Bugün {r(['mercimek çorbası', 'karnıyarık', 'mantı', 'lahmacun', 'iskender'])} yapmayı denedim, tarifi paylaşayım mı?",
        f"Restoran rezervasyonu onaylandı: {tarih()} {saat()} - {random.randint(2,8)} kişilik masa, {r(['Nusr-et', 'Hamdi', 'Çiya Sofrası', 'Borsam Taş Fırın'])}.",
        f"Yemek sipariş takibi: {SIPARIS_NO()} numaralı siparişiniz hazırlanıyor. Tahmini teslimat {random.randint(20,45)} dakika.",
        f"Haftalık yemek planı hazır. Bu haftanın menüsü: Pazartesi mercimek, Salı tavuk, Çarşamba sebzeli makarna, Perşembe balık, Cuma köfte.",
        f"Kafe buluşması: Yarın öğlen {r(['Starbucks', 'Gloria Jeans', 'Kahve Dünyası', 'Komşu Kafe'])} buluşalım mı? Saat {saat()} uyar mı?",
        f"Yemek grubu etkinliği: Bu ay {r(['Japon', 'İtalyan', 'Meksika', 'Hint'])} mutfağını keşfediyoruz. {tarih()} akşamı rezervasyon yaptım.",
        f"Pazar pazarı alışverişi: Bugün {r(['Kadıköy', 'Beşiktaş', 'Salı Pazarı'])} pazarında taze sebze ve meyve aldım. Hafta içi daha ucuz olduğunu hatırla.",
        f"Catering hizmeti teklifi: {tarih()} günkü {random.randint(20,100)} kişilik etkinliğiniz için menü ve fiyat teklifi ektedir.",
    ]
    return r(templates)


def _normal_is_arkadaslari():
    templates = [
        f"Selam, toplantı saati değişti mi? Takvimde {saat()} yazıyor ama bir mesaj geldi. Kontrol eder misin?",
        f"Merhaba, patronun senden raporu bugün istedi galiba. Bilgin var mı? Ben de göndereceğim için sormak istedim.",
        f"Çay molasında görüşelim mi? Proje ile ilgili iki dakikalık bir şey sormak istiyorum.",
        f"Yarınki sunum için slaytı ben mi hazırlıyorum yoksa sen mi? Net değil, açıkla lütfen.",
        f"Akşam ekip yemeği var, geliyor musun? {r(['Mecidiyeköy', 'Taksim', 'Kadıköy'])} taraflarında bir yer seçtik.",
        f"Müşteriyle toplantı {tarih()}'e ertelendi. Ajandana ekledin mi?",
        f"Yeni işe başlayan {isim()} için memnuniyet e-postası atmayı düşünüyorum, uygun olur mu?",
        f"Kargo geldi mi? Ofise bir şey sipariş etmiştim, görürsen beni haberdar et.",
        f"Bu hafta sonu takım buluşması yapıyor muyuz yoksa iptal mi? Evet ise yer ayarlayayım.",
        f"Proje sunumunu izledim, gerçekten çok iyiydi. Özellikle analiz kısmı etkileyiciydi, tebrikler.",
    ]
    return r(templates)


def _normal_kutlama():
    templates = [
        f"Doğum günün kutlu olsun! Sağlıklı, mutlu ve başarılarla dolu nice yıllara. Seni çok seviyoruz.",
        f"Yeni işin için tebrikler! Harika bir kariyer adımı, hakkını sonuna kadar kullanacağını biliyorum.",
        f"Nikahınız hayırlı olsun! Mutlu, sağlıklı ve uzun ömürlü bir birliktelik dileriz.",
        f"Mezuniyetin kutlu olsun! Yıllarca emek verdin, bu başarı çok hak edilmişti. Gurur duyuyoruz.",
        f"Bebeğiniz sağlıklı dünyaya geldi, tebrikler! Yeni aile üyeniz ve siz sağlıcakla büyüyün.",
        f"Sınavı kazandığına çok sevindim! Harcadığın emek boşa gitmedi, harika bir haber bu.",
        f"Ev aldığın için tebrikler! Yeni yuvanız hayırlı, uğurlu olsun. Taşınınca ziyarete geleceğiz.",
        f"Terfi haberin çok güzeldi! Emeklerinin karşılığını aldın, bundan sonrası daha iyi olacak.",
        f"Projeniz ödül aldı, harika iş çıkardınız! Tüm ekip adına tebrikler.",
        f"Emekliliğin kutlu olsun! Uzun yıllar boyunca çok güzel işler yaptın, iyi dinlenmeyi hak ettin.",
    ]
    return r(templates)


# ── YENİ PHİSHİNG KATEGORİLERİ (4. TUR) ─────────────────────────────────────

def _phishing_ceo_fraud():
    templates = [
        f"Merhaba, ben şirket CEO'suyum. Acil bir ödeme yapmam gerekiyor ama sistemlerim çalışmıyor. {tutar()} tutarını bu IBAN'a gönderir misiniz? Bugün içinde olması şart.",
        f"Yönetim kurulu toplantısındayım, telefona bakamıyorum. {tutar()} tutarında gizli bir transfer yapılması gerekiyor. Detaylar için: {link()}",
        f"Finans müdürüne acil: Tedarikçimiz {tutar()} bekliyor, ödemeyi bugün tamamlayın. Normal süreci atlamak zorundayız, üst yönetim onayladı.",
        f"Bu ödemeyi kimseyle paylaşmayın, gizli kalması şart. {tutar()} tutarını şu hesaba aktarın, denetim sürecinden önce kapatalım: {link()}",
        f"Avukatımız acil ödeme istiyor. {tutar()} tutarında havale yapılmasını onaylıyorum. İBAN bilgisi için: {link()}",
        f"Stratejik satın alma sürecindeyiz. {tutar()} tutarında gizli ön ödeme gerekiyor. Muhasebe bilmesin, direkt bana bildirin: {link()}",
        f"Vergi incelemesinden kaçınmak için {tutar()} nakdi bugün aktarmamız lazım. Güvenilir hesap bilgisi için: {link()}",
        f"Şirket adına yurt dışı transfer yapılacak. {tutar()} için SWIFT kodu ve IBAN'ı şu adresten alın: {link()}",
    ]
    return r(templates)


def _phishing_sahte_polis():
    templates = [
        f"Emniyet Müdürlüğü: Adınıza suç duyurusunda bulunuldu. {tarih()} tarihinde ifade vermek üzere karakola gelin ya da avukatınıza danışın: {link()}",
        f"Siber Suçlar Birimi: Cihazınızda yasadışı içerik tespit edildi. Kovuşturmadan muaf olmak için {tutar()} idari para cezasını ödeyin: {link()}",
        f"Savcılık tebligatı: {SIPARIS_NO()} numaralı soruşturma kapsamında bilgilerinize ihtiyaç duyulmaktadır. Başvuru için: {link()}",
        f"İnternette paylaştığınız içerik yasaları ihlal ediyor. Dava açılmadan uzlaşma için {tutar()} ödeme yapın: {link()}",
        f"Mali Suçları Araştırma Kurulu: Hesabınız kara para aklamayla ilişkilendirildi. Hesabınızı temize çıkarmak için bilgilerinizi doğrulayın: {link()}",
        f"Jandarma Komutanlığı: Aracınız hız ihlali nedeniyle {tutar()} ceza almıştır. Ödeme için son gün {tarih()}: {link()}",
        f"Mahkeme tebligatı: Gıyabi yargılanmak istemiyorsanız {tarih()} tarihine kadar başvurun: {link()}",
        f"Vergi kaçakçılığı soruşturması: {tutar()} vergi borcunuzu ödemezseniz mal varlığınıza el konulacak: {link()}",
    ]
    return r(templates)


def _phishing_sahte_ilac():
    templates = [
        f"Mucize zayıflama hapı: 30 günde {random.randint(5,20)} kg verin, garanti! İlk sipariş {tutar()} indirimli: {link()}",
        f"Diyabet ilacı stokta! Eczanelerde bulunamayan {r(['Ozempic', 'Metformin', 'insülin'])} alternatifi, {tutar()} kargo dahil: {link()}",
        f"Eklem ağrısına bitkisel çözüm: {random.randint(3,7)} günde ağrılarınız geçiyor, klinik testli: {link()}",
        f"Saç dökülmesine kesin çözüm: {random.randint(1,3)} aylık kullanımda görünür sonuç. {tutar()} kampanya fiyatı: {link()}",
        f"Kolesterol ve tansiyon için doğal takviye: İlaçsız tedavi mümkün. {tutar()} başlangıç paketi: {link()}",
        f"COVID sonrası yorgunluk için özel formül: Hekimler tavsiye ediyor, {tutar()} fiyata sipariş verin: {link()}",
        f"Kanser önleyici bitkisel kür: ABD'de patent almış formül, Türkiye'de ilk kez satışta. {tutar()}: {link()}",
        f"Güçlü uyku ilacı reçetesiz satışta! {tutar()} indirimli fiyata, kapıya teslimat: {link()}",
        f"Cinsel güç artırıcı bitkisel ürün: Yan etkisiz, {random.randint(100,1000)} kullanıcı tarafından doğrulandı. {tutar()}: {link()}",
    ]
    return r(templates)


def _phishing_sahte_yazilim():
    templates = [
        f"Windows lisansınız süresi doldu. {tutar()} ödeyerek orijinal lisansınızı yenileyin, aksi hâlde bilgisayarınız kilitlenecek: {link()}",
        f"Microsoft Office 2024 orijinal lisansı {tutar()}! Aktivasyon anahtarı anında e-posta ile gönderilir: {link()}",
        f"Adobe Creative Cloud yıllık abonelik {tutar()} (orijinal fiyatın %{random.randint(60,90)} altında). Sınırlı stok: {link()}",
        f"Antivirüs yazılımınız süresi doldu. Cihazınızı korumak için {tutar()} ile yenileyin: {link()}",
        f"VPN hizmeti yıllık {tutar()} — anonim kalın, sansürü aşın. 30 gün iade garantisi: {link()}",
        f"Hackleme araçları paketi: Etik hacking öğrenmek isteyenler için {tutar()} değerinde yazılım seti: {link()}",
        f"Ofis yazılımı paketi {tutar()}: Word, Excel, PowerPoint orijinal lisans, ömür boyu geçerli: {link()}",
        f"Sistem hızlandırma yazılımı: Bilgisayarınızı {random.randint(2,5)}x hızlandırın. Ücretsiz deneme süresi dolmak üzere: {link()}",
    ]
    return r(templates)


def _phishing_kisa_sms():
    """Kısa, SMS tarzı phishing mesajları."""
    templates = [
        f"Hesabınız askıya alındı. Doğrulayın: {link()}",
        f"Kargonuz bekliyor. Adres güncelleyin: {link()}",
        f"{tutar()} ödülünüz var. Talep edin: {link()}",
        f"Şifreniz değiştirildi. Siz değilseniz: {link()}",
        f"Faturanız ödenmedi. Son gün bugün: {link()}",
        f"Hesabınıza giriş yapıldı. Engelleyin: {link()}",
        f"Vergi iadeniz hazır. Başvurun: {link()}",
        f"Krediniz onaylandı. Aktifleştirin: {link()}",
        f"Paketiniz gümrükte. {tutar()} ödeyin: {link()}",
        f"Kazandınız! {tutar()} hediye. Alın: {link()}",
        f"Hesabınız silinecek. Önleyin: {link()}",
        f"Şüpheli işlem! Onaylayın: {link()}",
        f"Üyeliğiniz sona eriyor. Yenileyin: {link()}",
        f"Kimliğiniz doğrulanmadı. Tamamlayın: {link()}",
        f"Banka kartınız bloke edildi. Açın: {link()}",
    ]
    return r(templates)


# ── YENİ NORMAL KATEGORİLERİ (4. TUR) ────────────────────────────────────────

def _normal_kisa_sms():
    """Kısa, SMS/WhatsApp tarzı normal mesajlar."""
    templates = [
        f"Tamam, {saat()}'de oradayım.",
        f"Bugün gelemiyorum, yarın görüşelim mi?",
        f"Aldım, teşekkürler!",
        f"Yolda, {random.randint(5,20)} dakika sonra geliyorum.",
        f"Aradın mı? Ben de aramak istiyordum.",
        f"Harika! Yarın devam edelim.",
        f"Tamam anlaştık, {tarih()} günü.",
        f"Bitti mi? Geliyorum o zaman.",
        f"Evet, o saatte müsaitim.",
        f"Görüştük, iyi çalışmalar.",
        f"Özür dilerim, geç kaldım.",
        f"Fotoğrafı gördüm, çok güzel olmuş!",
        f"Sağ ol, bilmiyordum.",
        f"Tamam, hallettim.",
        f"Ne zaman uygun olursun?",
        f"Kolay gelsin, başarılar!",
        f"Aldım mesajı, birazdan yazarım.",
        f"İyi akşamlar, yarın konuşalım.",
    ]
    return r(templates)


def _normal_veli():
    templates = [
        f"Sayın velimiz, {isim()} bu hafta devamsızlık yaptı. Mazeret belgesi için okul idaresiyle görüşmenizi rica ederiz.",
        f"Veli toplantısı: {tarih()} saat {saat()}'de sınıf öğretmeniyle görüşme günü. Lütfen çocuğunuzun karnesi hakkında bilgi almaya gelin.",
        f"Okul gezisi izin formu gönderildi. {tarih()} tarihli {r(['müze', 'fabrika', 'hayvanat bahçesi', 'bilim merkezi'])} gezisi için imzalı formu {tarih()} tarihine kadar teslim edin.",
        f"Öğrenciniz bu dönem başarılı bir ilerleme kaydetti. Ayrıntılı görüşme için {tarih()} tarihli veli toplantısına bekliyoruz.",
        f"Okul servis güzergahı {tarih()} tarihinden itibaren değişiyor. Yeni güzergah bilgisi ektedir.",
        f"Kırtasiye listesi güncellendi. {tarih()} itibarıyla gerekli malzemelerin temin edilmesi beklenmektedir.",
        f"Ödev bildirimi: {isim()} bu hafta matematik ödevini teslim etmedi. Lütfen konuyu öğrencinizle görüşün.",
        f"Yüzme dersleri {tarih()} tarihinde başlıyor. Katılım için {tarih()} tarihine kadar kayıt yaptırılması gerekmektedir.",
        f"Okul kantininde nakit dışında QR ödeme sistemi başlatıldı. Kart veya uygulama ile ödeme yapılabilir.",
        f"Sağlık taraması: {tarih()} tarihinde okul hekimi, diş ve göz taraması yapacak. Çocuğunuzun o gün okulda olmasını sağlayın.",
    ]
    return r(templates)


def _normal_komsu():
    templates = [
        f"Merhaba komşu, bu akşam üst kattan gürültü geliyor. Rica etsek biraz kısar mısınız?",
        f"Selam, kapı önüne aldığım kargo kutularını taşırken yardım eder misiniz? Tek başıma zor olacak.",
        f"Komşu, su kesintisi var mıydı bugün? Bizde de mi? Yoksa sadece bizim daire mi?",
        f"Merhaba, balkona çıkan kedi sizin mi? Çok şirin ama komşu şikâyet edebilir, bilginiz olsun.",
        f"Hafta sonu apartman temizliği var. Herkes kendi katını süpürüyor, bilginiz olsun.",
        f"Komşu, elinizde fazladan tuz var mı? Markete gidemiyorum şu an.",
        f"Paketiniz geldi, kapıcıda bıraktım. Akşam alabilirsiniz.",
        f"Merhaba, binanın girişindeki lamba yandı. Yöneticiye bildirmek lazım, siz bildirebilir misiniz?",
        f"Çocuklar bahçede oynarken topu balkona attı, üzgünüz. Topu aşağıya atabilir misiniz?",
        f"Komşu, {tarih()} günü elektrikçi geliyor. Evinizde olmanız gerekmiyor ama gürültü olabilir.",
        f"Selam, aylık aidatı ödemeyi unuttunuz galiba. Yöneticiden mesaj geldi.",
        f"Merhaba, bu gece oruç açma yemeği yapıyoruz, sizi de bekleriz.",
    ]
    return r(templates)


def _normal_bayram_dini():
    templates = [
        f"Ramazan Bayramınız mübarek olsun! Sağlık, huzur ve mutluluk dolu bir bayram geçirmenizi dilerim.",
        f"Kurban Bayramınız hayırlı olsun! Bu güzel günde sevdiklerinizle bir arada olmanız dileğiyle.",
        f"İyi bayramlar! Uzakta olsak da kalbimiz hep birlikte. Bayramı ailece kutlayın.",
        f"Ramazan ayı bereketli geçsin. İbadetleriniz kabul olsun, dualarınız kabul görsün.",
        f"Kandil mübarek olsun! Bu mübarek gecede dualarınız kabul olsun.",
        f"Cumhuriyet Bayramı kutlu olsun! Atatürk'ü ve tüm şehitlerimizi saygıyla anıyoruz.",
        f"23 Nisan Ulusal Egemenlik ve Çocuk Bayramı kutlu olsun! Çocuklarımızın yüzü daima gülsün.",
        f"19 Mayıs Atatürk'ü Anma, Gençlik ve Spor Bayramı kutlu olsun!",
        f"Yeni yılınız kutlu, sağlık ve mutluluk dolu olsun. Nice yıllara!",
        f"Mevlid Kandili hayırlı olsun. Bu mübarek gecede tüm dilekleriniz kabul olsun.",
        f"Öğretmenler Günü kutlu olsun! Emekleriniz için sonsuz teşekkürler.",
        f"Anneler Günü kutlu olsun! Dünyanın en değerli insanı olduğunuzu unutmayın.",
    ]
    return r(templates)


def _normal_gonullu():
    templates = [
        f"Gönüllü çağrısı: {tarih()} Cumartesi sabahı {r(['Belgrad Ormanı', 'Atatürk Arboretumu', 'sahil'])} temizlik etkinliğimize katılır mısınız?",
        f"Kan bağışı kampanyası: {tarih()} tarihinde kan bağışı etkinliği düzenlenecek. Katkınız hayat kurtarır.",
        f"Gıda bankası: Bu ay {r(['pirinç', 'makarna', 'konserve', 'zeytinyağı'])} bağışı topluyoruz. Katkıda bulunmak için:",
        f"Hayvan barınağı gönüllü: {tarih()} Pazar günü barınakta temizlik ve sosyalleştirme etkinliği var. Gel, sahipsiz dostlarımızla vakit geçir.",
        f"Kitap bağışı: Okumadığınız kitapları çocuklara ulaştırıyoruz. {tarih()} tarihine kadar bırakabilirsiniz.",
        f"Yaşlı ziyareti gönüllüsü arıyoruz: {tarih()} günü huzurevini ziyaret ediyoruz. Katılmak ister misiniz?",
        f"Çevre koruma: Plastik kullanımını azaltma konusunda imza kampanyamıza destek olur musunuz?",
        f"Engelli destek gönüllüsü: {tarih()} günü engelli bireylerle spor etkinliği düzenliyoruz. Gönüllü olmak için yazın.",
        f"Mahalle dayanışması: {tarih()} akşamı mahalle toplantısı var. Bölge sorunlarını konuşacağız.",
    ]
    return r(templates)


def _normal_emekli():
    templates = [
        f"SGK emeklilik bordronuz hazır. {tarih()} tarihinde maaşınız hesabınıza yatacaktır.",
        f"Emekli Sandığı duyurusu: {tarih()} tarihinden itibaren sağlık yardımı kapsamında değişiklik yapılmıştır. Detaylar için şubeye başvurun.",
        f"Merhaba, emekli ikramiyeniz {tarih()} tarihinde hesabınıza aktarılacaktır.",
        f"Emekli kartı yenileme zamanı. Yeni kartınızı almak için nüfus cüzdanınızla en yakın SGK müdürlüğüne başvurun.",
        f"Sağlık Bakanlığı: 65 yaş üstü ücretsiz grip aşısı uygulaması {tarih()} tarihinde başlıyor. Aile hekiminize başvurun.",
        f"Emekli Sandığı sosyal etkinlik: {tarih()} tarihinde {r(['tiyatro', 'müze', 'gezi'])} etkinliği düzenliyoruz. Katılmak için kayıt yaptırın.",
        f"Maaş güncellemesi: Enflasyon farkı {tarih()} tarihli maaşınıza yansıtılmıştır.",
        f"Emekli konut kredisi başvurusu: Düşük faizli emekli konut kredisi kampanyamız {tarih()} tarihine kadar devam ediyor.",
    ]
    return r(templates)


def _normal_diger():
    """Diğer konulardan kısa ve çeşitli normal e-postalar."""
    templates = [
        f"Hava bugün çok güzel, dışarı çıkmak için ideal. Akşam yürüyüşe gidelim mi?",
        f"Enerji faturamı düşürmek için Led ampul taktım. Gerçekten fark yarattı, öneririm.",
        f"Bu ay çok harcama yaptım. Bütçe tutmak bu kadar zor mu olmalı?",
        f"Yeni çıkan diziyi izlemeye başladım, gerçekten çok iyiydi. Sana da öneririm.",
        f"Kahve makinesi bozuldu. Tamirciye gönderdim, bu hafta döner.",
        f"Dün akşam çok iyi bir kitap bitirdim. Hâlâ düşünüyorum, etkileyiciydi.",
        f"Market alışverişi yaptım, çantalar çok ağır. Asansör çalışıyor mu?",
        f"Trafikte çok bekliyorum. {r(['Kadıköy', 'Beşiktaş', 'Şişli', 'Bağcılar'])} tarafında bu saatte hep böyle.",
        f"Güneş çıktı nihayet! Uzun zamandır görmemiştik.",
        f"Bugün çok verimli geçti, harika hissettirdi.",
        f"Hafta sonu ne yapıyorsunuz? Birlikte bir şey planlayalım mı?",
        f"Yeni restoran açılmış köşe başında, denediniz mi? Kokusu çok güzel geliyor.",
        f"Sağlıklı beslenmeye başladım bu ay. Zorlanıyorum ama devam edeceğim.",
        f"Depreme hazırlık çantamı yeniledim. Herkese tavsiye ederim.",
        f"Komşunun kedisi sürekli bize geliyor, sanırım bizi benimsedi.",
    ]
    return r(templates)


PHISHING_GENERATORS = [
    (_phishing_banka,           1500),
    (_phishing_kargo,           1200),
    (_phishing_hesap_guvenligi, 1400),
    (_phishing_odul,            1200),
    (_phishing_fatura,          1200),
    (_phishing_devlet,          1400),
    (_phishing_eticaret,        1200),
    (_phishing_genel,           1000),
    (_phishing_kripto,          1400),
    (_phishing_sahte_is,        1400),
    (_phishing_romantik,         900),
    (_phishing_sigorta,          900),
    (_phishing_sosyal_medya,    1200),
    (_phishing_teknik_destek,   1200),
    (_phishing_yatirim,         1200),
    (_phishing_tatil,            900),
    (_phishing_kiralik,          900),
    (_phishing_kvkk,             900),
    (_phishing_whatsapp,        1200),
    (_phishing_bagis,            900),
    (_phishing_opertor,          900),
    (_phishing_hukuki,           900),
    (_phishing_ceo_fraud,        900),
    (_phishing_sahte_polis,      900),
    (_phishing_sahte_ilac,       900),
    (_phishing_sahte_yazilim,    900),
    (_phishing_kisa_sms,        1500),
]

NORMAL_GENERATORS = [
    (_normal_is_yazismasi,       1800),
    (_normal_alisveris,          1500),
    (_normal_kisisel,            1600),
    (_normal_haber_bulten,       1200),
    (_normal_bilgi_guncelleme,   1000),
    (_normal_saglik,             1500),
    (_normal_okul,               1500),
    (_normal_gercek_fatura,      1200),
    (_normal_sosyal_medya_gercek,1200),
    (_normal_gunluk_yasam,       1400),
    (_normal_seyahat,            1200),
    (_normal_spor,               1200),
    (_normal_apartman,           1000),
    (_normal_evcil_hayvan,        800),
    (_normal_etkinlik,           1000),
    (_normal_musteri_hizmetleri, 1000),
    (_normal_aile,               1400),
    (_normal_hobi,               1200),
    (_normal_online_kurs,        1000),
    (_normal_araba_servis,        800),
    (_normal_yemek,              1200),
    (_normal_is_arkadaslari,     1400),
    (_normal_kutlama,            1000),
    (_normal_kisa_sms,           2000),
    (_normal_veli,               1000),
    (_normal_komsu,              1000),
    (_normal_bayram_dini,        1000),
    (_normal_gonullu,             800),
    (_normal_emekli,              800),
    (_normal_diger,              1600),
]


def generate_rows(generators: list, label: int) -> list[dict]:
    rows = []
    for gen_fn, count in generators:
        for _ in range(count):
            rows.append({"body": gen_fn(), "label": label})
    return rows


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    clean_path   = project_root / "data" / "emails_clean.csv"
    output_path  = project_root / "data" / "emails_clean.csv"

    print("⚙️  Türkçe phishing e-postaları üretiliyor...")
    phishing_rows = generate_rows(PHISHING_GENERATORS, label=1)

    print("⚙️  Türkçe normal e-postalar üretiliyor...")
    normal_rows = generate_rows(NORMAL_GENERATORS, label=0)

    new_df = pd.DataFrame(phishing_rows + normal_rows)
    new_df = new_df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"   Yeni phishing : {len(phishing_rows):,}")
    print(f"   Yeni normal   : {len(normal_rows):,}")
    print(f"   Toplam yeni   : {len(new_df):,}")

    if clean_path.exists():
        existing_df = pd.read_csv(clean_path)
        print(f"\n📦 Mevcut dataset : {len(existing_df):,} satır")
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        print("\n⚠️  emails_clean.csv bulunamadı, yeni dosya oluşturuluyor.")
        combined_df = new_df

    combined_df = combined_df.drop_duplicates(subset=["body"]).reset_index(drop=True)
    combined_df.to_csv(output_path, index=False)

    print(f"✅ Birleştirilmiş dataset : {len(combined_df):,} satır")
    print(f"   Label 0 (normal)  : {(combined_df['label'] == 0).sum():,}")
    print(f"   Label 1 (phishing): {(combined_df['label'] == 1).sum():,}")
    print(f"   Kaydedildi        : {output_path}")


if __name__ == "__main__":
    main()
