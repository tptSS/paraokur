# ParaOkur tasarım sistemi

Kısa tutuldu; kararlar burada, ayrıntı `static/base.css` içindeki tokenlarda.

## Yön
Yeni kuşak finans uygulaması kalitesinde ama sakin: **açık zeminde büyük, net rakamlar; koyu petrol bantlarla ritim.**
Akılda kalan tek şey: **sikke içinde açılan kitap ve yükselen üç çubuk** (logo) ile buna eşlik eden iri, tabular rakam tipografisi. Geri kalan her şey sessiz kalır.
Ton: sade Türkçe, "genel bilgi, tavsiye değildir". Süs yok; çizgi, kutu ve etiket yalnızca bilgi taşıyorsa var.

## Renk (CSS değişkenleri, `:root`; koyu tema `[data-theme=dark]` ve sistem tercihi)
| Rol | Açık | Koyu | Kullanım |
|---|---|---|---|
| `--bg` | `#F2F6F5` | `#081A1F` | sayfa zemini |
| `--surface` | `#FFFFFF` | `#0F2830` | kart, panel |
| `--tint` | `#E4EEEC` | `#14343D` | dolgu, çip, tablo başlığı |
| `--ink` / `--mute` | `#0F2A31` / `#4A6369` | `#E6F2F1` / `#9DBDBB` | metin / ikincil metin |
| `--band` | `#0C2B33` | `#0D2F38` | tam genişlik koyu bant, footer |
| `--coin` | `#FFB81C` | `#FFC53D` | tek vurgu: sikke sarısı (üstünde `--coin-ink`) |
| `--link` | `#0B6A73` | `#6FD6D3` | bağlantı, etkileşim |
| `--gain` / `--loss` | `#0A7A4C` / `#BE3227` | `#5FDBA1` / `#FF8F84` | artış / azalış. Renk tek başına anlam taşımaz; işaret ve ok da yazılır |

Tüm metin çiftleri WCAG AA (≥4,5:1) doğrulandı. Sarı yalnızca dolgu ve büyük sayıda; küçük metinde kullanılmaz.

## Tipografi
Tek aile: **Bricolage Grotesque** (SIL OFL, `static/fonts/`, kendi sunucumuzda, woff2, 60 KB, Türkçe Latin alt kümesi; ₺ ğ ş ı İ ö ü ç doğrulandı). Değişken eksenler: ağırlık 400–800, optik boyut 14–48 (otomatik).
Sayılar her yerde `font-variant-numeric: tabular-nums`.
Ölçek (fluid, `--fs-*`): 14 / 16 / 18 / 22 / 28–32 / 40–56 / ekran başlığı 48–88. Gövde 16–17px, satır 1,6; başlık 800, satır 1,05–1,2, iz −0,02em. Satır uzunluğu ≤ 70 karakter.
Hizalama: metin sola, sayı tablolarında sağa.

## Grid ve boşluk
8px tabanı (`--sp-1`=8px … `--sp-8`=64px, `--sp-12`=96px). Konteyner `.shell` en çok 1200px, yan boşluk `clamp(16px, 4vw, 32px)`.
Bölümler **bant** (`.band`, tam genişlik) içinde; bant içeriği `.shell`. Bant çeşitleri: `--paper` (bg), `--tint`, `--ink` (koyu).
Düzenler: mobil tek sütun → ≥720px 2 sütun → ≥1024px içerik + yapışkan yan özet (`.layout`, yan sütun 320–360px). Geniş ekranda yan boşluk bırakılmaz.
Yarıçap: küçük 8, kart 16, çip/hap 999. Gölge yok denecek kadar az (yalnızca açılır menü ve çekmece).

## Bileşenler
- **Header** (`.site-head`): sticky, `--surface` zemin + alt çizgi, hero'dan ayrı. Logo (işaret + metin), ana linkler, **Araçlar** açılır menüsü (`<details>`, Esc ve dışarı tıklama ile kapanır), tema anahtarı. <900px: logo, tema, "Menü" düğmesi → **alt çekmece** (`<dialog>`, odak tuzağı, Esc).
- **Footer** (`.site-foot`): koyu bant; marka + misyon, gezinme, araçlar, kurumsal, kaynaklar ve kontrol tarihi (`facts.json`), yasal uyarı.
- **Düğme** `.btn` (birincil sarı, ikincil çerçeveli), **çip** `.chip`, **kart** `.card`, **rozet** `.badge`, **değişim** `.chg` (▲▼ + işaret).
- **Reklam** `.ad`: yalnızca içerik akışında, "Reklam" etiketli, CLS'yi önleyen `min-height`. Yan sütun yok, hesaplayıcı sonuç kartında yok.
- Odak halkası 3px `--focus`, dokunma hedefi ≥44px, `prefers-reduced-motion` saygısı.

## Hareket
Az ve anlamlı: sayı sayma ve çubuk dolma (ilerleyen PR'larda, sonuç değişince), menü/çekmece açılışı. Sayfa yüklenirken süs animasyonu yok.

## Logo ve marka
`static/brand/`: `logo-mark.svg` (tek renk, `currentColor`), `logo-wordmark.svg` (path'e çevrilmiş), üç konsept (`konsept-*.svg`), ikonlar ve `og-image.png`. Seçilen: **konsept 3**. Yeniden üretmek için `generator/brand_assets.py`.
