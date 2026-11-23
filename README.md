# AltınPano — otomatik altın / gümüş / döviz fiyat sitesi

Kurulumdan sonra **hiçbir şeye dokunmazsın**. GitHub Actions her saat başı fiyatları çeker, 19 sayfalık statik siteyi üretir ve GitHub Pages'e yayınlar. Sunucu yok, aylık ücret yok (tek maliyet alan adı, isteğe bağlı).

Sayfalar: ana pano, 12 ürün sayfası (gram/çeyrek/yarım/tam/14-18-22 ayar altın, ons, gümüş, dolar, euro, sterlin) her biri için grafik, otomatik yorum, geçmiş tablo, SSS ve hızlı hesaplama; 3 hesaplama aracı; hakkında / gizlilik / iletişim; sitemap.xml, robots.txt, ads.txt, schema.org işaretlemesi.

## Kurulum (yaklaşık 10 dakika)

1. GitHub'da **herkese açık (public)** yeni bir repo aç (ücretsiz Pages için public gerekir). Bu klasörün içindekileri repoya yükle (`.github` klasörü dahil).
2. `config.json` içinde şunları düzenle:
   - `site_name`: sitenin adı
   - `site_url`: `https://KULLANICI_ADI.github.io/REPO_ADI` (kendi alan adını bağlayacaksan `https://alanadin.com`)
   - `contact_email`: gerçek e-posta adresin (gizlilik ve iletişim sayfalarında görünür)
3. Repo → **Settings → Pages → Build and deployment → Source: GitHub Actions** seç.
4. Repo → **Actions** sekmesi → "Fiyatları güncelle ve yayınla" → **Run workflow**. 1-2 dakika sonra site yayında. Bundan sonra her saat kendi kendine güncellenir.

## Kendi alan adını bağlamak (önerilir)

1. `config.json`: `"domain": "alanadin.com"` ve `"site_url": "https://alanadin.com"`.
2. Alan adı DNS'inde GitHub Pages kayıtlarını ekle (A kayıtları: 185.199.108.153, .109.153, .110.153, .111.153 ve `www` için CNAME → `KULLANICI_ADI.github.io`).
3. Settings → Pages → **Enforce HTTPS** kutusunu işaretle.

## Gelir (sırayla)

1. **Google Search Console**'a siteyi ekle, `sitemap.xml` gönder (indekslenme için şart).
2. Birkaç hafta sonra **AdSense**'e başvur. Onaylanınca `config.json`'a `adsense_client` (`ca-pub-XXXXXXXX`) ve `ad_slots` (top / middle / bottom) reklam birimi numaralarını yaz. `ads.txt` otomatik üretilir.
3. `affiliate_links` listesine ortaklık bağlantıları ekleyebilirsin:
   `[{"label": "Örnek Platform", "url": "https://...", "note": "Kısa açıklama"}]`
4. İsteğe bağlı: `ga_measurement_id` ile Google Analytics.

## Nasıl çalışır

- `generator/build.py` fiyatları çeker (TCMB + uluslararası altın/gümüş API'leri, biri düşerse yedeğe geçer), `data/history.json` dosyasına günlük kapanış değerini yazar ve `dist/` klasörünü üretir.
- Veri kaynağı bozuk/mantıksız değer dönerse (son kayda göre %25'ten büyük sıçrama) yayın durur, site eski hâliyle kalır.
- Geçmiş grafikler siteyi kurduğun günden itibaren birikir; ilk gün grafik yoktur, 2. günden itibaren görünür.

## Yerel deneme

```bash
pip install -r requirements.txt
python generator/build.py --demo --site-url http://localhost:8000   # sahte veriyle önizleme, dist/ içine
python -m http.server -d dist 8000
```
(`--demo` gerçek geçmişi etkilemez. `--site-url` sadece bu çalıştırma için `config.json`'daki `site_url`'yi ezer; dosyaya dokunmaz, yerel önizlemede linklerin ve canonical adreslerin `http://localhost:8000`'i göstermesini sağlar.)

## Tasarım sistemi ve marka

Renk, tipografi, grid ve bileşen kararları `DESIGN.md` içinde. Ortak stiller `static/base.css` (tokenlar, header, footer), `components.css` (bileşenler), `motion.css` (hareket), sayfaya özel stiller `static/style.css`; yayında ilk üçü `core.css` olarak birleştirilir. Bileşen kitaplığı: `python generator/build.py --demo --styleguide` → `/bilesenler/`. Logo ve ikonlar `static/brand/`, yazı tipi (Literata, SIL OFL) `static/fonts/` altındadır ve kendi sunucumuzdan yüklenir. Bunları yeniden üretmek için `generator/brand_assets.py` (Literata TTF gerekir) (isteğe bağlı geliştirici aracı, `pip install fonttools brotli` gerekir).

## Bakım

Neredeyse sıfır. Actions sekmesinde kırmızı hata görürsen genelde geçici bir API kesintisidir, sonraki saat kendine gelir. Çok uzun süre (60 gün+) hiç commit olmazsa GitHub zamanlanmış çalıştırmayı durdurabilir; bu proje geçmişi her saat commit ettiği için normalde bu olmaz, olursa Actions'tan tek tıkla yeniden başlat.

## Notlar

- Gösterilen fiyatlar uluslararası ons fiyatından hesaplanan göstergedir, kuyumcu/banka fiyatı değildir (sitede yasal uyarı var).
- Yeni ürün eklemek: `generator/build.py` içindeki `ASSETS` listesine bir satır eklemek yeterli (altın türleri için `grams` ve `fine` değerleri).
- Kıdem tazminatı, net-brüt maaş gibi ek araçlar için `templates/tool_*.html` dosyalarını kopyalayıp `build.py` içindeki `tools` listesine ekle.


## Para Rehberi ve aylık rakam kontrolü

`/para-rehberi/` sayfası kaynaklı, elle doğrulanan bir içerik sayfasıdır. Sayfadaki tüm rakamlar tek dosyadan gelir: **`data/facts.json`**. Rakamı değiştirip `checked` tarihini bugüne çekmen yeter; site otomatik yeniden yayınlanır.

Ne zaman neyi kontrol et:
- Her ayın 1'i: TCMB kredi kartı azami faiz tablosu (`credit_card`)
- Her ayın 3'ü civarı: TÜİK yıllık enflasyon (`inflation`)
- Her PPK toplantısından sonra: politika faizi (`policy`)
- Ocak: TMSF mevduat sigortası limiti (`tmsf_limit`) ve mevduat stopajı (`stopaj`, `stopaj_valid_until`; 2026 için geçerlilik 31.12.2026'da bitiyor)

`checked` tarihi 45 günden eskiyse sayfa ziyaretçiye "güncel olmayabilir" uyarısı gösterir ve Actions loguna uyarı düşer.
