#!/usr/bin/env python3
"""Marka varlıklarını ve yazı tipi alt kümesini yeniden üretir (geliştirici aracı; CI'da çalışmaz).

Gereksinim (yalnızca bu betik için):  pip install fonttools brotli
Chrome/Edge (PNG için) yolu CHROME ortam değişkeniyle verilebilir.

    python generator/brand_assets.py font  <BricolageGrotesque[opsz,wdth,wght].ttf>
    python generator/brand_assets.py brand <BricolageGrotesque[opsz,wdth,wght].ttf>

Yazı tipi: Bricolage Grotesque (SIL OFL 1.1), https://github.com/ateliertriay/bricolage
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "static" / "brand"
FONT_OUT = ROOT / "static" / "fonts" / "bricolage-grotesque-tr.woff2"

INK = "#0c2b33"    # mürekkep (petrol)
COIN = "#ffb81c"   # sikke
MARK_PATH = ("M32 4a28 28 0 1 0 0 56 28 28 0 0 0 0-56ZM13 29c6-2 12-1 16 2v14c-4-3-10-4-16-2V29Z"
             "m21 8h5v9h-5v-9Zm7-7h5v16h-5V30Zm7-8h5v24h-5V22Z")


def mark_svg(fill: str = "currentColor", extra: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="{fill}" fill-rule="evenodd"{extra}>'
            f'<path d="{MARK_PATH}"/></svg>\n')


# --------------------------------------------------------------------------
# Yazı tipi: Türkçe Latin alt kümesi (₺ ğ Ğ ş Ş ı İ ö ü ç dahil), tek woff2
# --------------------------------------------------------------------------
def make_font(src: str) -> None:
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    f = instancer.instantiateVariableFont(TTFont(src), {"wdth": 100, "wght": (400, 800), "opsz": (14, 48)})
    unis = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [0x11E, 0x11F, 0x130, 0x131, 0x15E, 0x15F]
            + [0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x2022, 0x2026, 0x2032, 0x2033, 0x20AC,
               0x20BA, 0x2190, 0x2191, 0x2192, 0x2193, 0x2212, 0x2248, 0x2264, 0x2265])
    o = subset.Options()
    o.flavor = "woff2"
    o.layout_features = ["kern", "liga", "tnum", "lnum", "pnum", "case", "ccmp", "locl", "mark", "mkmk", "calt", "zero"]
    o.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    o.hinting = False
    s = subset.Subsetter(o)
    s.populate(unicodes=unis)
    s.subset(f)
    f.flavor = "woff2"
    f.save(FONT_OUT)
    cm = TTFont(FONT_OUT).getBestCmap()
    need = [0x20BA, 0x11F, 0x11E, 0x15F, 0x15E, 0x131, 0x130, 0xF6, 0xFC, 0xE7, 0xD6, 0xDC, 0xC7]
    assert all(c in cm for c in need), "Türkçe glifler eksik"
    print(f"[ok] {FONT_OUT.relative_to(ROOT)} ({FONT_OUT.stat().st_size} bayt)")


# --------------------------------------------------------------------------
# Yatay wordmark: yazı glifleri path'e çevrilir (font yüklemeden aynı görünür)
# --------------------------------------------------------------------------
def outlines(src: str, text: str, wght: int, size: float, x0: float) -> tuple[str, float]:
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    f = instancer.instantiateVariableFont(TTFont(src), {"wdth": 100, "wght": wght, "opsz": 40})
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    k, x, d = size / upm, x0, []
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x, 0)))
        d.append(pen.getCommands())
        x += gs[name].width * k - size * 0.012  # hafif sıkı iz
    return " ".join(d), x


def make_wordmark(src: str, fill: str = "currentColor") -> str:
    para, x = outlines(src, "Para", 800, 40, 60)
    okur, x2 = outlines(src, "Okur", 500, 40, x)
    w = round(x2 + 2)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 56" fill="{fill}" role="img" aria-label="ParaOkur">'
            f'<g transform="translate(0 4) scale(.75)" fill-rule="evenodd"><path d="{MARK_PATH}"/></g>'
            f'<g transform="translate(0 38.5)"><path d="{para}"/><path d="{okur}"/></g></svg>\n')


# --------------------------------------------------------------------------
# PNG'ler: Chrome ile HTML -> ekran görüntüsü
# --------------------------------------------------------------------------
def chrome() -> str:
    for p in [os.environ.get("CHROME"), r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "google-chrome", "chromium"]:
        if p and (Path(p).exists() or "\\" not in p and "/" not in p):
            return p
    sys.exit("Chrome/Edge bulunamadı (CHROME ortam değişkenini ayarla)")


def shot(html: str, out: Path, w: int, h: int) -> None:
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / "p.html"
        page.write_text(html, "utf-8")
        subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={w},{h}", f"--screenshot={out}", page.as_uri()],
                       check=True, capture_output=True)
    print(f"[ok] {out.relative_to(ROOT)}")


def icon_html(size: int, scale: float, radius: float) -> str:
    m = size * scale
    return (f'<body style="margin:0;background:transparent"><div style="width:{size}px;height:{size}px;background:{INK};'
            f'border-radius:{radius}px;display:grid;place-items:center"><div style="width:{m}px;height:{m}px;color:{COIN}">'
            f'{mark_svg().replace("<svg ", "<svg width=100% height=100% ")}</div></div></body>')


def make_brand(src: str) -> None:
    BRAND.mkdir(parents=True, exist_ok=True)
    (BRAND / "logo-mark.svg").write_text(mark_svg(), "utf-8")
    (BRAND / "logo-wordmark.svg").write_text(make_wordmark(src), "utf-8")
    fav = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{INK}"/>'
           f'<g transform="translate(7 7) scale(.78)" fill="{COIN}" fill-rule="evenodd"><path d="{MARK_PATH}"/></g></svg>\n')
    (ROOT / "static" / "favicon.svg").write_text(fav, "utf-8")
    shot(icon_html(180, 0.80, 0), BRAND / "apple-touch-icon.png", 180, 180)
    shot(icon_html(192, 0.84, 42), BRAND / "icon-192.png", 192, 192)
    shot(icon_html(512, 0.84, 112), BRAND / "icon-512.png", 512, 512)
    shot(icon_html(512, 0.56, 0), BRAND / "icon-maskable-512.png", 512, 512)  # güvenli bölge: merkez %80
    font = (ROOT / "static" / "fonts" / "bricolage-grotesque-tr.woff2").as_uri()
    og = (f'<style>@font-face{{font-family:B;src:url({font});font-weight:400 800}}'
          f'body{{margin:0;width:1200px;height:630px;background:{INK};color:#fff;font-family:B;position:relative;overflow:hidden}}'
          f'.m{{position:absolute;left:80px;top:70px;width:96px;height:96px;color:{COIN}}}'
          f'.n{{position:absolute;left:196px;top:84px;font-size:64px;font-weight:800;letter-spacing:-.02em}}.n b{{font-weight:500}}'
          f'h1{{position:absolute;left:80px;top:236px;margin:0;font-size:104px;line-height:1.04;letter-spacing:-.035em;font-weight:800;width:800px}}'
          f'p{{position:absolute;left:80px;bottom:64px;margin:0;font-size:32px;line-height:1.35;color:#9fc3c2;width:640px}}'
          f'.c{{position:absolute;right:-170px;bottom:-210px;width:560px;height:560px;border-radius:50%;background:{COIN}}}</style>'
          f'<div class=c></div><div class=m>{mark_svg().replace("<svg ", "<svg width=100% height=100% ")}</div>'
          f'<div class=n>Para<b>Okur</b></div><h1>Paranın dilini sade öğren.</h1>'
          f'<p>Resmi kaynaklı rakamlarla hesapla. Yatırım tavsiyesi değildir.</p>')
    shot(og, BRAND / "og-image.png", 1200, 630)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("font", "brand"):
        sys.exit(__doc__)
    (make_font if sys.argv[1] == "font" else make_brand)(sys.argv[2])
