# ParaOkur tasarım sistemi

Kararlar burada, değerler `static/base.css` (tokenlar), `components.css` (bileşenler), `motion.css` (hareket). Canlı doküman: `python generator/build.py --demo --styleguide` → `/bilesenler/` (sitemap dışı, noindex).

## Kavram: "okuyan kâğıt"

ParaOkur bir borsa terminali değil, paranın dilini öğreten sakin bir okuma masası. Kullanıcı çoğunlukla telefonda, finansal okuryazarlığı düşük, bazen borç utancıyla geliyor. Bu yüzden:

- **Sıcak kâğıt zemin, mürekkep metin.** Parlak beyaz ve soğuk petrol yok; site bir defter gibi hissettirir. Logo zaten açılan bir kitap.
- **Okurken serif, yaparken sans.** Başlıklar, uzun metin ve büyük sonuç rakamları Literata (serif) ile; düğme, etiket, tablo, girdi sistem sans ile. Serif güven ve sükunet, sans hız ve tanıdıklık verir.
- **Tek imza: işaretleyici.** En önemli rakam ve ifade, kitap okuyan birinin fosforlu kalemle çizdiği gibi kayısı bir şeritle vurgulanır (`.hl`). Süs değil bilgi: sayfada yalnızca "asıl rakam" vurgulanır. Gradient metin yok, arka plan şeridi.
- **Ölçülülük.** Gölge yalnızca yüzen katmanlarda (menü, çekmece, sözlük kartı). Kartlar 1px çizgiyle ayrılır. İkon kutuları, sayaç şablonları, süs dokuları yok.
- **Utandırmayan ton.** Borç ve kayıp ekranlarında büyük kırmızı, tehdit çubuğu ve hüküm cümlesi yok; kırmızı yalnızca kayıp rakamında, işaret ve okla birlikte kullanılır. Kaybı ve çözümü sakin cümleyle söyleriz.

### Renk yönü: neden değişti

Eski düzen (koyu petrol + sikke sarısı) iki bağımsız incelemede (tasarım eleştirisi ve kullanım testi) aynı sonuca çıktı: erişilebilirlik olarak sağlamdı ama kimlik olarak kategori klişesine (koyu teal üstünde sarı fiyat = altın/döviz terminali) çok yakındı, "banka mavi-altın" hissine kayıyordu, sarı hem fiyat hem düğme hem etiket rengi olduğu için anlamını yitiriyordu ve koyu temada bant zeminden ayırt edilemiyordu. Sıcaklık gerektiren kitle için fazla soğuktu. Değiştirildi.

Yeni yön mavi ve altın ailesinin tamamından uzak: **dut/patlıcan** (marka, eylem, bant), **kayısı işaretleyici** (tek vurgu), sıcak kâğıt yüzeyler. Sarı yok; altın fiyatı artık "altın rengi" değil, mürekkep renginde ve işaretleyici şeritli.

| Rol | Açık | Koyu | Not |
|---|---|---|---|
| `--bg` sayfa | `#F7F3EC` | `#161018` | sıcak kâğıt / patlıcan siyahı |
| `--surface` kart | `#FFFEFB` | `#211826` | |
| `--tint` dolgu | `#EEE7DA` | `#2B2031` | çip, tablo başlığı, boş durum |
| `--line` / `--line-strong` | `#DDD3C2` / `#8A7F8F` | `#3C2E43` / `#8E7D93` | ince çizgi / girdi kenarı (≥3:1) |
| `--ink` / `--mute` | `#211A26` / `#5F5666` | `#F4EDF1` / `#BDAEC0` | metin / ikincil |
| `--brand` | `#5E2154` (üstünde `#FFF`) | `#F0B8E3` (üstünde `#2A0F26`) | düğme, bağlantı, seçili çip |
| `--hl` işaretleyici | `#FFC9A6` (üstünde ink) | `#FFC9A6` (üstünde `#241520`) | tek vurgu |
| `--gain` / `--loss` | `#0B6B43` / `#B42318` | `#7FE0B0` / `#FF9E93` | işaret ve okla birlikte |
| `--band` koyu bant | `#2A1230` | `#2A1230` | hero, sonuç varyantı, footer; iki temada da patlıcan |
| `--focus` | `#1B5FD1` | `#8DB8FF` | odak halkası, bilinçli olarak marka renginden ayrı |

Kontrast (hesaplandı, WCAG AA): ink/bg 15,3 · mute/bg 6,3 · brand/bg 10,4 · beyaz/brand 11,5 · gain/surface 6,5 · loss/surface 6,5 · warn/warn-bg 6,6 · line-strong/surface 3,8 · on-band/band 15,1 · on-band-mute/band 9,2 · on-band-mute/band-2 7,9 · band-hl/band 11,5. Koyu: ink/bg 16,3 · mute/bg 8,9 · brand/surface 10,4 · on-brand/brand 10,6 · gain/surface 10,8 · loss/surface 8,6 · line-strong/bg 4,9 · on-hl/hl 11,8. Logo açık temada dut, koyu temada kayısı.

## Tipografi

- **Literata** (SIL OFL, `static/fonts/`, kendi sunucumuzda, woff2 58 KB, Türkçe Latin alt kümesi; ₺ ğ ş ı İ ö ü ç ▲ ▼ doğrulandı; değişken eksen: ağırlık 400-800, optik boyut 12-48). Okuma için tasarlanmış bir yüzdür.
- **Sistem sans** (`system-ui`): arayüz. Sıfır maliyet, kullanıcının telefonunda tanıdık.
- Sayılar her yerde `lining-nums tabular-nums`.
- Rol ölçeği (`--t-*`): meta 13 (yalnızca yasal metin/rozet) · etiket 15 · arayüz 16 · okuma gövdesi 17 (satır 1,68, en çok 68 karakter) · giriş cümlesi 19-22 · h3 19-22 · h2 24-34 · h1 32-56 · ekran başlığı 40-76 · sonuç rakamı 44-80. En büyük değer 5rem altında; iz en fazla -0,025em.
- Başlıklar `text-wrap: balance`, paragraflar `pretty`. Sola hizalı; sayı tablolarında sağa.
- Yedek: Georgia/Iowan Old Style. `font-display: swap` + preload.

## Boşluk, grid, yüzey

- 4 px tabanlı `--sp-1…12` (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96). İlgili şeyler yakın (8-16), bölümler geniş (48-64); başlığın üstü altından fazla.
- Konteyner `.shell` en çok 1200 px, yan boşluk `clamp(16px, 4vw, 32px)`; `.shell--narrow` 760 px (yasal/okuma sayfaları).
- Bölüm = `.band` (tam genişlik): zemin, `--tint` ya da `--ink` (koyu). İçerik + yan özet `.layout--side` (≥1024 px, yan sütun 352 px, yapışkan).
- Yardımcılar: `.stack` (bölüm ritmi), `.flow` (metin akışı), `.cluster` (satır içi gruplar), `.grid` (otomatik sütun, `--min`).
- Yarıçap 6 / 10 / 16 / 24 / hap. Gölge yalnızca yüzen katmanlarda.
- Hedef boyut: her etkileşimli öğe ≥44 px (`--tap`), satır içi sözlük terimi görünmez büyütülmüş isabet alanıyla.

## Bileşenler

Hepsinin canlı hali `/bilesenler/`. Ortak kural: klavye ile tam kullanım, odak halkası 3 px, renk tek başına anlam taşımaz, hareket yalnızca `motion.css`'ten.

| Bileşen | Sınıf | Not |
|---|---|---|
| Düğme | `.btn` `--primary` `--secondary` `--ghost` `--sm` `--block` | ≥48 px (`--sm` 44); basınca 0,97; `aria-busy`/`disabled` durumları |
| Girdi | `.field` > `label` + `.input-wrap` > `.input` + `.unit` | `data-money` (+ `data-decimals`): yazarken TR binlik ayracı (1.234.567,89), imleç yerinde kalır, noktalı klavyede "." ondalık virgüle döner; `aria-invalid` + `.err` (ikonlu, hata ve çözüm) |
| Seçim | `.select-wrap` > `.select` | yerel `<select>` |
| Çip | `.chip` (`aria-pressed`), `--lg`, `--on-band` | hazır seçenek, filtre, niyet |
| Sonuç kartı | `.result` > `.result-label`, `.result-num` (+ `.hl`), `.result-say` ("Bu ne demek?"), `.result-foot` (`.src-tag` + `.disclosure`) | tek büyük sayı; `aria-live="polite"`; `--ink` koyu varyant |
| Kaynak etiketi | `.src-tag` (`src_tag()` makrosu) | kurum + kontrol tarihi; bağlantılıysa 44 px |
| Açılır bilgi | `details.disclosure` | "Nasıl hesapladık?", SSS; `.formula` bloğu |
| Sekme | `[data-tabs]` > `.tablist[role=tablist]` > `.tab[role=tab]` | ok tuşları, Home/End, `aria-selected` |
| Tablo | `.table-wrap` > `.table` (`.num` sağa, `th scope`) | yatay kaydırma gölgeleri, `tabindex=0` bölge |
| Boş durum | `.empty-state` | çizim + ne olduğu + ne zaman değişeceği ("Toplanıyor") |
| Uyarı | `.callout` `--warn` `--good` `--legal` | tam çerçeve, kalın yan çizgi yok; ikon + metin |
| Sözlük terimi | `<button class="term" data-term="anahtar">` (`term()` makrosu), tanımlar `data/glossary.json` | dokunulabilir; mobilde alt kart, ≥720 px'te tetikleyicide açılan kart; Esc, dışarı dokunma, "Anladım"; odak geri döner; `aria-expanded`; JS yoksa düz metin |
| Değişim / rozet / kart / istatistik | `.chg` `.badge` `.card` `.stat` | `.chg` ▲▼ + işaret |
| İkon seti | `icon('ad')` makrosu, `templates/partials/icons.html` | 24 px ızgara, 1,75 çizgi, yuvarlak uç; tek stil |
| Reklam | `.ad` | yalnızca içerik akışında, "Reklam" etiketli, `min-height` (CLS yok) |

## Hareket

Kaynak: `static/motion.css`. İlke (emil-design-eng): sık yapılan eylemde hareket yok; hareket yalnızca geri bildirim, konum ya da durum anlatır; 300 ms altı; `ease-in` yok; yalnızca `transform` ve `opacity`; girişte yavaş, çıkışta hızlı.

Tokenlar: `--dur-press` 120 ms · `--dur-fast` 160 ms · `--dur-base` 220 ms · `--dur-sheet` 260 ms · `--dur-fill` 280 ms · `--ease-out` `cubic-bezier(.23,1,.32,1)` · `--ease-in-out` `cubic-bezier(.77,0,.175,1)` · `--ease-sheet` `cubic-bezier(.32,.72,0,1)`.

Mevcut animasyonların incelemesi:

| Önce | Sonra | Neden |
|---|---|---|
| Çekmece `.22s ease-out` (yerleşik eğri) + opaklık | `--dur-sheet` 260 ms, `--ease-sheet`, `translateY(100%)`'den | yerleşik `ease-out` zayıf; alttan gelen sheet kendi boyunu izler |
| Çekmece çıkışı (yok) | çıkış anında | kullanıcı karar verdi, sistem beklemez |
| Menü oku `.2s` düz `transition` | 160 ms, `--ease-out` | küçük durum değişimi |
| Araçlar paneli (animasyonsuz) | 220 ms `pop-down`, sol üstten | panel tetikleyiciye bağlı doğar (modal değil) |
| SSS `+` işareti `.2s` dönüşü | chevron dönüşü 160 ms | açılır bilgi tekrar tekrar kullanılır |
| Rehber çubuk dolması `1.5s` ve `.9s` | 280 ms, sürgüyle değişimde 0 ms | 1,5 s bekletmek sık kullanımda gecikme; anlam yine korunur |
| Düğme/çip (geri bildirim yok) | basınca `scale(.97)` 120 ms | arayüz dokunulduğunu duyduğunu hissettirir |
| Hover renkleri (her cihazda) | yalnızca `(hover:hover) and (pointer:fine)` | dokunmatikte takılı kalan hover yok |
| Toplu `prefers-reduced-motion: animation:none; transition:none` | konum/ölçek kalkar, opaklık geçişi ve renk kalır | "azaltılmış" hareket sıfır hareket değildir; anlam veren geçişler korunur |
| Sayı değişimi, sekme değişimi, tema anahtarı | hareket yok (bilinçli) | dakikada onlarca kez olur |

`.rise` (isteğe bağlı giriş, en çok 3-4 öğe, 50 ms aralık) sayfa başına tek bir "imza an" içindir; şimdilik hiçbir sayfada kullanılmıyor.

## Marka

`static/brand/`: `logo-mark.svg` (tek renk, `currentColor`), `logo-wordmark.svg` (Literata, path'e çevrilmiş), ikonlar ve `og-image.png` (patlıcan zemin, kayısı işaret). Yeniden üretmek için `generator/brand_assets.py` (`font` ve `brand`, Literata TTF gerekir). `konsept-*.svg` dosyaları eski sikke sarısı paletindeki arşiv taslaklarıdır, siteye bağlı değildir.

## Ton

"Sen" dili, sade Türkçe, jargon yok: her terim `term()` ile açıklanır. Borcu olan utanmaz. "Genel bilgi, tavsiye değildir". Rakam yalnızca `data/facts.json`'dan gelir, yanında kaynak ve kontrol tarihi durur.
