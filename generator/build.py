#!/usr/bin/env python3
"""AltınPano: altın / gümüş / döviz fiyat sitesini statik olarak üretir.

Kullanım:
    python generator/build.py            # gerçek veriyle üret (dist/ klasörüne)
    python generator/build.py --demo     # internetsiz, sahte veriyle önizleme
    python generator/build.py --demo --site-url http://localhost:8000   # yerel önizleme, config.json'a dokunmadan
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("Europe/Istanbul")
OUNCE_GRAMS = 31.1034768
UA = "Mozilla/5.0 (compatible; AltinPanoBot/1.0)"
HISTORY_FILE = ROOT / "data" / "history.json"

# --------------------------------------------------------------------------
# Varlık tanımları
# --------------------------------------------------------------------------
ASSETS = [
    dict(slug="gram-altin", name="Gram Altın", group="Altın", unit="TL", dec=2, qty="gram", grams=1.0, fine=1.0,
         about="Gram altın, 24 ayar (has) altının bir gramının Türk lirası karşılığıdır. Yatırım amaçlı en çok takip edilen altın fiyatıdır.",
         how="Uluslararası ons altın fiyatı gram cinsine çevrilir (1 ons = 31,1035 gram) ve güncel USD/TL kuruyla çarpılır."),
    dict(slug="ceyrek-altin", name="Çeyrek Altın", group="Altın", unit="TL", dec=2, qty="adet", grams=1.75, fine=0.916,
         about="Çeyrek altın, yaklaşık 1,75 gram ağırlığında ve 22 ayar (0,916) saflıkta ziynet altınıdır. Hediye ve birikim amacıyla en yaygın kullanılan altın türlerindendir.",
         how="1,75 gram × 0,916 saflık üzerinden has altın karşılığı hesaplanır. Kuyumcu satış fiyatlarında işçilik ve makas bulunduğu için gösterilen değerden farklı olabilir."),
    dict(slug="yarim-altin", name="Yarım Altın", group="Altın", unit="TL", dec=2, qty="adet", grams=3.5, fine=0.916,
         about="Yarım altın, yaklaşık 3,5 gram ağırlığında 22 ayar ziynet altınıdır ve çeyrek altının iki katı değerindedir.",
         how="3,5 gram × 0,916 saflık üzerinden has altın karşılığı hesaplanır. Kuyumcu fiyatları işçilik nedeniyle farklılık gösterebilir."),
    dict(slug="tam-altin", name="Tam Altın", group="Altın", unit="TL", dec=2, qty="adet", grams=7.0, fine=0.916,
         about="Tam altın, yaklaşık 7 gram ağırlığında 22 ayar ziynet altınıdır ve çeyrek altının dört katı değerindedir.",
         how="7 gram × 0,916 saflık üzerinden has altın karşılığı hesaplanır. Kuyumcu fiyatları işçilik nedeniyle farklılık gösterebilir."),
    dict(slug="22-ayar-altin", name="22 Ayar Altın", group="Altın", unit="TL", dec=2, qty="gram", grams=1.0, fine=0.916,
         about="22 ayar altın %91,6 saflıktadır. Bilezik ve ziynet ürünlerinde yaygın kullanılır.",
         how="Gram has altın fiyatı 0,916 ile çarpılır. Perakende fiyatlarda işçilik ayrıca eklenir."),
    dict(slug="18-ayar-altin", name="18 Ayar Altın", group="Altın", unit="TL", dec=2, qty="gram", grams=1.0, fine=0.75,
         about="18 ayar altın %75 saflıktadır. Takı ve mücevherde çok kullanılır.",
         how="Gram has altın fiyatı 0,75 ile çarpılır. Perakende fiyatlarda işçilik ayrıca eklenir."),
    dict(slug="14-ayar-altin", name="14 Ayar Altın", group="Altın", unit="TL", dec=2, qty="gram", grams=1.0, fine=0.585,
         about="14 ayar altın %58,5 saflıktadır. Günlük takılarda ve daha uygun fiyatlı mücevherde kullanılır.",
         how="Gram has altın fiyatı 0,585 ile çarpılır. Perakende fiyatlarda işçilik ayrıca eklenir."),
    dict(slug="ons-altin", name="Ons Altın", group="Altın", unit="USD", dec=2, qty="ons",
         about="Ons altın, uluslararası piyasada altının dolar cinsinden fiyatıdır (1 ons ≈ 31,1035 gram). Türkiye'deki gram altın fiyatının temel referansıdır.",
         how="Uluslararası spot altın fiyatı (XAU/USD) doğrudan gösterilir."),
    dict(slug="gumus", name="Gümüş (Gram)", group="Gümüş", unit="TL", dec=2, qty="gram",
         about="Gümüş gram fiyatı, uluslararası gümüş ons fiyatının gram ve Türk lirası karşılığıdır. Hem yatırım hem sanayi metali olarak takip edilir.",
         how="Uluslararası ons gümüş fiyatı (XAG/USD) gram cinsine çevrilir ve güncel USD/TL kuruyla çarpılır."),
    dict(slug="dolar", name="Dolar (USD/TL)", group="Döviz", unit="TL", dec=4, qty="USD",
         about="Amerikan doları / Türk lirası kuru. Türkiye'de en çok takip edilen döviz kurudur.",
         how="Türkiye Cumhuriyet Merkez Bankası'nın yayımladığı döviz satış kuru esas alınır."),
    dict(slug="euro", name="Euro (EUR/TL)", group="Döviz", unit="TL", dec=4, qty="EUR",
         about="Euro / Türk lirası kuru. Avrupa ile ticaret ve seyahat için takip edilir.",
         how="Türkiye Cumhuriyet Merkez Bankası'nın yayımladığı döviz satış kuru esas alınır."),
    dict(slug="sterlin", name="Sterlin (GBP/TL)", group="Döviz", unit="TL", dec=4, qty="GBP",
         about="İngiliz sterlini / Türk lirası kuru.",
         how="Türkiye Cumhuriyet Merkez Bankası'nın yayımladığı döviz satış kuru esas alınır."),
]
GOLD_SLUGS = [a["slug"] for a in ASSETS if "grams" in a]


# --------------------------------------------------------------------------
# Veri çekme
# --------------------------------------------------------------------------
def http_get(url: str, tries: int = 3, timeout: int = 20) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def fetch_fx() -> dict:
    """USD, EUR, GBP -> TRY. Önce TCMB, olmazsa yedek kaynak."""
    try:
        root = ET.fromstring(http_get("https://www.tcmb.gov.tr/kurlar/today.xml"))
        out = {}
        for cur in root.findall("Currency"):
            code = cur.get("CurrencyCode")
            if code in ("USD", "EUR", "GBP"):
                unit = float(cur.findtext("Unit") or 1)
                sell = cur.findtext("ForexSelling") or cur.findtext("BanknoteSelling")
                out[code] = float(sell) / unit
        if len(out) == 3:
            return out
    except Exception as e:  # noqa: BLE001
        print(f"[uyarı] TCMB alınamadı, yedeğe geçiliyor: {e}", file=sys.stderr)
    data = json.loads(http_get("https://open.er-api.com/v6/latest/USD"))
    r = data["rates"]
    usd = float(r["TRY"])
    return {"USD": usd, "EUR": usd / float(r["EUR"]), "GBP": usd / float(r["GBP"])}


def fetch_metals() -> tuple[float, float]:
    """XAU/USD ve XAG/USD ons fiyatları."""
    try:
        xau = json.loads(http_get("https://api.gold-api.com/price/XAU"))["price"]
        xag = json.loads(http_get("https://api.gold-api.com/price/XAG"))["price"]
        return float(xau), float(xag)
    except Exception as e:  # noqa: BLE001
        print(f"[uyarı] gold-api alınamadı, yedeğe geçiliyor: {e}", file=sys.stderr)
    item = json.loads(http_get("https://data-asg.goldprice.org/dbXRates/USD"))["items"][0]
    return float(item["xauPrice"]), float(item["xagPrice"])


def fetch_inputs() -> dict:
    fx = fetch_fx()
    xau, xag = fetch_metals()
    inputs = {**fx, "xau_usd": xau, "xag_usd": xag}
    if not (1 < fx["USD"] < 10000 and 100 < xau < 100000 and 1 < xag < 5000):
        raise RuntimeError(f"Mantıksız veri: {inputs}")
    return inputs


def compute_prices(i: dict) -> dict:
    gram24 = i["xau_usd"] / OUNCE_GRAMS * i["USD"]
    p = {}
    for a in ASSETS:
        if "grams" in a:
            p[a["slug"]] = gram24 * a["grams"] * a["fine"]
    p["ons-altin"] = i["xau_usd"]
    p["gumus"] = i["xag_usd"] / OUNCE_GRAMS * i["USD"]
    p["dolar"], p["euro"], p["sterlin"] = i["USD"], i["EUR"], i["GBP"]
    return p


# --------------------------------------------------------------------------
# Geçmiş
# --------------------------------------------------------------------------
def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            h = json.loads(HISTORY_FILE.read_text("utf-8"))
            h.setdefault("daily", {})
            return h
        except json.JSONDecodeError:
            print("[uyarı] history.json bozuk, sıfırdan başlanıyor", file=sys.stderr)
    return {"daily": {}, "updated": ""}


def save_history(h: dict) -> None:
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(h, sort_keys=True, separators=(",", ":")), "utf-8")


def series_for(hist: dict, slug: str) -> list[tuple[str, float]]:
    return [(d, v[slug]) for d, v in sorted(hist["daily"].items()) if slug in v]


def compute_stats(series: list[tuple[str, float]], today) -> dict:
    today_iso = today.isoformat()
    price = series[-1][1]

    def ref(days: int):
        target = (today - timedelta(days=days)).isoformat()
        c = [v for d, v in series if d <= target]
        return c[-1] if c else None

    def pct(old):
        return None if not old else (price / old - 1) * 100

    prev = [v for d, v in series if d < today_iso]
    since = (today - timedelta(days=30)).isoformat()
    last30 = [v for d, v in series if d >= since]
    return dict(
        date=today_iso,
        price=price,
        d1=pct(prev[-1] if prev else None),
        d1_abs=(price - prev[-1]) if prev else None,
        d7=pct(ref(7)),
        d30=pct(ref(30)),
        n30=len(last30),
        lo30=min(last30) if last30 else None,
        hi30=max(last30) if last30 else None,
        avg30=(sum(last30) / len(last30)) if last30 else None,
    )


def sparkline(series, w=640, h=160, pad=10):
    pts = series[-60:]
    if len(pts) < 2:
        return None
    vals = [v for _, v in pts]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    xs = [pad + i * (w - 2 * pad) / (len(vals) - 1) for i in range(len(vals))]
    ys = [h - pad - (v - lo) / span * (h - 2 * pad) for v in vals]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(zip(xs, ys)))
    area = f"{line} L{xs[-1]:.1f},{h - pad} L{xs[0]:.1f},{h - pad} Z"
    return dict(w=w, h=h, line=line, area=area, x=xs[-1], y=ys[-1],
                up=vals[-1] >= vals[0], first=pts[0][0], last=pts[-1][0], n=len(pts))


# --------------------------------------------------------------------------
# Biçimlendirme ve otomatik yorum
# --------------------------------------------------------------------------
def tr(x, d=2):
    if x is None:
        return "–"
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct_s(x):
    if x is None:
        return "–"
    return f"{'+' if x > 0.005 else ''}{tr(x, 2)}%"


def date_tr(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}.{m}.{y}"


def commentary(a: dict, st: dict) -> str:
    rnd = random.Random(f"{st['date']}:{a['slug']}")
    n, u, dec = a["name"], a["unit"], a["dec"]
    p = tr(st["price"], dec)
    out = [rnd.choice([
        f"{n} bugün {p} {u} seviyesinde.",
        f"{n} fiyatı güncel olarak {p} {u} olarak hesaplanıyor.",
        f"Son güncellemeye göre {n} {p} {u} seviyesinde işlem görüyor.",
    ])]
    d1 = st["d1"]
    if d1 is not None:
        if abs(d1) < 0.05:
            out.append("Önceki güne göre fiyat neredeyse yatay seyrediyor.")
        else:
            verb = "yükseldi" if d1 > 0 else "geriledi"
            out.append(rnd.choice([
                f"Önceki güne göre %{tr(abs(d1))} {verb}.",
                f"Günlük değişim %{tr(abs(d1))} ile {'artış' if d1 > 0 else 'düşüş'} yönünde.",
                f"Bir önceki kayda kıyasla fiyat %{tr(abs(d1))} {verb}.",
            ]))
    d7 = st["d7"]
    if d7 is not None and abs(d7) >= 0.05:
        out.append(f"Son 7 günde toplam değişim %{tr(abs(d7))} {'artış' if d7 > 0 else 'düşüş'} şeklinde.")
    if st["n30"] >= 5 and st["hi30"] and st["hi30"] > st["lo30"]:
        pos = (st["price"] - st["lo30"]) / (st["hi30"] - st["lo30"]) * 100
        out.append(
            f"Son 30 günün en düşük değeri {tr(st['lo30'], dec)} {u}, en yüksek değeri {tr(st['hi30'], dec)} {u} oldu; "
            f"güncel fiyat bu aralığın %{tr(pos, 0)} seviyesinde bulunuyor."
        )
    return " ".join(out)


def faq_for(a: dict, updated_h: str) -> list[tuple[str, str]]:
    return [
        (f"{a['name']} nasıl hesaplanır?", a["how"]),
        (f"{a['name']} fiyatı ne sıklıkla güncellenir?",
         f"Bu sayfa her saat başı otomatik olarak güncellenir. Son güncelleme: {updated_h}."),
        (f"{a['name']} için gösterilen fiyat kuyumcu ya da banka fiyatıyla aynı mı?",
         "Hayır. Burada gösterilen değerler uluslararası piyasa verilerinden hesaplanan göstergedir. "
         "Kuyumcu, banka ve döviz büroları alış-satış farkı (makas) ve işçilik uygular; işlem yapmadan önce güncel fiyatı kurumdan teyit edin."),
    ]


# --------------------------------------------------------------------------
# Demo verisi (internetsiz önizleme)
# --------------------------------------------------------------------------
def demo(now: datetime, hist: dict) -> dict:
    rnd = random.Random(42)
    xau, xag, usd, eur, gbp = 4200.0, 52.0, 41.5, 45.0, 52.5
    days = []
    for back in range(60, 0, -1):
        xau *= 1 + rnd.uniform(-0.012, 0.014)
        xag *= 1 + rnd.uniform(-0.02, 0.022)
        usd *= 1 + rnd.uniform(0.0005, 0.004)
        eur *= 1 + rnd.uniform(-0.002, 0.005)
        gbp *= 1 + rnd.uniform(-0.002, 0.005)
        d = (now.date() - timedelta(days=back)).isoformat()
        days.append((d, dict(USD=usd, EUR=eur, GBP=gbp, xau_usd=xau, xag_usd=xag)))
    for d, i in days:
        hist["daily"][d] = {k: round(v, 4) for k, v in compute_prices(i).items()}
    return dict(USD=usd * 1.002, EUR=eur * 1.001, GBP=gbp * 1.001, xau_usd=xau * 1.006, xag_usd=xag * 0.994)


# --------------------------------------------------------------------------
# Site üretimi
# --------------------------------------------------------------------------
def build_site(cfg: dict, hist: dict, prices: dict, now: datetime, out: Path) -> None:
    site = cfg["site_url"].rstrip("/")
    base = urlparse(site).path.rstrip("/")
    today = now.date()
    updated_iso = now.isoformat(timespec="seconds")
    updated_h = now.strftime("%d.%m.%Y %H:%M")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(ROOT / "static", out / "assets")
    (out / ".nojekyll").write_text("")
    if cfg.get("domain"):
        (out / "CNAME").write_text(cfg["domain"].strip() + "\n")

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html", "xml"]), trim_blocks=True, lstrip_blocks=True)
    env.filters["tr"] = tr
    env.filters["pct"] = pct_s

    items = {}
    for a in ASSETS:
        series = series_for(hist, a["slug"])
        items[a["slug"]] = {**a, "price": prices[a["slug"]], "st": compute_stats(series, today), "series": series}

    groups = []
    for a in ASSETS:
        if not groups or groups[-1]["name"] != a["group"]:
            groups.append({"name": a["group"], "items": []})
        groups[-1]["items"].append(items[a["slug"]])

    rates_try = {a["slug"]: prices[a["slug"]] for a in ASSETS if a["slug"] != "ons-altin"}
    rates_try["TRY"] = 1.0

    tools = [
        dict(slug="altin-hesaplama", name="Altın Hesaplama", short="Elindeki altının TL karşılığını veya bütçenle alabileceğin altın miktarını hesapla."),
        dict(slug="doviz-cevirici", name="Döviz Çevirici", short="TL, dolar, euro, sterlin, altın ve gümüş arasında anlık çeviri yap."),
        dict(slug="altin-getiri-hesaplama", name="Kâr / Zarar Hesaplama", short="Alış fiyatını gir; güncel değeri, kâr veya zararı ve yüzde getiriyi gör."),
    ]

    g = dict(cfg=cfg, site=site, u=lambda p: base + p, build_id=now.strftime("%Y%m%d"),
             updated_iso=updated_iso, updated_h=updated_h, groups=groups, tools=tools,
             nav=[items["gram-altin"], items["ceyrek-altin"], items["gumus"], items["dolar"]])
    sitemap: list[str] = []

    def page(path: str, template: str, **ctx) -> None:
        html = env.get_template(template).render(**g, path=path, **ctx)
        target = out / path.strip("/") / "index.html" if path != "/" else out / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, "utf-8")
        sitemap.append(path)

    def ld_graph(path, name, desc, crumbs, faq=None):
        graph = [
            {"@type": "WebPage", "@id": site + path, "url": site + path, "name": name, "description": desc,
             "inLanguage": "tr", "dateModified": updated_iso,
             "isPartOf": {"@type": "WebSite", "name": cfg["site_name"], "url": site + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": site + p} for i, (n, p) in enumerate(crumbs)]},
        ]
        if faq:
            graph.append({"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faq]})
        return {"@context": "https://schema.org", "@graph": graph}

    # Ana sayfa
    gram = items["gram-altin"]
    title = f"Altın Fiyatları, Gram Altın, Çeyrek Altın, Dolar ve Euro | {cfg['site_name']}"
    desc = (f"Gram altın {tr(gram['price'])} TL. Çeyrek altın, gümüş, dolar ve euro fiyatları her saat otomatik güncellenir; "
            f"grafik, geçmiş fiyatlar ve hesaplama araçları.")
    page("/", "index.html", title=title, description=desc, home=items,
         jsonld=ld_graph("/", title, desc, [("Ana sayfa", "/")]))

    # Varlık sayfaları
    for a in ASSETS:
        it = items[a["slug"]]
        path = f"/{a['slug']}/"
        st = it["st"]
        series = it["series"]
        rows = []
        tail = series[-31:]
        for idx in range(len(tail) - 1, 0, -1):
            rows.append(dict(date=date_tr(tail[idx][0]), price=tail[idx][1],
                             chg=(tail[idx][1] / tail[idx - 1][1] - 1) * 100 if tail[idx - 1][1] else None))
        faq = faq_for(a, updated_h)
        title = f"{a['name']} Fiyatı Bugün: {tr(it['price'], a['dec'])} {a['unit']} | {cfg['site_name']}"
        desc = (f"{a['name']} bugün {tr(it['price'], a['dec'])} {a['unit']}. "
                f"Günlük ve haftalık değişim, 30 günlük grafik, geçmiş fiyat tablosu ve hesaplama aracı.")
        page(path, "asset.html", title=title, description=desc, a=it, spark=sparkline(series),
             text=commentary(it, st), rows=rows, faq=faq,
             same=[x for x in items.values() if x["group"] == a["group"] and x["slug"] != a["slug"]],
             jsonld=ld_graph(path, title, desc, [("Ana sayfa", "/"), (a["name"], path)], faq))

    # Araçlar
    tool_meta = {
        "altin-hesaplama": ("Altın Hesaplama: Gram, Çeyrek, Yarım ve Tam Altın Kaç TL?",
                            "Gram, çeyrek, yarım, tam ve ayarlı altının güncel TL karşılığını hesaplayın veya bütçenizle ne kadar altın alabileceğinizi öğrenin."),
        "doviz-cevirici": ("Döviz Çevirici: Dolar, Euro, Sterlin, Altın ve Gümüş → TL",
                           "TL, dolar, euro, sterlin, gram altın ve gümüş arasında güncel fiyatlarla anında çeviri yapın."),
        "altin-getiri-hesaplama": ("Altın ve Döviz Kâr / Zarar Hesaplama",
                                   "Alış fiyatınızı girerek altın, gümüş veya dövizde güncel değeri, kâr ya da zararı ve yüzde getiriyi hesaplayın."),
    }
    for t in tools:
        path = f"/{t['slug']}/"
        ttl, dsc = tool_meta[t["slug"]]
        page(path, f"tool_{t['slug']}.html", title=f"{ttl} | {cfg['site_name']}", description=dsc, tool=t,
             rates=rates_try, items=items, gold=[items[s] for s in GOLD_SLUGS if s != "ons-altin"],
             jsonld=ld_graph(path, ttl, dsc, [("Ana sayfa", "/"), (t["name"], path)]))

    # Para Rehberi (kaynaklı, elle yazılmış içerik sayfası; rakamlar data/facts.json'dan gelir)
    facts = json.loads((ROOT / "data" / "facts.json").read_text("utf-8"))
    age = (today - datetime.strptime(facts["checked"], "%Y-%m-%d").date()).days
    if age > 45:
        print(f"::warning::data/facts.json {age} gün önce kontrol edildi; Para Rehberi rakamlarını güncelleyin.")
    head_extra = ""
    if cfg.get("adsense_client"):
        head_extra += (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
                       f'?client={cfg["adsense_client"]}" crossorigin="anonymous"></script>')
    if cfg.get("ga_measurement_id"):
        gid = cfg["ga_measurement_id"]
        head_extra += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>'
                       f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}'
                       f'gtag("js",new Date());gtag("config","{gid}");</script>')
    guide = (ROOT / "content" / "para-rehberi.html").read_text("utf-8")
    guide = (guide.replace("__SITE_NAME__", cfg["site_name"]).replace("__BASE__", base)
             .replace("__CANONICAL__", site + "/para-rehberi/").replace("__HEAD_EXTRA__", head_extra)
             .replace("__FACTS__", json.dumps(facts, ensure_ascii=False).replace("</", "<\\/")))
    (out / "para-rehberi").mkdir(parents=True, exist_ok=True)
    (out / "para-rehberi" / "index.html").write_text(guide, "utf-8")
    sitemap.append("/para-rehberi/")

    # Sabit sayfalar
    for slug, ttl, dsc in [
        ("hakkinda", "Hakkında ve Yasal Uyarı", "Veri kaynakları, hesaplama yöntemi ve yasal uyarı."),
        ("gizlilik", "Gizlilik Politikası", "Çerezler, reklamlar ve kişisel verilerin korunması hakkında bilgi."),
        ("iletisim", "İletişim", "Bize ulaşın."),
    ]:
        page(f"/{slug}/", f"pages/{slug}.html", title=f"{ttl} | {cfg['site_name']}", description=dsc,
             jsonld=ld_graph(f"/{slug}/", ttl, dsc, [("Ana sayfa", "/"), (ttl, f"/{slug}/")]))

    # 404 (sitemap'e girmez)
    (out / "404.html").write_text(env.get_template("404.html").render(
        **g, path="/404.html", title=f"Sayfa bulunamadı | {cfg['site_name']}",
        description="Aradığınız sayfa bulunamadı.", jsonld=None), "utf-8")

    # robots, sitemap, ads.txt
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n")
    lastmod = today.isoformat()
    urls = "".join(f"<url><loc>{site}{p}</loc><lastmod>{lastmod}</lastmod></url>" for p in sitemap)
    (out / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    if cfg.get("adsense_client"):
        pub = cfg["adsense_client"].replace("ca-", "")
        (out / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")

    print(f"[ok] {len(sitemap)} sayfa üretildi -> {out}  ({updated_h})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="sahte veriyle üret, geçmişi kaydetme")
    ap.add_argument("--out", default=str(ROOT / "dist"))
    ap.add_argument("--site-url", help="config.json'daki site_url'i geçici olarak ez (örn. yerel önizleme için http://localhost:8000)")
    args = ap.parse_args()

    cfg = json.loads((ROOT / "config.json").read_text("utf-8"))
    if args.site_url:
        cfg["site_url"] = args.site_url
    now = datetime.now(TZ)
    hist = {"daily": {}, "updated": ""} if args.demo else load_history()

    inputs = demo(now, hist) if args.demo else fetch_inputs()
    prices = compute_prices(inputs)

    if not args.demo:  # bozuk API verisine karşı koruma: son kayda göre %25'ten büyük sıçrama varsa dur
        prev_days = [d for d in sorted(hist["daily"]) if d < now.date().isoformat()]
        if prev_days:
            last = hist["daily"][prev_days[-1]]
            for k, v in prices.items():
                if k in last and last[k] and abs(v / last[k] - 1) > 0.25:
                    sys.exit(f"[hata] {k} fiyatı şüpheli sıçrama yaptı ({last[k]} -> {v}); yayın durduruldu.")

    hist["daily"].setdefault(now.date().isoformat(), {}).update({k: round(v, 4) for k, v in prices.items()})
    keep = sorted(hist["daily"])[-int(cfg.get("history_days", 400)):]
    hist["daily"] = {d: hist["daily"][d] for d in keep}
    hist["updated"] = now.isoformat(timespec="seconds")
    if not args.demo:
        save_history(hist)

    build_site(cfg, hist, prices, now, Path(args.out))


if __name__ == "__main__":
    main()
