# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Türkiye'de finansal okuryazarlığı düşük yetişkinler. Çoğu siteye telefondan girer. Bir fiyata bakmak, bir hesap yapmak ya da "bu rakam benim için ne demek" sorusuna sade bir cevap bulmak için gelirler. Jargon bilmezler; güven ararlar.

## Product Purpose

ParaOkur, altın, gümüş ve döviz fiyatlarını ve para konularındaki temel rakamları (enflasyon, faiz, kredi kartı borcu, stopaj, hesaplayıcılar) sade Türkçe ile ve ücretsiz sunan statik bir bilgi sitesidir. Fiyatlar her saat otomatik güncellenir. Başarı: kullanıcı rakamı anlar, kendi durumuna uygular ve siteye güvenir; gelir yalnızca bu güvenin yan ürünü olarak reklamdan gelir.

## Positioning

Sade, güvenilir, samimi ve net. Rakamı yalnızca göstermez, anlamlandırır (alım gücü, enflasyona karşı getiri, gerçek borç maliyeti). Her rakamın kaynağı ve kontrol tarihi görünür. Komşu bir fiyat sitesi, agresif "yatırım fırsatı" dilini kullanmadan bu tonu ve kaynak şeffaflığını birlikte taşıyamaz.

## Operating Context

Statik site: Python (`generator/build.py`) ve Jinja şablonlarıyla üretilir, GitHub Actions her saat fiyatları çeker ve GitHub Pages'e yayınlar. Sunucu yok. Fiyat kaynakları: TCMB döviz satış kurları ve uluslararası altın/gümüş veri sağlayıcıları. Kaynak bozuk değer dönerse (son kayda göre %25'ten büyük sıçrama) yayın durur, site eski hâliyle kalır. Kullanım ağırlıkla mobilde, kısa ziyaretlerdir.

## Capabilities and Constraints

- Ürün sayfaları: gram, çeyrek, yarım, tam, 14/18/22 ayar altın, ons, gümüş, dolar, euro, sterlin. Her birinde grafik, otomatik yorum, geçmiş tablo, SSS ve hızlı hesaplama.
- Araçlar: altın hesaplama, altın getiri hesaplama, döviz çevirici. Ayrıca Para Rehberi (enflasyon, faiz, borç) sayfası.
- Kurumsal sayfalar: hakkında ve yasal uyarı, gizlilik, iletişim.
- **Hiçbir finansal rakam uydurulmaz.** Rakamlar yalnızca `data/facts.json` dosyasından gelir; kaynak ve kontrol tarihi gösterilir.
- **Yatırım tavsiyesi verilmez.** Yorum yapılır, "al/sat" denmez. Fiyatlar hesaplanmış göstergedir; kuyumcu ve banka fiyatı değildir, yasal uyarı sitede yer alır.
- `data/history.json` bot tarafından her saat yazılır; elle değiştirilmez.
- Gelir modeli: AdSense. Reklam yalnızca içerik akışında ve "Reklam" etiketiyle yer alır. Ortaklık bağlantısı şimdilik yok. Reklam, alan adı ve iletişim e-postası henüz `config.json` içinde boştur (açık karar).

## Brand Commitments

- Ad: ParaOkur. Logo: sikke içinde açılan kitap ve yükselen üç çubuk (`static/brand/`).
- Ses: sade Türkçe, jargon yok, sakin. Korku, kazanç vaadi ya da "yatırım fırsatı" agresifliği yok.
- Kullanıcının bağlayıcı saydığı kaçınılacaklar: banka klişesi mavi-altın görünümü, kripto neon renkleri.

## Evidence on Hand

- Resmî kaynaklı rakamlar `data/facts.json` içinde: enflasyon, politika faizi, kredi kartı azami faiz dilimleri, stopaj oranları, TMSF limiti; kontrol tarihi 2026-09-20.
- Saatlik fiyat geçmişi `data/history.json` içinde (bot yazar).
- Referans, kullanıcı yorumu, kullanıcı sayısı, basın ya da vaka çalışması yoktur. Bunlar uydurulmaz ve tasarımda yer tutucu olarak da gösterilmez.

## Product Principles

1. Rakam, kaynak ve kontrol tarihi birlikte görünür; kaynaksız rakam yayımlanmaz.
2. Önce anlamlandır: ham fiyat yerine kullanıcı için ne ifade ettiğini sade dille söyle.
3. Tavsiye verme, yönlendirme yapma; bilgi ver ve kararı kullanıcıya bırak.
4. Önce telefon: kısa, hızlı, tek elle kullanılan akışlar.
5. Reklam içeriğin önüne geçmez, açıkça etiketlenir; güven gelirden önce gelir.

## Accessibility & Inclusion

Düşük finansal okuryazarlık nedeniyle jargon yerine açıklayıcı sade Türkçe kullanılır. Renk tek başına anlam taşımaz (artış/azalış işaret ve okla da yazılır). Metin çiftleri WCAG AA (≥4,5:1), dokunma hedefi ≥44px, `prefers-reduced-motion` saygısı.
