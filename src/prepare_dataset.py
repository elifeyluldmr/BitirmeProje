"""
Dataset Temizleme + Türkçe Veri Ekleme Scripti
Çalıştır: python src/prepare_dataset.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

DATA_PATH   = Path(__file__).resolve().parents[1] / "data" / "emails.csv"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "emails_clean.csv"

TURKISH_PHISHING = [
    # ── Banka & Kredi Kartı ──────────────────────────────────────────────────
    ("Hesabınız askıya alındı", "Hesabınız güvenlik ihlali nedeniyle askıya alınmıştır. Doğrulamak için hemen tıklayın.", 1),
    ("Acil: Şifrenizi güncelleyin", "Şifrenizin süresi doldu. Hesabınıza erişmek için hemen güncelleyin.", 1),
    ("Banka hesabınızda şüpheli işlem", "Hesabınızda yetkisiz giriş tespit edildi. Güvenliğiniz için bilgilerinizi doğrulayın.", 1),
    ("Kredi kartınız bloke edildi", "Kredi kartınız güvenlik amacıyla bloke edilmiştir. Açmak için bilgilerinizi güncelleyin.", 1),
    ("Hesabınızdan para çekildi", "Hesabınızdan yetkisiz para transferi yapıldı. Durdurmak için hemen tıklayın.", 1),
    ("Kredi kartı doğrulama gerekli", "Kredi kartınızın güvenliği için doğrulama gerekiyor. Kart bilgilerinizi girin.", 1),
    ("Banka hesabınız donduruldu", "Şüpheli işlem nedeniyle hesabınız donduruldu. Çözmek için tıklayın.", 1),
    ("Transfer onayı gerekiyor", "Hesabınızdan yapılan 3500 TL transferi onaylamak için tıklayın.", 1),
    ("Ödeme bilgilerinizi güncelleyin", "Ödeme bilgileriniz güncel değil. Hesabınızın açık kalması için güncelleyin.", 1),
    ("Banka güvenlik protokolü", "Bankanız yeni güvenlik protokolü uyguluyor. Hesabınızı doğrulamak için tıklayın.", 1),
    ("Hesap limitiniz aşıldı", "Günlük işlem limitiniz aşıldı. Limiti artırmak için bilgilerinizi doğrulayın.", 1),
    ("İnternet bankacılığı güncelleme", "İnternet bankacılığı sistemimiz güncellendi. Yeniden giriş yapmanız gerekmektedir.", 1),
    ("Kart bilgilerinizi doğrulayın", "Kart bilgilerinizde tutarsızlık tespit edildi. Hemen doğrulayın.", 1),
    ("Hesabınız kapatılacak", "Doğrulama yapılmadığı için hesabınız 24 saat içinde kapatılacak.", 1),
    ("Şüpheli para transferi", "Hesabınızdan yurt dışına para transferi yapıldı. Onaylamıyor musunuz tıklayın.", 1),
    ("Banka kimlik doğrulama", "Kimliğinizi doğrulamazsanız hesabınıza erişim engellenecektir.", 1),
    ("ATM kartınız iptal edilecek", "ATM kartınız güvenlik nedeniyle iptal edilecek. Önlemek için bilgilerinizi girin.", 1),
    ("Hesap güvenlik uyarısı", "Hesabınıza 5 başarısız giriş denemesi yapıldı. Güvenliğiniz için şifrenizi değiştirin.", 1),
    ("Online bankacılık kısıtlandı", "Online bankacılık işlemleriniz kısıtlandı. Kısıtlamayı kaldırmak için doğrulayın.", 1),
    ("Kredi başvurusu onaylandı", "Kredi başvurunuz onaylandı. Parayı almak için banka bilgilerinizi girin.", 1),

    # ── Ödül & Çekiliş ──────────────────────────────────────────────────────
    ("Ödülünüzü talep edin", "Tebrikler! 10.000 TL kazandınız. Ödülünüzü almak için bağlantıya tıklayın.", 1),
    ("Hediye çeki kazandınız", "Anketimizi doldurduğunuz için 500 TL hediye çeki kazandınız. 24 saat içinde talep edin.", 1),
    ("Ücretsiz iPhone kazandınız", "Çekilişimizin kazananısınız! iPhone 15 Pro'nuzu talep etmek için bilgilerinizi girin.", 1),
    ("Siz seçildiniz", "Özel müşterilerimizden biri olarak 1000 TL değerinde ödül kazandınız. Hemen talep edin.", 1),
    ("Çekiliş sonucu açıklandı", "Katıldığınız çekilişte büyük ikramiyeyi kazandınız. Ödülünüzü almak için tıklayın.", 1),
    ("Para ödülü kazandınız", "50.000 TL nakit ödül kazandınız. Hesabınıza aktarmak için bilgilerinizi girin.", 1),
    ("Piyango kazandınız", "Milli piyango çekilişinde 500.000 TL kazandınız. Almak için tıklayın.", 1),
    ("Şanslı müşteri seçildiniz", "Bu ayın şanslı müşterisi seçildiniz. Hediyenizi almak için formu doldurun.", 1),
    ("Bedava tatil kazandınız", "Antalya'da 7 gece tatil kazandınız. Rezervasyonunuzu yapmak için tıklayın.", 1),
    ("VIP üyelik hediyesi", "Size özel VIP üyelik hediye edildi. Aktivasyon için hemen tıklayın.", 1),
    ("Anket ödülü kazandınız", "Anketimizi doldurduğunuz için 750 TL kazandınız. Almak için tıklayın.", 1),
    ("Çekilişi kazandınız", "Yıllık büyük çekilişimizde adınız çıktı. Ödülünüzü talep etmek için tıklayın.", 1),
    ("Özel teklif size özel", "Sadece size özel yüzde 90 indirim kazandınız. 1 saat içinde kullanın.", 1),
    ("Samsung telefon kazandınız", "Samsung Galaxy S24 kazandınız. Telefonunuzu teslim almak için adresinizi girin.", 1),
    ("Süpriz ödül", "Hesabınıza özel sürpriz ödül yüklendi. Görüntülemek için tıklayın.", 1),
    ("Altın çekiliş kazananı", "Altın çekilişimizin kazananı sizsiniz. 50 gram altını almak için başvurun.", 1),
    ("Tatil paketi hediye", "Size özel tatil paketi hediye edildi. Uçak bileti ve otel dahil. Hemen talep edin.", 1),
    ("Nakit para ödülü", "Hesabınıza 2500 TL nakit ödül tanımlandı. Çekmek için bilgilerinizi doğrulayın.", 1),
    ("Yıllık müşteri ödülü", "Yıllık en sadık müşterimiz seçildiniz. Ödülünüzü almak için formu doldurun.", 1),
    ("Büyük ikramiye", "Bu haftanın büyük ikramiyesini kazandınız. Detaylar için hemen tıklayın.", 1),

    # ── Fatura & Ödeme ──────────────────────────────────────────────────────
    ("Faturanız ödenmedi", "Son ödeme tarihiniz geçti. Hesabınızın kapatılmaması için hemen ödeme yapın.", 1),
    ("Üyeliğiniz sona eriyor", "Premium üyeliğiniz 24 saat içinde sona erecek. Devam etmek için ödeme bilgilerinizi girin.", 1),
    ("Gecikmiş ödeme uyarısı", "Faturanız 30 gündür ödenmedi. Hizmetinizin kesilmemesi için hemen ödeme yapın.", 1),
    ("Son ödeme uyarısı", "Borcunuzun son ödeme tarihi bugün. Geç ödeme cezası uygulanmadan önce ödeyin.", 1),
    ("Aboneliğiniz iptal edilecek", "Ödeme alınamadığı için aboneliğiniz yarın iptal edilecek. Güncelleyin.", 1),
    ("Elektrik kesinti bildirimi", "Faturanız ödenmediği için yarın elektriğiniz kesilecek. Hemen ödeme yapın.", 1),
    ("Vergi borcu bildirimi", "Vergi borcunuz bulunmaktadır. Ceza uygulanmadan önce ödeme yapın.", 1),
    ("Otomatik ödeme başarısız", "Otomatik ödemeniz başarısız oldu. Bilgilerinizi güncellemek için tıklayın.", 1),
    ("Su faturası ödenmedi", "Su faturanız ödenmedi. Hizmet kesintisini önlemek için hemen ödeme yapın.", 1),
    ("Doğalgaz kesileceK", "Doğalgaz faturanız gecikti. Yarın kesilmemesi için hemen ödeme yapın.", 1),
    ("İnternet faturası", "İnternet faturanız ödenmedi. Bağlantınızın kesilmemesi için ödeme yapın.", 1),
    ("Telefon faturası uyarısı", "Telefon faturanız gecikti. Hattınızın kapatılmaması için hemen ödeyin.", 1),
    ("Kredi taksiti gecikti", "Kredi taksitiniz gecikti. Ek faiz uygulanmadan önce ödeme yapın.", 1),
    ("Kira ödemesi gecikti", "Kira ödemeniz gecikti. Yasal işlem başlatılmadan önce ödeyin.", 1),
    ("Sigorta poliçesi", "Sigorta poliçenizin ödemesi gecikti. İptal olmadan önce ödeme yapın.", 1),

    # ── Kargo & Teslimat ────────────────────────────────────────────────────
    ("Kargo bilgilendirme", "Paketiniz teslim edilemedi. Adresinizi güncellemek için aşağıdaki bağlantıya tıklayın.", 1),
    ("Paketiniz gümrükte bekliyor", "Paketiniz gümrükte bekliyor. Serbest bırakmak için ücret ödeyin.", 1),
    ("Teslimat adresi hatası", "Adresinizde hata tespit edildi. Paketinizin teslimi için adresinizi güncelleyin.", 1),
    ("Gümrük vergisi gerekli", "Paketiniz için 45 TL gümrük vergisi gerekiyor. Ödeme yapmak için tıklayın.", 1),
    ("Kargo ücreti gerekiyor", "Paketiniz için küçük bir kargo ücreti gerekiyor. Ödeme yapmak için tıklayın.", 1),
    ("Teslimat yeniden planlandı", "Paketinizin teslimatı yeniden planlandı. Onaylamak için tıklayın.", 1),
    ("Paketiniz iade edilecek", "Adres bulunamadı. Paketiniz iade edilmeden önce adresinizi güncelleyin.", 1),
    ("Kargo takip sorunu", "Paketinizde sorun var. Çözmek için kargo firmasının sitesine giriş yapın.", 1),
    ("Paket teslim edilemedi", "Evde bulunmadığınız için paketiniz teslim edilemedi. Yeni randevu için tıklayın.", 1),
    ("Gümrük bildirimi acil", "Paketiniz gümrükte 3 gündür bekliyor. Bugün işlem yapmazsanız iade edilecek.", 1),

    # ── Devlet & Resmi Kurum ────────────────────────────────────────────────
    ("Vergi iadesi bildirimi", "Vergi iadeniz onaylandı. Tutarı almak için banka bilgilerinizi girin.", 1),
    ("E-devlet bildirimi", "E-devlet sisteminizde bekleyen işlemleriniz var. Tıklayarak görüntüleyin.", 1),
    ("SGK bildirimi", "SGK kaydınızda eksik bilgi tespit edildi. Güncelleme için tıklayın.", 1),
    ("Vergi dairesi uyarısı", "Vergi borcunuz nedeniyle yasal işlem başlatılacak. Ödeme için tıklayın.", 1),
    ("Mahkeme celbi bildirimi", "Adınıza açılmış dava bulunmaktadır. Detaylar için hemen tıklayın.", 1),
    ("Emeklilik başvurusu onaylandı", "Emeklilik başvurunuz onaylandı. Maaşınızı almak için bilgilerinizi girin.", 1),
    ("Nüfus müdürlüğü", "Kimlik bilgilerinizde tutarsızlık tespit edildi. Düzeltmek için başvurun.", 1),
    ("Trafik cezası bildirimi", "Adınıza trafik cezası kesildi. Ödeme yapmazsanız haciz uygulanacak.", 1),
    ("Pasaport uyarısı", "Pasaportunuzun süresi dolmak üzere. Online yenilemek için tıklayın.", 1),
    ("Ehliyet yenileme", "Ehliyetinizin süresi doldu. Online yenilemek için bilgilerinizi girin.", 1),
    ("Sosyal yardım bildirimi", "Adınıza sosyal yardım ödemesi onaylandı. Almak için bilgilerinizi doğrulayın.", 1),
    ("Belediye uyarısı", "Belediye borcunuz bulunmaktadır. Haciz uygulanmadan önce ödeme yapın.", 1),

    # ── Sosyal Medya ────────────────────────────────────────────────────────
    ("Instagram hesabınız askıya alındı", "Hesabınız kural ihlali nedeniyle askıya alındı. İtiraz etmek için tıklayın.", 1),
    ("Facebook güvenlik uyarısı", "Facebook hesabınıza şüpheli giriş tespit edildi. Hemen doğrulayın.", 1),
    ("WhatsApp hesabınız kısıtlandı", "WhatsApp hesabınız geçici olarak kısıtlandı. Açmak için doğrulayın.", 1),
    ("Twitter hesabınız askıda", "Hesabınız ihlal nedeniyle askıya alındı. Geri almak için başvurun.", 1),
    ("TikTok hesabı uyarısı", "TikTok hesabınız kısıtlanmak üzere. Önlemek için kimliğinizi doğrulayın.", 1),
    ("YouTube kanalınız kaldırılacak", "Kanalınız telif ihlali nedeniyle kaldırılacak. İtiraz için tıklayın.", 1),
    ("LinkedIn hesap güvenliği", "LinkedIn hesabınıza farklı ülkeden giriş yapıldı. Onaylamıyor musunuz?", 1),
    ("Sosyal medya şifre sıfırlama", "Şifreniz sıfırlandı. Siz yapmadıysanız hesabınızı hemen koruyun.", 1),

    # ── Teknoloji & Güvenlik ────────────────────────────────────────────────
    ("E-posta depolama alanınız doldu", "E-posta hesabınız dolmak üzere. Hesabınızı kaybetmemek için hemen doğrulayın.", 1),
    ("Acil güncelleme gerekiyor", "Sisteminizde kritik güvenlik açığı tespit edildi. Koruma için hemen tıklayın.", 1),
    ("Virüs tespit edildi", "Cihazınızda virüs tespit edildi. Temizlemek için hemen tıklayın.", 1),
    ("Hesabınız hacklendi", "Hesabınıza yetkisiz erişim tespit edildi. Hemen şifrenizi değiştirin.", 1),
    ("Yazılım lisansı sona erdi", "Lisansınız sona erdi. Bilgisayarınızı korumak için yenileyin.", 1),
    ("Bulut depolama uyarısı", "Bulut depolama alanınız doldu. Dosyalarınızı kaybetmemek için planınızı yükseltin.", 1),
    ("İnternet servisiniz kesilecek", "Ödeme yapılmadığı için internetiniz yarın kesilecek. Hemen ödeme yapın.", 1),
    ("Cihazınız tehlikede", "Cihazınız zararlı yazılım içeriyor. Hemen tarama yapın.", 1),
    ("Apple kimlik doğrulama", "Apple ID'niz başka bir cihazdan kullanıldı. Siz değilseniz doğrulayın.", 1),
    ("Google hesap güvenliği", "Google hesabınıza şüpheli giriş yapıldı. Hemen güvenliğinizi kontrol edin.", 1),
    ("Microsoft güvenlik uyarısı", "Microsoft hesabınız tehlikede. Korumak için hemen giriş yapın.", 1),
    ("Netflix şifre değişti", "Netflix şifreniz değiştirildi. Siz yapmadıysanız hesabınızı kurtarın.", 1),

    # ── Yatırım & Dolandırıcılık ────────────────────────────────────────────
    ("Yatırımınızı katlayın", "Güvenli yatırım fırsatı! 1000 TL yatırın, 30 günde 3000 TL kazanın.", 1),
    ("Kripto para fırsatı", "Bitcoin'de büyük fırsat! Şimdi yatırım yapın, yüzde 500 getiri garantili.", 1),
    ("Özel yatırım teklifi", "Seçkin yatırımcılara özel fırsat. Minimum 500 TL ile başlayın.", 1),
    ("Borsa içeriden bilgi", "İçeriden bilgi: Bu hisse yarın yüzde 200 yükselecek. Hemen alın.", 1),
    ("Forex yatırım fırsatı", "Forex'te günlük yüzde 10 kazanç garantili. Hemen hesap açın.", 1),
    ("Kripto madencilik", "Evden kripto madenciliği yapın. Aylık 5000 TL garantili kazanç.", 1),
    ("Hisse senedi tüyo", "Bu hisse senedini alın, yarın iki katına çıkacak. Sınırlı süre.", 1),
    ("Emeklilik fonu fırsatı", "Emeklilik fonunuzu katlayın. Güvenli ve garantili yatırım.", 1),

    # ── İş Teklifi Dolandırıcılığı ──────────────────────────────────────────
    ("İş teklifi evden çalış", "Evden çalışarak ayda 20.000 TL kazanın. Başlamak için hemen başvurun.", 1),
    ("Part time iş fırsatı", "Günde 2 saat çalışarak 5000 TL kazanın. Hemen başvurun.", 1),
    ("Online iş teklifi", "İnternetten para kazanmak ister misiniz? Günlük 500 TL garantili.", 1),
    ("Acele iş başvurusu", "Şirketimiz acil eleman arıyor. Maaş 15.000 TL. Hemen başvurun.", 1),
    ("Kolay para kazanma", "Sosyal medyada paylaşım yaparak ayda 8000 TL kazanın.", 1),

    # ── Sağlık & Sigorta ────────────────────────────────────────────────────
    ("Sağlık sigortanız sona eriyor", "Sağlık sigortanız 48 saat içinde sona erecek. Yenilemek için tıklayın.", 1),
    ("Ücretsiz sağlık kontrolü", "Size özel ücretsiz sağlık kontrolü kazandınız. Randevu almak için tıklayın.", 1),
    ("Sigorta iadesi", "Sigorta poliçenizden iade hakkınız doğdu. Almak için bilgilerinizi girin.", 1),
    ("Covid test sonucu", "Covid test sonucunuz pozitif. Detaylar için bilgilerinizi doğrulayın.", 1),

    # ── Alışveriş ───────────────────────────────────────────────────────────
    ("Siparişiniz iptal edilecek", "Ödeme alınamadı. Siparişinizin iptal olmaması için bilgilerinizi güncelleyin.", 1),
    ("Flash indirim fırsatı", "Sadece 1 saat geçerli! Yüzde 95 indirim. Hemen satın almak için tıklayın.", 1),
    ("Sipariş doğrulama gerekli", "Siparişinizi doğrulamak için kart bilgilerinizi yeniden girin.", 1),
    ("İade için bilgi gerekli", "İade talebiniz için banka bilgilerinizi girin.", 1),
    ("Hediye paketi teslimi", "Adınıza hediye paketi var. Teslim almak için adres bilgilerinizi girin.", 1),
    ("Özel indirim kuponu", "Size özel yüzde 80 indirim kuponu kazandınız. Hemen kullanın.", 1),

    # ── Diğer ───────────────────────────────────────────────────────────────
    ("Avukat bildirimi", "Hakkınızda yasal işlem başlatıldı. Durdurmak için hemen bizimle iletişime geçin.", 1),
    ("Miras bildirimi", "Uzak akrabanızdan size miras kaldı. Almak için bilgilerinizi gönderin.", 1),
    ("Burs kazandınız", "Burs başvurunuz onaylandı. Ödemeyi almak için banka bilgilerinizi girin.", 1),
    ("Araç sigortası sona eriyor", "Araç sigortanız sona eriyor. Ceza almamak için hemen yenileyin.", 1),
    ("Okul kaydı ücreti", "Çocuğunuzun okul kaydı için ek ödeme gerekmektedir. Hemen ödeyin.", 1),
    ("Yardım kampanyası", "Depremzedeler için bağış toplanıyor. Yardım etmek için tıklayın.", 1),
    ("Kiracı uyarısı", "Kiracınız şikayette bulundu. Hukuki süreç başlamadan önce iletişime geçin.", 1),
    ("Araç haczi", "Aracınıza haciz kararı verildi. Önlemek için hemen ödeme yapın.", 1),
    ("Borcunuz icra takibine alındı", "Borcunuz icra takibine alındı. Durdurmak için bugün ödeme yapın.", 1),
    ("Hesabınız doğrulanmadı", "Hesabınız henüz doğrulanmadı. 48 saat içinde doğrulamazsanız silinecek.", 1),
    ("Yeni cihaz girişi tespit edildi", "Hesabınıza yeni bir cihazdan giriş yapıldı. Siz değilseniz tıklayın.", 1),
    ("Para transferi yapıldı", "Hesabınızdan 5000 TL transfer yapıldı. Onaylamıyor musunuz tıklayın.", 1),
    ("Ücretsiz abonelik", "3 aylık ücretsiz premium üyelik kazandınız. Aktif etmek için bilgilerinizi girin.", 1),
    ("Kampanya son gün", "Bu kampanya bugün sona eriyor. Kaçırmamak için hemen tıklayın.", 1),
]

TURKISH_LEGITIMATE = [
    # ── İş & Toplantı ────────────────────────────────────────────────────────
    ("Toplantı hatırlatması", "Yarın saat 10:00'da proje toplantımız var. Katılımınızı bekliyoruz.", 0),
    ("Haftalık rapor", "Bu haftaki satış rakamlarını ekte bulabilirsiniz. İyi çalışmalar.", 0),
    ("Proje güncellemesi", "Projede bu hafta şu adımları tamamladık. Detaylar için ekteki dosyaya bakabilirsiniz.", 0),
    ("Bütçe toplantısı", "Q1 bütçe değerlendirme toplantısı 8 Ocak Çarşamba günü yapılacaktır.", 0),
    ("Sunum hazırlığı", "Cuma günkü sunum için slaytları hazırladım. Görüşlerinizi paylaşır mısınız?", 0),
    ("Ekip yemeği", "Bu hafta cuma akşamı ekip yemeği organizasyonu yapıyoruz. Katılabilir misiniz?", 0),
    ("Görev atama", "Yeni projedeki görevinizi ekte bulabilirsiniz. Sorularınız için yazabilirsiniz.", 0),
    ("Performans değerlendirmesi", "Yıllık performans değerlendirmeniz için lütfen formu doldurun.", 0),
    ("Ofis kapalı duyurusu", "Pazartesi günü ofis tadilat nedeniyle kapalı olacaktır.", 0),
    ("İş başvurusu yanıtı", "Başvurunuzu aldık. Değerlendirme süreci tamamlandığında size dönüş yapacağız.", 0),
    ("Maaş bordrosu", "Kasım ayı maaş bordronuz sisteme yüklendi. Hesabınızdan görüntüleyebilirsiniz.", 0),
    ("İzin onayı", "İzin talebiniz onaylanmıştır. 5-10 Ocak tarihleri arasında izinli sayılacaksınız.", 0),
    ("Şirket pikniği", "Yıllık şirket pikniğimiz 15 Temmuz'da Belgrad Ormanı'nda yapılacak.", 0),
    ("Eğitim duyurusu", "Önümüzdeki ay düzenlenecek eğitim programına kayıt yaptırmak ister misiniz?", 0),
    ("Proje teslim tarihi", "Projenin teslim tarihi 20 Ocak olarak belirlendi. Ekibinizi bilgilendiriniz.", 0),
    ("Toplantı notu", "Dünkü toplantı notlarını ekte bulabilirsiniz. İncelemenizi rica ederim.", 0),
    ("Yeni çalışan tanıtımı", "Pazartesi günü yeni ekip arkadaşımız Mehmet işe başlıyor. Hoş geldin diyelim.", 0),
    ("Ofis malzeme siparişi", "Ofis malzemeleri siparişi verildi. Önümüzdeki hafta teslim edilecek.", 0),
    ("Müşteri geri bildirimi", "Son projeyle ilgili müşteriden olumlu geri bildirim aldık. Tebrikler.", 0),
    ("Rapor teslimi", "Aylık faaliyet raporunu bu akşam teslim etmem gerekiyor. Veriler hazır mı?", 0),
    ("Konferans kaydı", "Önümüzdeki ay İstanbul'da düzenlenecek konferansa kayıt yaptırdım.", 0),
    ("Şirket toplantısı", "Tüm çalışanlar için genel kurul toplantısı 15 Ocak Pazartesi saat 09:00.", 0),
    ("Proje onayı", "Sunduğunuz proje teklifi yönetim kurulu tarafından onaylandı. Tebrikler.", 0),
    ("Çalışan anketi", "Çalışan memnuniyeti anketimizi doldurmayı unutmayın. Son gün 31 Ocak.", 0),
    ("Seyahat planı", "İzmir ziyareti için uçak bileti ve otel rezervasyonu yapıldı. Detaylar ekte.", 0),

    # ── Alışveriş & Sipariş ──────────────────────────────────────────────────
    ("Sipariş onayı", "Siparişiniz alınmıştır. Tahmini teslimat süresi 3-5 iş günüdür.", 0),
    ("Kargo teslim edildi", "Siparişiniz bugün teslim edilmiştir. Umarız alışverişinizden memnun kalmışsınızdır.", 0),
    ("Abonelik yenileme", "Netflix aboneliğiniz otomatik olarak yenilenmiştir. Fatura detayları hesabınızda.", 0),
    ("İade onayı", "İade talebiniz onaylandı. Tutar 3-5 iş günü içinde hesabınıza aktarılacak.", 0),
    ("Ürün değerlendirmesi", "Son alışverişinizi değerlendirmek ister misiniz? Görüşleriniz bizim için önemli.", 0),
    ("Kargo takip", "Siparişiniz kargoya verildi. Takip numaranız: TRK123456789", 0),
    ("Sipariş hazırlanıyor", "Siparişiniz hazırlanmaktadır. En kısa sürede kargoya verilecektir.", 0),
    ("Stok bildirimi", "Favorilere eklediğiniz ürün tekrar stokta. Hemen inceleyin.", 0),
    ("Yeni sezon ürünleri", "Yeni sezon ürünlerimiz geldi. Koleksiyonu incelemek için uygulamamızı açın.", 0),
    ("Sipariş teslim edildi", "Kargo firması siparişinizi teslim ettiğini bildirdi. İyi günler dileriz.", 0),
    ("Sipariş iptal onayı", "Talep ettiğiniz sipariş iptali gerçekleştirildi. Ödemeniz iade edilecek.", 0),

    # ── Fatura & Ödeme (meşru) ───────────────────────────────────────────────
    ("Fatura bildirimi", "Kasım ayı faturanız oluşturulmuştur. Ödeme için son tarih 15 Aralık.", 0),
    ("Ödeme onayı", "Ödemeniz başarıyla alındı. Teşekkür ederiz.", 0),
    ("Otomatik ödeme bildirimi", "Aylık abonelik ücretiniz otomatik olarak hesabınızdan alınmıştır.", 0),
    ("Elektrik faturası", "Ekim ayı elektrik faturanız 450 TL olarak kesilmiştir.", 0),
    ("Su faturası", "Bu ayki su faturanız 85 TL'dir. Son ödeme tarihi 20 Aralık.", 0),
    ("İnternet faturası", "Kasım ayı internet faturanız oluştu. Otomatik ödeme ile ödenecektir.", 0),
    ("Kredi kartı ekstresi", "Ekim ayı kredi kartı ekstreniz hazır. Hesabınızdan görüntüleyebilirsiniz.", 0),

    # ── Sağlık & Randevu ─────────────────────────────────────────────────────
    ("Randevu onayı", "Dr. Ayşe Kaya ile 15 Ocak saat 14:30 randevunuz onaylanmıştır.", 0),
    ("Randevu hatırlatması", "Yarın saat 11:00'deki randevunuzu hatırlatmak istedik.", 0),
    ("Tahlil sonuçları", "Tahlil sonuçlarınız hazır. Hastane portalından görüntüleyebilirsiniz.", 0),
    ("Aşı hatırlatması", "Yıllık grip aşısı dönemi geldi. Randevu almak için arayabilirsiniz.", 0),
    ("Reçete yenileme", "Kronik ilaçlarınızın reçetesi sona eriyor. Randevu alarak yenileyebilirsiniz.", 0),
    ("Randevu iptali", "Dr. Yılmaz yarınki randevusunu iptal etti. Yeni randevu için arayabilirsiniz.", 0),
    ("Kontrol randevusu", "Yıllık sağlık kontrolünüz için randevu almanızı hatırlatmak istedik.", 0),
    ("İlaç hatırlatması", "Sabah ilacınızı almayı unutmayın. Düzenli kullanım önemlidir.", 0),

    # ── Eğitim ───────────────────────────────────────────────────────────────
    ("Ders programı değişikliği", "Bu haftaki ders programında değişiklik yapılmıştır. Güncel programı kontrol edin.", 0),
    ("Ödev hatırlatması", "Matematik ödevinizin teslim tarihi yarın. Başarılar.", 0),
    ("Sınav sonuçları", "Dönem sonu sınav sonuçlarınız açıklandı. Öğrenci portalından görüntüleyin.", 0),
    ("Kütüphane hatırlatması", "Ödünç aldığınız kitabın iade tarihi yaklaşıyor. Lütfen zamanında iade edin.", 0),
    ("Mezuniyet töreni", "Mezuniyet törenimiz 20 Haziran'da düzenlenecektir. Ailenizi de davet edebilirsiniz.", 0),
    ("Staj duyurusu", "Yaz stajı başvuruları başladı. Detaylar için kariyer portalını ziyaret edin.", 0),
    ("Veli toplantısı", "Dönem sonu veli toplantısı 25 Ocak Cuma günü saat 18:00'de.", 0),
    ("Ders notu paylaşımı", "Bu haftaki ders notlarını sisteme yükledim. Faydalı olması dileğiyle.", 0),
    ("Burs başvurusu", "Burs başvuru dönemi açıldı. Son başvuru tarihi 31 Ocak.", 0),
    ("Kulüp etkinliği", "Fotoğrafçılık kulübü bu hafta dış çekim yapacak. Katılmak ister misiniz?", 0),
    ("Öğrenci toplantısı", "Sınıf temsilcisi seçimi için yarın öğle arası toplanıyoruz.", 0),
    ("Proje sunumu", "Bitirme projesi sunumları 15 Mayıs'ta başlıyor. Hazırlıklarınızı tamamlayın.", 0),
    ("Dönem başlangıcı", "Yeni dönem 15 Eylül'de başlıyor. Ders kayıtlarınızı tamamlamayı unutmayın.", 0),

    # ── Sosyal & Kişisel ─────────────────────────────────────────────────────
    ("Doğum günü kutlaması", "Doğum günün kutlu olsun! Güzel bir gün geçirmeni diliyoruz.", 0),
    ("Düğün daveti", "Düğün törenimize sizi de bekliyoruz. 15 Haziran saat 18:00 İstanbul.", 0),
    ("Yemek daveti", "Cuma akşamı akşam yemeği için buluşalım mı? Saat 19:00 uygun mu?", 0),
    ("Kahve buluşması", "Bu hafta sonu bir kahve içelim mi? Pazar öğleden sonra müsaitim.", 0),
    ("Tatil planı", "Yaz tatili için Kapadokya'ya gitmeyi düşünüyoruz. Katılmak ister misin?", 0),
    ("Yardım talebi", "Taşınmamda yardımcı olabilir misin? Cumartesi günü planlıyorum.", 0),
    ("Spor daveti", "Bu hafta sonu futbol oynayacağız. Katılmak ister misin?", 0),
    ("Kitap önerisi", "Okuduğum kitabı çok beğendim. Sana da öneririm.", 0),
    ("Film önerisi", "Dün izlediğim filmi çok beğendim, sana da öneririm.", 0),
    ("Sosyal etkinlik", "Cumartesi günü müzeye gidiyoruz. Seninle de paylaşmak istedim.", 0),
    ("Dayanışma mesajı", "Zor bir dönemden geçtiğini biliyorum. Yanındayım, ihtiyacın olursa yaz.", 0),
    ("Tebrik mesajı", "Terfin hayırlı olsun! Yeni pozisyonunda başarılar dilerim.", 0),
    ("Geçmiş olsun", "Hastalığını duydum, geçmiş olsun. İyileşmeni diliyorum.", 0),
    ("Teşekkür mesajı", "Dünkü yardımın için çok teşekkür ederim. Büyük kolaylık sağladı.", 0),
    ("Nişan daveti", "Nişan törenimize katılmanızı rica ederiz. 10 Mart Cumartesi saat 19:00.", 0),
    ("Bebek haberi", "Bebeğimiz dünyaya geldi! Herkesi haberdar etmek istedik.", 0),
    ("Vefat duyurusu", "Annemin vefatını üzüntüyle bildiririm. Cenaze namazı yarın öğle vakti.", 0),
    ("Ev taşıma haberi", "Yeni evimize taşındık. Adresimizi paylaşıyorum, ziyarete bekliyoruz.", 0),

    # ── Haber & Bilgi ────────────────────────────────────────────────────────
    ("Günlük haber özeti", "Bugünkü haber özetiniz hazır. Güncel gelişmeleri okumak için uygulamayı açın.", 0),
    ("Hava durumu bildirimi", "Yarın İstanbul'da yağmur bekleniyor. Şemsiyenizi yanınıza almayı unutmayın.", 0),
    ("Trafik bildirimi", "FSM Köprüsü'nde yoğunluk var. Alternatif güzergah kullanmanızı öneririz.", 0),
    ("Spor sonuçları", "Dün akşamki maç 2-1 bitti. Detaylı analiz için uygulamamızı açın.", 0),
    ("Bülten aboneliği", "Bültenimize abone olduğunuz için teşekkürler. İlk sayımız Pazartesi geliyor.", 0),
    ("Hisse senedi özeti", "Portföyünüzdeki hisselerin bugünkü özeti hazır. Uygulamamızdan görüntüleyin.", 0),

    # ── Teknik Destek (meşru) ────────────────────────────────────────────────
    ("Teknik destek yanıtı", "Talebiniz alınmıştır. Ekibimiz en kısa sürede size geri dönecektir.", 0),
    ("Sistem bakımı bildirimi", "Pazar gecesi 02:00-04:00 arası planlı bakım yapılacaktır.", 0),
    ("Güncelleme tamamlandı", "Uygulama güncellemesi başarıyla tamamlandı. Yeni özellikler aktif.", 0),
    ("Destek talebi kapatıldı", "Destek talebiniz çözüme kavuştu ve kapatıldı.", 0),
    ("Şifre sıfırlama", "Şifre sıfırlama talebiniz alındı. Bağlantı e-postanıza gönderildi.", 0),
    ("Hesap oluşturuldu", "Hesabınız başarıyla oluşturuldu. Hoş geldiniz!", 0),
    ("İki faktörlü doğrulama", "İki faktörlü doğrulama başarıyla aktif edildi. Hesabınız güvende.", 0),

    # ── Diğer Meşru ─────────────────────────────────────────────────────────
    ("Anket daveti", "Hizmet kalitemizi geliştirmek için görüşlerinize ihtiyacımız var.", 0),
    ("Etkinlik hatırlatması", "Yarın saat 15:00'deki webinara katılımınızı hatırlatmak istedik.", 0),
    ("Proje teklifi", "Hazırladığım proje teklifini incelemenizi rica ederim.", 0),
    ("Dosya paylaşımı", "Toplantı notlarını Google Drive'a yükledim. Erişim bağlantısı ektedir.", 0),
    ("Referans talebi", "İş başvurusu için referans olarak sizi gösterebilir miyim?", 0),
    ("Organizasyon daveti", "Yardım kampanyamıza gönüllü olarak katılmak ister misiniz?", 0),
    ("Çalışma daveti", "Kütüphanede birlikte çalışmak ister misin? Öğleden sonra müsaitim.", 0),
    ("Geri bildirim talebi", "Sunumumla ilgili geri bildiriminizi almak isterim.", 0),
    ("Konser daveti", "Cuma akşamı konsere gidiyoruz. Seninle de gelmek ister misin?", 0),
    ("Sergi daveti", "Arkadaşımın fotoğraf sergisi açılıyor. Birlikte gidelim mi?", 0),
    ("Spor maçı daveti", "Pazar günü stadyumda maç var. Bilet aldım, benimle gelir misin?", 0),
    ("Kitap kulübü", "Bu ayki kitap kulübü toplantımız Cumartesi saat 15:00'te.", 0),
    ("Dil kursu", "İngilizce kursuna kayıt oldum. Sen de katılmak ister misin?", 0),
    ("Yemek tarifi", "Dün denediğim tarifi paylaşmak istedim. Harika çıktı.", 0),
    ("Seyahat önerisi", "Geçen hafta gittiğim yer harikaydı. Sana da öneririm.", 0),
    ("Hatırlatma notu", "Yarın sabah 9'daki toplantıyı hatırlatmak istedim. Görüşürüz.", 0),
    ("Bilgi paylaşımı", "Konuyla ilgili ilginç bir makale buldum. Paylaşmak istedim.", 0),
    ("Kütüphane önerisi", "Bu kitabı mutlaka oku. Gerçekten etkileyici bir eser.", 0),
    ("Uygulama önerisi", "Bu uygulamayı yükle, işini kolaylaştırır.", 0),
    ("Podcast önerisi", "Bu podcast'i dinlemeye başladım, çok faydalı. Sana da öneririm.", 0),
]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    print("\n🧹 Temizleme başlıyor...")
    original_len = len(df)

    if "subject" in df.columns:
        if df["subject"].isnull().all():
            df = df.drop(columns=["subject"])
            print("   ✓ Subject kolonu kaldırıldı (tamamı boş)")

    df = df[df["body"].notna()]
    df = df[df["body"].astype(str).str.strip() != ""]
    df = df[df["body"].astype(str).str.strip().str.lower() != "nan"]
    df = df[df["body"].astype(str).str.len() >= 20]
    print("   ✓ Çok kısa body satırları kaldırıldı (< 20 karakter)")
    df = df[df["body"].astype(str).str.len() <= 100_000]
    print("   ✓ Anormal uzun body satırları kaldırıldı (> 100,000 karakter)")

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["body"])
    print(f"   ✓ {before_dedup - len(df):,} tekrar eden satır kaldırıldı")

    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df[df["label"].isin([0, 1])]
    df["label"] = df["label"].astype(int)

    print(f"   ✓ Temizleme tamamlandı: {original_len:,} → {len(df):,} satır")
    return df.reset_index(drop=True)


def add_turkish_data(df: pd.DataFrame) -> pd.DataFrame:
    print("\n🇹🇷 Türkçe veriler ekleniyor...")
    turkish_rows = []
    for subject, body, label in TURKISH_PHISHING:
        turkish_rows.append({"body": f"{subject} {body}", "label": label})
    for subject, body, label in TURKISH_LEGITIMATE:
        turkish_rows.append({"body": f"{subject} {body}", "label": label})
    turkish_df = pd.DataFrame(turkish_rows)
    combined = pd.concat([df, turkish_df], ignore_index=True)
    print(f"   ✓ {len(TURKISH_PHISHING)} Türkçe phishing eklendi")
    print(f"   ✓ {len(TURKISH_LEGITIMATE)} Türkçe normal e-posta eklendi")
    return combined


def print_summary(df: pd.DataFrame) -> None:
    print("\n📊 Temizlenmiş Dataset Özeti:")
    print(f"   Toplam satır : {len(df):,}")
    dist = df["label"].value_counts()
    for label, count in dist.items():
        name = "Phishing" if label == 1 else "Normal"
        pct = count / len(df) * 100
        print(f"   {name} ({label}) : {count:,} (%{pct:.1f})")


def main() -> None:
    print("=" * 55)
    print("  DATASET HAZIRLAMA")
    print("=" * 55)

    df = pd.read_csv(DATA_PATH)
    print(f"📦 Orijinal satır sayısı: {len(df):,}")

    df = clean_dataframe(df)
    df = add_turkish_data(df)
    print_summary(df)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\n✅ Temizlenmiş dataset kaydedildi: {OUTPUT_PATH}")
    print("=" * 55)
    print("Şimdi modeli yeniden eğit:")
    print("   python src/train_model.py")
    print("=" * 55)


if __name__ == "__main__":
    main()