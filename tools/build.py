#!/usr/bin/env python3
"""Writes every page of the Levorchy site from business.json and data/looks.json.

Run it after changing a fact, a dress or a word:  python3 tools/build.py
The pages it writes are plain HTML, committed to the repo, so GitHub Pages
serves them as they are (no build step on the server).

Language: every visible text is written twice, <span class="en"> and
<span class="ar">, and the CSS shows one of them depending on <html lang>.
The language button just flips that attribute.
"""
import html
import json
import os
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = json.load(open(os.path.join(ROOT, "business.json"), encoding="utf-8"))
LOOKS = json.load(open(os.path.join(ROOT, "data", "looks.json"), encoding="utf-8"))
BY_SLUG = {l["slug"]: l for l in LOOKS}

# Draft preview: keep search engines away until Levorchy says yes and the domain points here.
PREVIEW = True

COLLECTIONS = {
    "aurora-bordeaux": {
        "en": "Aurora Bordeaux", "ar": "أورورا بوردو",
        "note_en": "Shown at Panorama Dead Sea, October 2025",
        "note_ar": "عُرضت في بانوراما البحر الميت، تشرين الأول 2025",
    },
    "bleu-imperial": {
        "en": "Bleu Imperial", "ar": "بلو إمبريال",
        "note_en": "Three-piece and two-piece couture sets",
        "note_ar": "أطقم كوتور من قطعتين وثلاث قطع",
    },
    "new-couture": {
        "en": "New couture", "ar": "أحدث القطع",
        "note_en": "The newest pieces from the atelier",
        "note_ar": "أحدث ما خرج من الأتيليه",
    },
}
TYPES = {"gown": ("Gowns", "فساتين"), "set": ("Sets", "أطقم"), "bridal": ("Bridal", "زفاف")}

# The six looks that walk the home-page runway, in order (the last one is the hero gown).
# fx/fy: where the model stands in the photo (percent), zoom: how far the camera moves in when she arrives,
# detail: a close-up photo that fades in while she holds in the spotlight (None if there is no good one).
RUNWAY = [
    ("olive-stardust", 31, 68, 1.9, "olive-stardust-2.webp"),
    ("teal-horizon", 33, 62, 1.8, "teal-horizon-2.webp"),
    ("crimson-dawn", 52, 58, 1.45, None),
    ("frozen-aurora", 51, 70, 2.5, "frozen-aurora-2.webp"),
    ("heart-of-the-aurora", 50, 68, 1.4, "heart-of-the-aurora-2.webp"),
    ("celestial-dusk", 53, 57, 1.45, "celestial-dusk-2.webp"),
]


def e(s):
    return html.escape(str(s), quote=True)


def t(en, ar, tag="span", cls=""):
    """One text in both languages."""
    c = f" {cls}" if cls else ""
    return f'<{tag} class="en{c}">{en}</{tag}><{tag} class="ar{c}" lang="ar">{ar}</{tag}>'


def price(l):
    # US dollars, the same amounts levorchy.com shows (their site converts from JOD).
    n = f"{l['price_usd']:,}"
    return t(f"${n}", f"{n} دولار")


def wa(msg):
    return f"https://wa.me/{B['whatsapp']}?text={urllib.parse.quote(msg)}"


def wa_buttons(en_msg, ar_msg, en_label, ar_label, cls="btn"):
    return (f'<a class="{cls} en" href="{e(wa(en_msg))}" target="_blank" rel="noopener">{en_label}</a>'
            f'<a class="{cls} ar" lang="ar" href="{e(wa(ar_msg))}" target="_blank" rel="noopener">{ar_label}</a>')


def img(src, alt, w, h, cls="", eager=False, sizes="(max-width: 720px) 50vw, 25vw"):
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{e(src)}" alt="{e(alt)}" width="{w}" height="{h}" {load}>'


# ---------------------------------------------------------------- page shell

NAV = [
    ("index.html", "Home", "الرئيسية"),
    ("collection.html", "Collection", "المجموعة"),
    ("story.html", "The house", "الدار"),
    ("visit.html", "Visit", "الزيارة"),
]


def page(path, title_en, desc, body, active="", extra_head="", body_cls=""):
    depth = path.count("/")
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{href}"{" aria-current=\"page\"" if href == active else ""}>{t(en, ar)}</a>'
        for href, en, ar in NAV)
    robots = '<meta name="robots" content="noindex, nofollow">\n  ' if PREVIEW else ""
    banner = (f'<div class="preview-bar">{t("Draft preview by LabsUncut, made for Levorchy. Not the official site.", "نسخة تجريبية من LabsUncut لدار ليفورشي، وليست الموقع الرسمي.")}</div>'
              if PREVIEW else "")
    book_en = "Hello Levorchy, I would like to book a private fitting."
    book_ar = "مرحباً ليفورشي، أودّ حجز موعد قياس خاص."
    doc = f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(title_en)}</title>
  <meta name="description" content="{e(desc)}">
  {robots}<meta name="theme-color" content="#0b0809">
  <meta property="og:title" content="{e(title_en)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{up}assets/img/story/show-aurora-bordeaux.webp">
  <link rel="icon" href="{up}assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="{up}assets/fonts/cormorant-garamond-latin-300-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{up}assets/css/site.css">
  <script>
    // Picks the visitor's language before the page paints, so there is no flash.
    (function () {{
      var l = null; try {{ l = localStorage.getItem('lev-lang'); }} catch (e) {{}}
      if (!l && /^ar\\b/i.test(navigator.language || '')) l = 'ar';
      if (l === 'ar') {{ document.documentElement.lang = 'ar'; document.documentElement.dir = 'rtl'; }}
      document.documentElement.classList.add('js');
    }})();
  </script>
  {extra_head}
</head>
<body class="{body_cls}">
  <a class="skip" href="#main">{t("Skip to content", "انتقل إلى المحتوى")}</a>
  {banner}
  <header class="site-header">
    <div class="header-row">
      <a class="brand" href="{up}index.html" aria-label="Levorchy, home">
        <img src="{up}assets/img/logo.png" alt="" width="42" height="31">
        <span>LEVORCHY</span>
      </a>
      <nav class="nav" id="nav" aria-label="Main">{nav}
        <span class="nav-book">{wa_buttons(book_en, book_ar, "Book a fitting", "احجزي موعد قياس", "btn btn-small")}</span>
      </nav>
      <div class="header-tools">
        <button class="lang" type="button" data-lang-toggle aria-label="Switch language"><span class="en" lang="ar">عربي</span><span class="ar">English</span></button>
        <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav"><span></span><span></span><span class="sr">Menu</span></button>
      </div>
    </div>
  </header>
  <main id="main">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div>
        <p class="footer-mark">LEVORCHY</p>
        <p class="muted">{t("House of couture · Um Uthaina, Amman", "دار أزياء راقية · أم أذينة، عمّان")}</p>
      </div>
      <div class="footer-links">
        {nav}
      </div>
      <div class="footer-contact">
        <a href="tel:{B['phone_digits']}" dir="ltr">{e(B['phone'])}</a>
        <a href="mailto:{e(B['email'])}">{e(B['email'])}</a>
        <a href="{e(B['links']['tiktok'])}" target="_blank" rel="noopener">TikTok</a>
      </div>
    </div>
    <p class="wrap copy muted">© <span data-year>2026</span> Levorchy</p>
  </footer>
  <div class="call-bar">
    <a href="tel:{B['phone_digits']}">{t("Call", "اتصال")}</a>
    {wa_buttons(book_en, book_ar, "Book a fitting", "احجزي موعد قياس", "call-bar-main")}
  </div>
  <script src="{up}assets/js/site.js" defer></script>
</body>
</html>
"""
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)


def card(l, up="", eager=False):
    a = l["images"][0]
    w, h = l["sizes"][0]
    second = ""
    if len(l["images"]) > 1:
        w2, h2 = l["sizes"][1]
        second = img(f"{up}assets/img/looks/{l['images'][1]}", "", w2, h2, "alt-img")
    col = COLLECTIONS[l["collection"]]
    return f"""<li class="card reveal" data-col="{l['collection']}" data-type="{l['type']}">
  <a href="{up}looks/{l['slug']}.html">
    <figure>{img(f"{up}assets/img/looks/{a}", l['name'], w, h, eager=eager)}{second}</figure>
    <div class="card-text">
      <h3>{e(l['name'])}</h3>
      <p class="card-col">{t(col['en'], col['ar'])}</p>
      <p class="card-price">{price(l)}</p>
    </div>
  </a>
</li>"""


# ---------------------------------------------------------------- home

def home():
    show = "assets/img/story/show-aurora-bordeaux.webp"
    looks = [BY_SLUG[r[0]] for r in RUNWAY]

    def detail(d, l):
        if not d:
            return ""
        w, h = l["sizes"][l["images"].index(d)]
        return img(f"assets/img/looks/{d}", f"{l['name']}, close-up", w, h, "detail") + f'<span class="up-close">{t("Up close", "عن قرب")}</span>'

    runway = "".join(
        f"""<article class="look" data-look data-zoom="{r[3]}" style="--fx:{r[1]}%;--fy:{r[2]}%">
      <a href="looks/{l['slug']}.html" class="look-photo">{img(f"assets/img/looks/{l['images'][0]}", l['name'], *l['sizes'][0], "walk")}{detail(r[4], l)}</a>
      <div class="look-caption">
        <p class="look-num">{t(f"Look {i + 1:02d}", f"الإطلالة {i + 1:02d}")}</p>
        <h3>{e(l['name'])}</h3>
        <p class="look-line">{t(e(l['card_en']), e(l['desc_ar']))}</p>
        <p class="look-price">{price(l)}</p>
        <a class="link-arrow" href="looks/{l['slug']}.html">{t("View the look", "شاهدي الإطلالة")}</a>
      </div>
    </article>""" for i, (l, r) in enumerate(zip(looks, RUNWAY)))

    cols = ""
    for key, c in COLLECTIONS.items():
        first = next(l for l in LOOKS if l["collection"] == key)
        if key == "aurora-bordeaux":
            first = BY_SLUG["celestial-dusk"]
        if key == "new-couture":
            first = BY_SLUG["floraison-de-lavande"]
        n = sum(1 for l in LOOKS if l["collection"] == key)
        cols += f"""<a class="col-card reveal" href="collection.html#{key}">
      {img(f"assets/img/looks/{first['images'][0]}", c['en'], *first['sizes'][0])}
      <div><h3>{t(c['en'], c['ar'])}</h3><p>{t(c['note_en'], c['note_ar'])}</p><p class="muted">{t(f"{n} pieces", f"{n} قطعة")}</p></div>
    </a>"""

    shows = "".join(
        f"""<li class="reveal"><span class="show-n">0{i + 1}</span><div><h3>{e(s['title'])}</h3><p>{t(e(s['place']), ['عمّان', 'أسبوع الموضة في باريس', 'بانوراما البحر الميت، الأردن'][i])}{(' · ' + t(e(s['date']), 'تشرين الأول 2025')) if s['date'] else ''}</p></div></li>"""
        for i, s in enumerate(B["shows"]))

    ld = {
        "@context": "https://schema.org", "@type": "ClothingStore", "name": "Levorchy",
        "description": "Haute couture and ready-to-wear fashion house in Amman, founded by Norjan Alkharouf.",
        "telephone": B["phone_digits"], "email": B["email"],
        "address": {"@type": "PostalAddress", "addressLocality": "Um Uthaina, Amman", "addressCountry": "JO"},
        "founder": {"@type": "Person", "name": B["founder"]},
        "image": "assets/img/story/show-aurora-bordeaux.webp",
        "sameAs": [B["links"]["tiktok"], B["links"]["youtube"]],
    }
    head = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'

    body = f"""
    <div class="intro" id="intro" aria-hidden="true">
      <div class="intro-inner">
        <img class="intro-logo" src="assets/img/logo.png" alt="" width="125" height="93">
        <p class="intro-word">LEVORCHY</p>
        <p class="intro-line">{t("Maison de couture · Amman", "دار الأزياء الراقية · عمّان")}</p>
      </div>
      <p class="intro-skip">{t("Tap to enter", "اضغطي للدخول")}</p>
    </div>

    <section class="hero">
      <div class="hero-media">
        {img(show, "Models in Levorchy gowns on the Aurora Bordeaux runway at Panorama Dead Sea", 799, 1400, eager=True)}
      </div>
      <div class="hero-text">
        <p class="kicker">{t("Haute couture · Amman", "هوت كوتور · عمّان")}</p>
        <h1><span class="en">Couture,<br><em>walked in light.</em></span><span class="ar" lang="ar">كوتور<br><em>يمشي في الضوء.</em></span></h1>
        <p class="hero-sub">{t("Hand-embroidered gowns and sets by Norjan Alkharouf. See them the way they were made to be seen: on the runway.", "فساتين وأطقم مطرّزة يدوياً بتوقيع نورجان الخاروف. شاهديها كما صُمّمت لتُرى: على منصّة العرض.")}</p>
        <div class="hero-ctas">
          <a class="btn" href="#runway">{t("Take your seat", "خذي مقعدك")}</a>
          <a class="btn btn-ghost" href="collection.html">{t("The collection", "المجموعة")}</a>
        </div>
      </div>
      <a class="scroll-cue" href="#runway">{t("Scroll", "مرّري")}</a>
    </section>

    <section class="runway" id="runway" aria-label="Runway">
      <div class="runway-stage">
        <div class="runway-floor" aria-hidden="true"></div>
        <p class="runway-title">{t("Aurora Bordeaux · Front row", "أورورا بوردو · الصف الأول")}</p>
        <div class="runway-looks">
    {runway}
        </div>
        <div class="runway-count" aria-hidden="true" dir="ltr"><span data-count>01</span> / {len(looks):02d}</div>
      </div>
    </section>

    <section class="section cream">
      <div class="wrap">
        <p class="kicker">{t("The collections", "المجموعات")}</p>
        <h2>{t("Thirty-five pieces, three stories", "خمس وثلاثون قطعة، وثلاث حكايات")}</h2>
        <div class="col-grid">
    {cols}
        </div>
        <p class="center"><a class="btn" href="collection.html">{t("See every piece", "شاهدي كل القطع")}</a></p>
      </div>
    </section>

    <section class="section numbers">
      <div class="wrap numbers-grid">
        <div class="reveal"><b>2021</b><p>{t("Norjan opens Levorchy as an online page, at 21", "نورجان تطلق ليفورشي كصفحة على الإنترنت، في عمر 21 عاماً")}</p></div>
        <div class="reveal"><b>2,400+</b><p>{t("fabrics in the atelier archive", "قماش في أرشيف الأتيليه")}</p></div>
        <div class="reveal"><b>{t("Hundreds", "مئات")}</b><p>{t("of hours of handwork in every gown", "من ساعات العمل اليدوي في كل فستان")}</p></div>
      </div>
    </section>

    <section class="section shows">
      <div class="wrap shows-grid">
        <div>
          <p class="kicker">{t("The shows", "العروض")}</p>
          <h2>{t("From Amman to Paris, and home to the Dead Sea", "من عمّان إلى باريس، ثم العودة إلى البحر الميت")}</h2>
          <ol class="show-list">{shows}</ol>
          <a class="link-arrow" href="story.html">{t("The story of the house", "حكاية الدار")}</a>
        </div>
        <figure class="shows-photo reveal">{img("assets/img/story/story-1.webp", "Backstage before a Levorchy show", 1411, 925)}</figure>
      </div>
    </section>

    <section class="section fitting">
      <div class="wrap fitting-inner reveal">
        <p class="kicker">{t("Private fittings", "مواعيد القياس الخاصة")}</p>
        <h2>{t("Every piece is seen in person, by appointment", "كل قطعة تُقاس شخصياً، بموعد مسبق")}</h2>
        <p>{t("Tell us which dress you love. We will arrange a private fitting at the atelier in Um Uthaina.", "أخبرينا بالفستان الذي أحببتِه، وسنرتّب لكِ موعد قياس خاص في الأتيليه في أم أذينة.")}</p>
        <div class="hero-ctas center">
          {wa_buttons("Hello Levorchy, I would like to book a private fitting.", "مرحباً ليفورشي، أودّ حجز موعد قياس خاص.", "Book on WhatsApp", "احجزي عبر واتساب")}
          <a class="btn btn-ghost" href="tel:{B['phone_digits']}">{t("Call the atelier", "اتصلي بالأتيليه")}</a>
        </div>
      </div>
    </section>
"""
    page("index.html", "Levorchy · Haute couture house in Amman",
         "Levorchy is a haute couture and ready-to-wear house in Um Uthaina, Amman, founded by Norjan Alkharouf. See the Aurora Bordeaux collection and book a private fitting.",
         body, "index.html", head, "home")


# ---------------------------------------------------------------- collection

def collection():
    chips = f'<button class="chip" aria-pressed="true" data-filter="all">{t("All", "الكل")}</button>'
    for key, c in COLLECTIONS.items():
        chips += f'<button class="chip" aria-pressed="false" data-filter="col:{key}" id="{key}">{t(c["en"], c["ar"])}</button>'
    for key, (en, ar) in TYPES.items():
        chips += f'<button class="chip" aria-pressed="false" data-filter="type:{key}">{t(en, ar)}</button>'
    cards = "\n".join(card(l, eager=i < 4) for i, l in enumerate(LOOKS))
    body = f"""
    <section class="page-head">
      <div class="wrap">
        <p class="kicker">{t("The collection", "المجموعة")}</p>
        <h1>{t("Every piece, made by hand", "كل قطعة، مصنوعة يدوياً")}</h1>
        <p class="lead">{t("Tap a piece to see it up close and book a fitting for it. Prices in US dollars.", "اضغطي على أي قطعة لمشاهدتها عن قرب وحجز موعد قياس لها. الأسعار بالدولار الأمريكي.")}</p>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="chips" role="group" aria-label="Filter">{chips}</div>
        <p class="result-count muted" aria-live="polite"><span data-shown>{len(LOOKS)}</span> {t("pieces", "قطعة")}</p>
        <ul class="grid" data-grid>
{cards}
        </ul>
      </div>
    </section>
"""
    page("collection.html", "The collection · Levorchy",
         "All Levorchy couture pieces: Aurora Bordeaux gowns, Bleu Imperial sets and new couture, with prices in US dollars. Book a private fitting in Amman.",
         body, "collection.html")


# ---------------------------------------------------------------- one look

def look(l):
    up = "../"
    col = COLLECTIONS[l["collection"]]
    slides = "".join(
        f'<figure class="slide">{img(f"{up}assets/img/looks/{f}", f"{l["name"]} by Levorchy, photo {i + 1}", *l["sizes"][i], eager=i == 0)}</figure>'
        for i, f in enumerate(l["images"]))
    dots = "".join(f'<button type="button" aria-label="Photo {i + 1}" data-dot="{i}"></button>' for i in range(len(l["images"]))) if len(l["images"]) > 1 else ""
    paras = "".join(f"<p>{e(p.strip())}</p>" for p in l["desc_en"].split("\n") if p.strip())
    more = [m for m in LOOKS if m["collection"] == l["collection"] and m["slug"] != l["slug"]][:4]
    if len(more) < 4:
        more += [m for m in LOOKS if m["slug"] != l["slug"] and m not in more][: 4 - len(more)]
    en_msg = f"Hello Levorchy, I would like to book a fitting for {l['name']} (${l['price_usd']:,})."
    ar_msg = f"مرحباً ليفورشي، أودّ حجز موعد قياس لقطعة {l['name']} ({l['price_usd']:,} دولار)."
    ld = {
        "@context": "https://schema.org", "@type": "Product", "name": l["name"],
        "brand": {"@type": "Brand", "name": "Levorchy"}, "description": l["card_en"],
        "image": [f"{up}assets/img/looks/{f}" for f in l["images"]],
        "offers": {"@type": "Offer", "price": l["price_usd"], "priceCurrency": "USD",
                   "availability": "https://schema.org/InStoreOnly"},
    }
    head = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    body = f"""
    <div class="look-page">
      <div class="gallery" data-gallery>
        <div class="slides" data-slides>{slides}</div>
        <div class="dots">{dots}</div>
      </div>
      <div class="look-info">
        <a class="back" href="{up}collection.html">{t("← The collection", "→ المجموعة")}</a>
        <p class="kicker">{t(col['en'], col['ar'])}</p>
        <h1>{e(l['name'])}</h1>
        <p class="look-price big">{price(l)}</p>
        <div class="look-desc"><div class="en">{paras}</div><div class="ar" lang="ar"><p>{e(l['desc_ar'])}</p></div></div>
        <div class="look-actions">
          {wa_buttons(en_msg, ar_msg, "Book a fitting for this piece", "احجزي موعد قياس لهذه القطعة")}
          <a class="btn btn-ghost" href="tel:{B['phone_digits']}">{t("Call the atelier", "اتصلي بالأتيليه")}</a>
        </div>
        <ul class="look-notes muted">
          <li>{t("Made by hand in the Levorchy atelier, Amman", "صُنعت يدوياً في أتيليه ليفورشي، عمّان")}</li>
          <li>{t("Seen and fitted in person, by appointment", "تُشاهد وتُقاس شخصياً، بموعد مسبق")}</li>
        </ul>
      </div>
    </div>
    <section class="section tight">
      <div class="wrap">
        <h2 class="small-h">{t("More from " + col['en'], "المزيد من " + col['ar'])}</h2>
        <ul class="grid">
{"".join(card(m, up) for m in more)}
        </ul>
      </div>
    </section>
"""
    page(f"looks/{l['slug']}.html", f"{l['name']} · Levorchy",
         f"{l['name']}, {col['en']} by Levorchy. {l['card_en'][:120]} Book a private fitting in Amman.",
         body, "collection.html", head, "look-body")


# ---------------------------------------------------------------- story

def story():
    shows = "".join(
        f"""<li class="reveal"><span class="show-n">0{i + 1}</span><div><h3>{e(s['title'])}</h3><p>{t(e(s['place']), ['عمّان، العرض الأول', 'أسبوع الموضة في باريس', 'بانوراما البحر الميت، الأردن'][i])}{(' · ' + t(e(s['date']), 'تشرين الأول 2025')) if s['date'] else ''}</p><p class="muted">{t(['The first show, a trilogy that caught the attention of the Middle East.', 'Umbra de Lumina, a study of shadow and light.', 'Back home, before international guests who travelled for the show.'][i], ['العرض الأول، ثلاثية لفتت أنظار الشرق الأوسط.', 'أومبرا دي لومينا، دراسة في الظل والضوء.', 'العودة إلى الوطن، أمام ضيوف دوليين سافروا خصيصاً للعرض.'][i])}</p></div></li>"""
        for i, s in enumerate(B["shows"]))
    body = f"""
    <section class="page-head dark">
      <div class="wrap">
        <p class="kicker">{t("The house", "الدار")}</p>
        <h1>{t("Built for expression", "صُنعت للتعبير")}</h1>
        <p class="lead">{t("Haute couture and ready-to-wear, from a page opened online in 2021 to runways in Paris and the Dead Sea.", "هوت كوتور وأزياء جاهزة، من صفحة على الإنترنت عام 2021 إلى منصّات باريس والبحر الميت.")}</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap split">
        <figure class="reveal">{img("assets/img/story/story-2.webp", "Norjan Alkharouf, founder of Levorchy", 1699, 1400)}</figure>
        <div class="prose">
          <p class="kicker">{t("The founder", "المؤسِّسة")}</p>
          <h2>Norjan Alkharouf</h2>
          <div class="en">
            <p>In October 2021, at 21, Norjan opened an online page with nothing but faith, determination and a vision: to redefine modern femininity through artistry and emotion.</p>
            <p>Three landmark shows followed. The first, in Amman, was “Savage Sophistication”. Then Paris Fashion Week, with Umbra de Lumina. In October 2025 she came home with Aurora Bordeaux at Panorama Dead Sea.</p>
            <p>Four years after her first online sketch, she opened her first atelier.</p>
          </div>
          <div class="ar" lang="ar">
            <p>في تشرين الأول 2021، وفي عمر 21 عاماً، أطلقت نورجان صفحة على الإنترنت بالإيمان والإصرار ورؤية واحدة: أن تعيد تعريف الأنوثة العصرية بالفن والإحساس.</p>
            <p>تلتها ثلاثة عروض بارزة: الأول في عمّان بعنوان «Savage Sophistication»، ثم أسبوع الموضة في باريس مع مجموعة Umbra de Lumina، وفي تشرين الأول 2025 عادت إلى الوطن بمجموعة Aurora Bordeaux في بانوراما البحر الميت.</p>
            <p>وبعد أربع سنوات من أول رسمة على الإنترنت، افتتحت أول أتيليه لها.</p>
          </div>
        </div>
      </div>
    </section>
    <section class="section cream">
      <div class="wrap split reverse">
        <figure class="reveal">{img("assets/img/story/story-3.webp", "Levorchy pieces in the atelier", 1920, 1382)}</figure>
        <div class="prose">
          <p class="kicker">{t("The atelier", "الأتيليه")}</p>
          <h2>{t("The burgundy thread", "الخيط العنابي")}</h2>
          <div class="en">
            <p>Every piece carries the house colour, burgundy: strength, depth and elegance.</p>
            <p>The atelier keeps an archive of over 2,400 fabrics, from French silks and Italian satins to hand-embroidered tulles. Each gown takes hundreds of hours, from the first sketch to the final thread: draping, hand embroidery, crystal work and structural tailoring.</p>
            <p>Before each new collection, the house holds private exhibitions for select clients, press and partners.</p>
          </div>
          <div class="ar" lang="ar">
            <p>تحمل كل قطعة لون الدار، العنابي: لون القوة والعمق والأناقة.</p>
            <p>يضمّ الأتيليه أرشيفاً من أكثر من 2,400 قماش، من الحرير الفرنسي والساتان الإيطالي إلى التول المطرّز يدوياً. ويستغرق كل فستان مئات الساعات، من الرسمة الأولى حتى الغرزة الأخيرة.</p>
            <p>وقبل كل مجموعة جديدة، تقيم الدار معارض خاصة لعدد مختار من العملاء والصحافة والشركاء.</p>
          </div>
        </div>
      </div>
    </section>
    <section class="section shows">
      <div class="wrap">
        <p class="kicker">{t("The shows", "العروض")}</p>
        <h2>{t("Three runways", "ثلاث منصّات")}</h2>
        <ol class="show-list wide">{shows}</ol>
        <figure class="wide-photo reveal">{img("assets/img/story/story-1.webp", "Backstage before a Levorchy show", 1411, 925)}</figure>
      </div>
    </section>
"""
    page("story.html", "The house · Levorchy",
         "The story of Levorchy: founded in 2021 by Norjan Alkharouf, shown in Amman, at Paris Fashion Week and at Panorama Dead Sea.",
         body, "story.html")


# ---------------------------------------------------------------- visit

def visit():
    q = urllib.parse.quote("Levorchy, Um Uthaina, Amman, Jordan")
    body = f"""
    <section class="page-head">
      <div class="wrap">
        <p class="kicker">{t("Visit", "الزيارة")}</p>
        <h1>{t("Book a private fitting", "احجزي موعد قياس خاص")}</h1>
        <p class="lead">{t("The atelier is in Um Uthaina, Amman. Fittings are by appointment, so message or call us first.", "الأتيليه في أم أذينة، عمّان. القياس بموعد مسبق، فراسلينا أو اتصلي بنا أولاً.")}</p>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap visit-grid">
        <div class="visit-card">
          <h2 class="small-h">{t("Contact the atelier", "تواصلي مع الأتيليه")}</h2>
          <ul class="contact-list">
            <li><span class="muted">{t("WhatsApp", "واتساب")}</span>{wa_buttons("Hello Levorchy, I would like to book a private fitting.", "مرحباً ليفورشي، أودّ حجز موعد قياس خاص.", "Message us", "راسلينا", "link-arrow")}</li>
            <li><span class="muted">{t("Phone", "الهاتف")}</span><a href="tel:{B['phone_digits']}" dir="ltr">{e(B['phone'])}</a></li>
            <li><span class="muted">{t("Email", "البريد")}</span><a href="mailto:{e(B['email'])}">{e(B['email'])}</a></li>
            <li><span class="muted">{t("Address", "العنوان")}</span>{t("Um Uthaina, Amman, Jordan", "أم أذينة، عمّان، الأردن")}</li>
          </ul>
          <a class="btn" href="{e(B['links']['google'])}" target="_blank" rel="noopener">{t("Get directions", "الاتجاهات")}</a>
        </div>
        <div class="map">
          <iframe title="Map of Um Uthaina, Amman" data-src="https://www.google.com/maps?q={q}&amp;output=embed" src="about:blank" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
      </div>
    </section>
"""
    page("visit.html", "Visit and book a fitting · Levorchy",
         "Book a private fitting at the Levorchy atelier in Um Uthaina, Amman. WhatsApp, phone +962 79 000 0979 or info@levorchy.com.",
         body, "visit.html")


def notfound():
    body = f"""
    <section class="page-head dark center" style="min-height:60vh">
      <div class="wrap">
        <p class="kicker">404</p>
        <h1>{t("This page has left the runway", "هذه الصفحة غادرت المنصّة")}</h1>
        <p><a class="btn" href="index.html">{t("Back to the house", "العودة إلى الدار")}</a></p>
      </div>
    </section>
"""
    page("404.html", "Page not found · Levorchy", "Page not found.", body)


if __name__ == "__main__":
    home()
    collection()
    for l in LOOKS:
        look(l)
    story()
    visit()
    notfound()
    print(f"Wrote {5 + len(LOOKS)} pages.")
