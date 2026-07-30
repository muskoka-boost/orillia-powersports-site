#!/usr/bin/env python3
"""
FM Recycling — static site generator.

Emits plain .html with no runtime dependencies. Run after editing:

    python3 build.py

Output is ordinary static HTML; host it anywhere. This script exists so the
prices, hours and contact details live in exactly one place.
"""

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent

# ── Business facts — single source of truth ────────────────────────────────
BIZ = {
    "name": "FM Recycling",
    "legal": "FM Recycling",
    "phone_display": "(705) 325-8118",
    "phone_href": "+17053258118",
    "email": "office@fmrecycling.ca",
    "street": "18 Kitchener Street",
    "city": "Orillia",
    "region": "ON",
    "postal": "L3V 6Z9",
    "country": "CA",
    "lat": 44.592028,
    "lng": -79.40887,
    "maps": "https://www.google.com/maps/place/F+M+Recycling/@44.592028,-79.4110587,17z/"
            "data=!3m1!4b1!4m5!3m4!1s0x0:0x2f5dc85428a837d7!8m2!3d44.592028!4d-79.40887",
    "origin": "https://www.fmrecycling.ca",
    "year": 2026,
}

HOURS = [
    ("Monday – Friday", "8:00am – 5:00pm", "1,2,3,4,5"),
    ("Saturday", "8:00am – 12:00pm", "6"),
    ("Sunday", "Closed", "0"),
]

PRICES_UPDATED = "2026-07-25"

# Transcribed from fmrecycling.ca. See brand.md — the source site renders each
# table as two unlinked text columns, so Ferrous and Aluminium row alignment was
# reconstructed from document order and should be spot-checked before launch.
PRICE_TABLES = [
    {
        "id": "ferrous", "name": "Ferrous", "unit": "$ / NT", "unit_note": "per net ton",
        "image": None,
        "blurb": "Steel and iron, priced by the net ton. Bring it in loose or bring the whole vehicle.",
        "rows": [
            ("Shred", "$175"), ("White Goods", "$155"), ("Autocast", "$215"),
            ("HMS #1", "$230"), ("HMS #2", "$200"), ("OS / Torching", "$140"),
            ("OS / Machinery", "$115"), ("P&S", "$275"), ("OS P&S", "$225"),
            ("Cars (complete)", "$215"), ("Cars – no cats / no motor", "$165"),
        ],
    },
    {
        "id": "copper-brass", "name": "Copper & Brass", "unit": "$ / LB", "unit_note": "per pound",
        "image": ("media/copper-brass.jpg", "A pile of brass and copper plumbing fittings and elbows"),
        "blurb": "Our highest-paying material. Strip it clean and bare bright pays the most.",
        "rows": [
            ("#1 Bare Bright", "$6.50"), ("#1 Copper", "$6.25"), ("#2 Copper", "$6.15"),
            ("#3 Copper", "$6.05"), ("Electric Motors", "$0.23"), ("Insulated Wires", "call"),
            ("Yellow Brass", "$3.95"), ("Taps & Faucets", "$0.40"), ("Auto Rads", "$4.00"),
        ],
    },
    {
        "id": "aluminium", "name": "Aluminium", "unit": "$ / LB", "unit_note": "per pound",
        "image": ("media/aluminium.jpg", "Aluminium tubing and extrusion scrap with painted brackets"),
        "blurb": "Siding, extrusion, wheels, rads and cans. Cleaner means a better rate.",
        "rows": [
            ("Clean Extrusion", "$1.45"), ("MLC", "$1.15"), ("Painted / Siding", "$1.10"),
            ("Irony Aluminium", "$0.10"), ("Cast Aluminium", "$0.95"), ("Clean Al Rads", "$1.00"),
            ("Clean Al / Cu Rads", "$3.85"), ("Clean Al Wheels", "$1.65"),
            ("Pop Cans (clear bags only)", "$0.85"),
        ],
    },
    {
        "id": "stainless", "name": "Stainless & Misc", "unit": "$ / LB", "unit_note": "per pound",
        "image": ("media/stainless.jpg", "Stainless steel pipe and tube offcuts stacked together"),
        "blurb": "Stainless, lead, batteries and the electrical odds and ends.",
        "rows": [
            ("Clean Stainless", "$0.29"), ("Compressors", "$0.13"), ("Ballasts", "$0.15"),
            ("Electronic Ballasts", "$0.05"), ("Starters", "$0.22"), ("Alternators", "$0.44"),
            ("Clean Lead", "$0.45"), ("Batteries (lead acid)", "$0.20"),
        ],
    },
]

NOT_ACCEPTED = ["Propane tanks", "Fuel tanks", "Fire extinguishers"]

SERVICES = [
    {
        "id": "public-yard", "name": "Public Yard", "icon": "scale",
        "image": ("media/metal-shop.jpg", "The metal shop bench at FM Recycling with tools and sorted non-ferrous offcuts"),
        "short": "Drive in, weigh in, get paid. No appointment, no account, no minimum.",
        "long": "We go out of our way to make sure your recycling process is made as easy as "
                "possible. Our staff are dedicated to providing you with top quality customer "
                "service and are here to answer any and all of your scrap metal questions. Turn "
                "your scrap into cash today — fast, fair and friendly.",
        "ticks": ["Open to the public", "Weighed on site", "Same-day payment",
                  "Homeowners, contractors and businesses"],
    },
    {
        "id": "bins", "name": "Bin Services", "icon": "bin",
        "image": ("media/bins.jpg", "A green FM Recycling roll-off bin marked FMR Scrap Buyers beside an orange roll-off truck"),
        "short": "Roll-off bins dropped where you need them — driveway, shop or jobsite.",
        "long": "Since 2000, FM Recycling has provided a wide range of recycling services at "
                "great market rates. From driveway to jobsite, we drop it where you need it. "
                "Call us and see what we can do for you and your company today.",
        "ticks": ["Roll-off bins", "Driveway or jobsite delivery", "Scheduled swap-outs",
                  "Serving Orillia and area since 2000"],
    },
    {
        "id": "trucking", "name": "Trucking & Float", "icon": "truck",
        "image": ("media/flatbed.jpg", "An FM Recycling flatbed trailer parked at the yard"),
        "short": "Too big to move yourself? We have the trucks and the float to come get it.",
        "long": "Here at FMR, we have the means and the trucks to move your material in the most "
                "cost effective and responsible way. On time. On budget. On the flatbed. Call our "
                "office to find out more about our rates and availability.",
        "ticks": ["Flatbed hauling", "Float service for machinery", "On-site collection",
                  "Call the office for rates"],
    },
]

# ── Icons ──────────────────────────────────────────────────────────────────
I = {
    "scale": '<path d="M12 4v16M7 20h10"/><path d="m5 8 3.5 6h-7L5 8ZM19 8l3.5 6h-7L19 8ZM5 8l7-2 7 2"/>',
    "bin": '<path d="M4 8h16l-1.5 12h-13L4 8Z"/><path d="M9 8V5h6v3"/><path d="M10 12v4M14 12v4"/>',
    "truck": '<path d="M2 7h11v10H2z"/><path d="M13 10h4l3 3.5V17h-7"/><circle cx="6" cy="18.5" r="1.8"/><circle cx="17" cy="18.5" r="1.8"/>',
    "cash": '<rect x="2" y="6" width="20" height="12" rx="1.5"/><circle cx="12" cy="12" r="2.8"/><path d="M6 12h.01M18 12h.01"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l3.5 2"/>',
    "pin": '<path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
    "phone": '<path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 5 5L15 12l5 2v3a2 2 0 0 1-2.2 2A16 16 0 0 1 4 5.2 2 2 0 0 1 6 3Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    "check": '<path d="m4 12 5 5L20 6"/>',
    "arrow": '<path d="M4 12h15"/><path d="m13 6 6 6-6 6"/>',
    "ban": '<circle cx="12" cy="12" r="9"/><path d="m6 6 12 12"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 5.5a3.2 3.2 0 0 1 0 6.3M17.5 20a6.5 6.5 0 0 0-2.2-4.9"/>',
    "recycle": '<path d="M8 4.5 5 10h6L8 4.5Z"/><path d="m16.5 9 3 5.5h-6L16.5 9Z"/><path d="M11 19.5H5.5a1.5 1.5 0 0 1-1.3-2.2L6 14"/><path d="M13 19.5h5.5a1.5 1.5 0 0 0 1.3-2.2"/><path d="m11 17.5 2 2-2 2"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{I[name]}</svg>')


def tick(t):
    return f'<li>{icon("check")}<span>{t}</span></li>'


NAV = [
    ("prices.html", "Prices"),
    ("services.html", "Services"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]


def nav(active):
    CUR = ' aria-current="page"'
    items = "".join(
        '<li><a href="{}"{}>{}</a></li>'.format(h_, CUR if h_ == active else "", l)
        for h_, l in NAV)
    return f"""
<a class="skip-link" href="#main">Skip to content</a>

<div class="utility">
  <div class="utility-inner">
    <span class="yard-state" data-yard-state hidden></span>
    <span>Yard: Mon–Fri 8am–5pm &middot; Sat 8am–12pm</span>
    <span class="sep" aria-hidden="true">|</span>
    <a href="tel:{BIZ['phone_href']}">{BIZ['phone_display']}</a>
    <span class="sep" aria-hidden="true">|</span>
    <span>{BIZ['street']}, {BIZ['city']}</span>
  </div>
</div>

<header class="site-nav">
  <div class="nav-inner">
    <a class="brand" href="index.html" aria-label="{BIZ['name']} — home">
      <img src="media/fm-logo.png" alt="{BIZ['name']}" width="559" height="256">
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false"
            aria-controls="nav-links" aria-label="Open menu">
      {icon("menu", "icon-open")}{icon("close", "icon-close")}
    </button>
    <nav id="nav-links" class="nav-links" aria-label="Main">
      <ul style="display:contents">{items}</ul>
      <a class="btn btn-primary nav-cta" href="tel:{BIZ['phone_href']}">
        {icon("phone")} {BIZ['phone_display']}</a>
    </nav>
  </div>
</header>"""


FOOTER = f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="footer-logo" href="index.html">
          <img src="media/fm-logo.png" alt="{BIZ['name']}" width="559" height="256">
        </a>
        <p class="footer-about">
          Orillia's local scrap yard. Ferrous and non-ferrous metals bought at honest
          weights with same-day payment. Open to the public.
        </p>
      </div>
      <div class="footer-col">
        <h2>Site</h2>
        <ul>
          <li><a href="prices.html">Current Prices</a></li>
          <li><a href="services.html">Services</a></li>
          <li><a href="about.html">About</a></li>
          <li><a href="contact.html">Contact &amp; Hours</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h2>Services</h2>
        <ul>
          <li><a href="services.html#public-yard">Public Yard</a></li>
          <li><a href="services.html#bins">Bin Services</a></li>
          <li><a href="services.html#trucking">Trucking &amp; Float</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h2>Find us</h2>
        <ul class="footer-contact">
          <li>{icon("phone")}<a href="tel:{BIZ['phone_href']}">{BIZ['phone_display']}</a></li>
          <li>{icon("mail")}<a href="mailto:{BIZ['email']}">{BIZ['email']}</a></li>
          <li>{icon("pin")}<a href="{BIZ['maps']}" target="_blank" rel="noopener">
            {BIZ['street']}<br>{BIZ['city']}, {BIZ['region']} {BIZ['postal']}</a></li>
          <li>{icon("clock")}<span>Mon–Fri 8am–5pm<br>Sat 8am–12pm</span></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {BIZ['year']} {BIZ['name']}. All rights reserved.</span>
      <span>Scrap metal &amp; recycling &middot; Orillia, Ontario</span>
    </div>
    <p class="footer-made" style="padding-bottom:26px">
      Created by <a href="https://muskokadigitalboost.ca" target="_blank" rel="noopener">Muskoka Digital Boost</a>
    </p>
  </div>
</footer>"""


def biz_ld():
    data = {
        "@context": "https://schema.org",
        "@type": "RecyclingCenter",
        "@id": BIZ["origin"] + "/#business",
        "name": BIZ["name"],
        "description": "Scrap metal yard in Orillia, Ontario buying ferrous and non-ferrous "
                       "metals with honest weights and same-day payment. Roll-off bins, "
                       "flatbed hauling and on-site collection.",
        "url": BIZ["origin"] + "/",
        "telephone": BIZ["phone_display"],
        "email": BIZ["email"],
        "image": BIZ["origin"] + "/media/yard-hero.jpg",
        "logo": BIZ["origin"] + "/media/fm-logo.png",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": BIZ["street"],
            "addressLocality": BIZ["city"],
            "addressRegion": BIZ["region"],
            "postalCode": BIZ["postal"],
            "addressCountry": BIZ["country"],
        },
        "geo": {"@type": "GeoCoordinates", "latitude": BIZ["lat"], "longitude": BIZ["lng"]},
        "hasMap": BIZ["maps"],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "opens": "08:00", "closes": "17:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday",
             "opens": "08:00", "closes": "12:00"},
        ],
        "areaServed": [{"@type": "City", "name": n} for n in
                       ["Orillia", "Barrie", "Gravenhurst", "Bracebridge", "Midland",
                        "Coldwater", "Washago", "Severn", "Ramara", "Oro-Medonte"]],
        "knowsAbout": ["Scrap metal recycling", "Ferrous metal", "Copper", "Aluminium",
                       "Stainless steel", "Roll-off bins", "Auto recycling"],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def page(*, slug, title, description, body, og_image="media/yard-hero.jpg", extra_ld=""):
    canonical = f"{BIZ['origin']}/{'' if slug == 'index.html' else slug}"
    return f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{BIZ['name']}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BIZ['origin']}/{og_image}">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{BIZ['origin']}/{og_image}">
<meta name="theme-color" content="#0d0d0d">
<meta name="geo.region" content="CA-ON">
<meta name="geo.placename" content="Orillia">

<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="fonts/barlow-condensed-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/barlow-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/styles.css">
{extra_ld}
</head>
<body>
{nav(slug)}
<main id="main">
{body}
</main>
{FOOTER}
<script src="js/site.js" defer></script>
</body>
</html>
"""


def cta_band(heading, sub, secondary=None):
    sec = f'<a class="btn btn-outline btn-lg" href="{secondary[0]}">{secondary[1]}</a>' if secondary else ""
    return f"""
<section class="section">
  <div class="container">
    <div class="cta-band reveal">
      <h2 class="cond">{heading}</h2>
      <p>{sub}</p>
      <div class="cta-actions">
        <a class="btn btn-dark btn-lg" href="tel:{BIZ['phone_href']}">{icon("phone")} Call {BIZ['phone_display']}</a>
        {sec}
      </div>
    </div>
  </div>
</section>"""


def hours_table(dark=False):
    rows = "".join(
        f'<tr data-dow="{dow}"><td>{d}</td><td>{t}</td></tr>' for d, t, dow in HOURS)
    return f"""<table class="hours-table"><caption class="visually-hidden">Yard opening hours</caption>
<tbody>{rows}</tbody></table>
<p style="font-size:.88rem;color:{'#9aa2ab' if dark else 'var(--gray-500)'};margin-top:12px">
  The metal shop closes 10 minutes before the yard.</p>"""


def not_accepted_block():
    items = "".join(f'<li>{icon("ban")}<span>{n}</span></li>' for n in NOT_ACCEPTED)
    return f"""
<div class="alert alert-light reveal">
  <h3 class="cond">We cannot accept</h3>
  <p>For everyone's safety these are turned away at the gate — no exceptions.</p>
  <ul class="nope">{items}</ul>
</div>"""


def price_table_html(t, compact=False):
    rows = "".join(
        '<tr><td class="material">{}</td><td class="price{}">{}</td></tr>'.format(
            m, " call" if p == "call" else "", "Call us" if p == "call" else p)
        for m, p in t["rows"])
    img = ""
    if t["image"] and not compact:
        src, alt = t["image"]
        img = f'<img src="{src}" alt="{alt}" width="1100" height="825" loading="lazy" decoding="async">'
    blurb = f'<p style="padding:16px 20px 0;color:var(--gray-600);font-size:.95rem">{t["blurb"]}</p>' if not compact else ""
    return f"""
<section class="price-cat reveal" id="{t['id']}">
  <div class="price-cat-head">
    <h3 class="cond">{t['name']}</h3>
    <span class="unit">{t['unit']}</span>
    {img}
  </div>
  {blurb}
  <table class="price-table">
    <caption class="visually-hidden">{t['name']} prices, {t['unit_note']}</caption>
    <thead><tr><th scope="col">Material</th><th scope="col" style="text-align:right">{t['unit']}</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


PRICE_DISCLAIMER = f"""
<div class="price-note reveal">
  <strong>Prices change with the market.</strong> Last updated
  <time datetime="{PRICES_UPDATED}">{PRICES_UPDATED}</time>. These are a guide only — call
  <a href="tel:{BIZ['phone_href']}" style="color:#6b5410;font-weight:700;text-decoration:underline">{BIZ['phone_display']}</a>
  for today's rate before you load up. Prices are subject to change without notice and
  final settlement is based on weights taken at our scale.
</div>"""


# ── Pages ──────────────────────────────────────────────────────────────────
def build_index():
    svc = "".join(f"""
      <article class="svc card-hover reveal" data-delay="{i*70}">
        <div class="svc-media"><img src="{s['image'][0]}" alt="{s['image'][1]}"
             width="1100" height="825" loading="lazy" decoding="async"></div>
        <div class="svc-body">
          <h3 class="cond">{s['name']}</h3>
          <p>{s['short']}</p>
          <a class="link-arrow" href="services.html#{s['id']}">More {icon("arrow")}</a>
        </div>
      </article>""" for i, s in enumerate(SERVICES))

    # Each category gets its own material photo; ferrous falls back to the yard.
    TEASER_IMG = {
        "ferrous": ("media/grapple.jpg", "A grapple attachment resting in the yard among ferrous scrap"),
    }
    teaser = "".join(f"""
      <a class="svc card-hover reveal" href="prices.html#{t['id']}" data-delay="{i*60}">
        <div class="svc-media" style="aspect-ratio:16/10"><img src="{(t['image'] or TEASER_IMG[t['id']])[0]}"
             alt="{(t['image'] or TEASER_IMG[t['id']])[1]}" width="1100" height="825"
             loading="lazy" decoding="async"></div>
        <div class="svc-body" style="padding:20px">
          <h3 class="cond">{t['name']}</h3>
          <p style="margin-bottom:12px">{t['blurb']}</p>
          <span class="link-arrow">See {len(t['rows'])} prices {icon("arrow")}</span>
        </div>
      </a>""" for i, t in enumerate(PRICE_TABLES))

    steps = "".join(f"""
      <div class="step reveal" data-delay="{i*70}"><h3 class="cond">{t}</h3><p>{d}</p></div>"""
      for i, (t, d) in enumerate([
        ("Load it up", "Sort it if you can — clean material pays more. No need to call ahead or book a time."),
        ("Drive onto the scale", "We weigh your load on site. Ask our staff anything; they will tell you straight what a grade is worth."),
        ("Get paid", "Same day, before you leave. Honest weights, competitive prices, no waiting on a cheque."),
      ]))

    body = f"""
<section class="hero">
  <img class="hero-bg" src="media/yard-hero.jpg" alt="" width="1726" height="970" fetchpriority="high" decoding="async">
  <div class="hero-inner">
    <div class="hero-copy">
      <h1 class="cond">Turn unwanted items <em>into cash</em></h1>
      <p class="hero-sub">
        Orillia's local scrap yard. We buy ferrous and non-ferrous metal at honest weights,
        competitive prices and same-day payment. Open to the public — fast, fair and friendly.
      </p>
      <div class="hero-actions">
        <a class="btn btn-primary btn-lg" href="prices.html">See today's prices {icon("arrow")}</a>
        <a class="btn btn-ghost-light btn-lg" href="tel:{BIZ['phone_href']}">{icon("phone")} {BIZ['phone_display']}</a>
      </div>
      <div class="hero-facts">
        <span class="hero-fact">{icon("cash")} Paid the same day</span>
        <span class="hero-fact">{icon("scale")} Weighed on site</span>
        <span class="hero-fact">{icon("users")} Open to the public</span>
      </div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="buy-heading">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">What we buy</span>
      <h2 class="cond" id="buy-heading">Steel, copper, aluminium, brass, stainless &amp; more</h2>
      <p>Whether you're a homeowner cleaning out a garage, a contractor with jobsite scrap,
         or a business needing regular pickups — bring it in and get paid on the spot.</p>
    </div>
    <div class="grid grid-4">{teaser}</div>
    <p style="margin-top:28px">
      <a class="link-arrow" href="prices.html">See the full price list {icon("arrow")}</a>
    </p>
  </div>
</section>

<section class="section section-dark" aria-labelledby="how-heading">
  <div class="container">
    <div class="section-head center reveal">
      <span class="eyebrow">How it works</span>
      <h2 class="cond" id="how-heading">Three steps, no appointment</h2>
    </div>
    <div class="steps">{steps}</div>
  </div>
</section>

<section class="section section-tint" aria-labelledby="svc-heading">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Services</span>
      <h2 class="cond" id="svc-heading">More than a drop-off</h2>
      <p>Bins for the jobsite, flatbeds for the heavy stuff, and a yard that's open to anyone.</p>
    </div>
    <div class="grid grid-3">{svc}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">Before you come</span>
        <h2 class="cond" style="font-size:clamp(1.8rem,3.6vw,2.6rem);margin-bottom:16px;text-transform:uppercase">
          Hours &amp; what we can't take</h2>
        {hours_table()}
      </div>
      <div class="reveal" data-delay="80">{not_accepted_block()}</div>
    </div>
  </div>
</section>

{cta_band("Got metal? Get paid.",
          "Call the office for today's rate, or just drive in during yard hours.",
          secondary=("prices.html", "See prices"))}
"""
    return page(slug="index.html",
                title="FM Recycling | Scrap Metal Yard in Orillia, Ontario — Paid Same Day",
                description="Orillia scrap yard buying steel, copper, aluminium, brass and "
                            "stainless. Honest weights, competitive prices, same-day payment. "
                            "Open to the public. Call (705) 325-8118.",
                body=body, extra_ld=biz_ld())


def build_prices():
    tables = "".join(price_table_html(t) for t in PRICE_TABLES)
    jump = "".join(
        f'<a class="btn btn-outline" href="#{t["id"]}" style="padding:9px 16px;font-size:.9rem">{t["name"]}</a>'
        for t in PRICE_TABLES)
    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">Prices</span>
    </nav>
    <h1 class="cond">Current scrap prices</h1>
    <p>What we're paying at the Orillia yard right now. Ferrous by the net ton,
       everything else by the pound.</p>
  </div>
</section>

<section class="section" aria-labelledby="pricelist-heading">
  <div class="container">
    <h2 id="pricelist-heading" class="visually-hidden">Price list by material</h2>
    {PRICE_DISCLAIMER}
    <nav style="display:flex;flex-wrap:wrap;gap:9px;margin-bottom:34px" class="reveal" aria-label="Jump to material">{jump}</nav>
    {tables}
    {not_accepted_block()}
  </div>
</section>

{cta_band("Not sure what you've got?",
          "Bring it in and we'll grade it at the scale, or call and describe it — we'll tell you straight.",
          secondary=("services.html", "Our services"))}
"""
    return page(slug="prices.html",
                title="Scrap Metal Prices in Orillia | FM Recycling",
                description="Current scrap metal prices at FM Recycling in Orillia: ferrous per "
                            "net ton, copper, brass, aluminium and stainless per pound. "
                            "Updated regularly — call (705) 325-8118 for today's rate.",
                body=body, og_image="media/copper-brass.jpg")


def build_services():
    blocks = "".join(f"""
<section class="section {'section-tint' if i % 2 else ''}" id="{s['id']}">
  <div class="container">
    <div class="split">
      <div class="{'reveal' if i % 2 == 0 else 'reveal'}" {'style="order:2"' if i % 2 else ''}>
        <span class="eyebrow">{s['name']}</span>
        <h2 class="cond" style="font-size:clamp(1.8rem,3.8vw,2.7rem);margin-bottom:16px;text-transform:uppercase">{s['name']}</h2>
        <p style="font-size:1.08rem;color:var(--gray-700);margin-bottom:14px">{s['short']}</p>
        <p style="color:var(--gray-600)">{s['long']}</p>
        <ul class="ticks">{''.join(tick(t) for t in s['ticks'])}</ul>
        <p style="margin-top:24px">
          <a class="btn btn-primary" href="tel:{BIZ['phone_href']}">{icon("phone")} Call the office</a>
        </p>
      </div>
      <figure class="split-media reveal" data-delay="80" {'style="order:1"' if i % 2 else ''}>
        <img src="{s['image'][0]}" alt="{s['image'][1]}" width="1500" height="1125"
             loading="lazy" decoding="async" style="aspect-ratio:4/3">
      </figure>
    </div>
  </div>
</section>""" for i, s in enumerate(SERVICES))

    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">Services</span>
    </nav>
    <h1 class="cond">Services</h1>
    <p>A public yard anyone can drive into, roll-off bins for the jobsite, and the
       trucks to move whatever won't fit in a pickup.</p>
  </div>
</section>
{blocks}
{cta_band("Need a bin or a pickup?",
          "Call the office and we'll sort out rates, sizes and timing.",
          secondary=("prices.html", "See prices"))}
"""
    return page(slug="services.html",
                title="Roll-Off Bins, Flatbed Hauling & Public Scrap Yard | FM Recycling Orillia",
                description="FM Recycling in Orillia: public scrap yard open to everyone, "
                            "roll-off bin rental for driveways and jobsites, plus flatbed and "
                            "float hauling for heavy material.",
                body=body, og_image="media/bins.jpg")


def build_about():
    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">About</span>
    </nav>
    <h1 class="cond">Your leading local scrap yard</h1>
    <p>Fast, fair, and open to the public.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">About us</span>
        <h2 class="cond" style="font-size:clamp(1.8rem,3.8vw,2.6rem);margin-bottom:18px;text-transform:uppercase">
          Turn unwanted items into cash</h2>
        <p style="font-size:1.08rem;color:var(--gray-700);margin-bottom:16px">
          Bring in your unwanted metal and get paid on the spot. We buy ferrous and
          non-ferrous metals including steel, copper, aluminium, brass, stainless, and more.
        </p>
        <p style="color:var(--gray-600);margin-bottom:16px">
          Whether you're a homeowner cleaning out a garage, a contractor with jobsite scrap,
          or a business needing regular pickups, our yard offers honest weights, competitive
          prices, and same-day payment. We also provide roll-off bins, flatbed hauling, and
          on-site collection for larger loads.
        </p>
        <p style="color:var(--gray-600)">
          Turn your scrap into cash while helping the environment — fast, friendly service
          every time.
        </p>
        <ul class="ticks" style="margin-top:22px">
          {tick("Providing recycling services since 2000")}
          {tick("Honest weights taken on our own scale")}
          {tick("Same-day payment, every time")}
          {tick("Staff who will actually answer your scrap questions")}
        </ul>
      </div>
      <figure class="split-media reveal" data-delay="80">
        <img src="media/metal-shop.jpg" width="1000" height="1333" loading="lazy" decoding="async"
             alt="The metal shop bench at FM Recycling with bolt cutters and sorted non-ferrous offcuts">
        <figcaption>The metal shop, where non-ferrous gets sorted and graded.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="section section-dark">
  <div class="container">
    <div class="section-head center reveal">
      <span class="eyebrow">Why bring it to FMR</span>
      <h2 class="cond">Fast, fair and friendly</h2>
    </div>
    <div class="grid grid-3">
      <div class="card reveal" style="background:var(--steel-800);border-color:var(--steel-700)">
        <div class="icon-box">{icon("scale")}</div>
        <h3 class="cond" style="color:#fff;text-transform:uppercase">Honest weights</h3>
        <p style="color:#b6bdc5">Everything is weighed on our own scale, on site, in front of you. No estimates.</p>
      </div>
      <div class="card reveal" data-delay="70" style="background:var(--steel-800);border-color:var(--steel-700)">
        <div class="icon-box">{icon("cash")}</div>
        <h3 class="cond" style="color:#fff;text-transform:uppercase">Same-day payment</h3>
        <p style="color:#b6bdc5">You get paid before you leave the yard. No invoicing, no waiting on a cheque.</p>
      </div>
      <div class="card reveal" data-delay="140" style="background:var(--steel-800);border-color:var(--steel-700)">
        <div class="icon-box">{icon("users")}</div>
        <h3 class="cond" style="color:#fff;text-transform:uppercase">Open to the public</h3>
        <p style="color:#b6bdc5">One bucket or a full float — homeowners are as welcome as contractors.</p>
      </div>
    </div>
  </div>
</section>

{cta_band("Come see us in Orillia",
          "18 Kitchener Street. Mon–Fri 8am–5pm, Sat 8am–12pm.",
          secondary=("contact.html", "Directions &amp; hours"))}
"""
    return page(slug="about.html",
                title="About FM Recycling | Orillia Scrap Metal Yard Since 2000",
                description="FM Recycling is Orillia's local scrap yard — ferrous and "
                            "non-ferrous metals, honest weights, same-day payment, open to "
                            "the public. Providing recycling services since 2000.",
                body=body, og_image="media/metal-shop.jpg")


def build_contact():
    map_src = (f"https://www.google.com/maps?q={BIZ['lat']},{BIZ['lng']}"
               f"&z=16&output=embed")
    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">Contact</span>
    </nav>
    <h1 class="cond">Contact &amp; hours</h1>
    <p>18 Kitchener Street, Orillia. Drive in during yard hours — no appointment needed.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="contact-grid">
      <div class="reveal">
        <div class="grid" style="gap:12px;margin-bottom:30px">
          <a class="contact-method" href="tel:{BIZ['phone_href']}">
            <span class="icon-box">{icon("phone")}</span>
            <span>
              <span class="label">Phone</span>
              <span class="value">{BIZ['phone_display']}</span>
              <span class="meta">Best for today's prices and bin bookings</span>
            </span>
          </a>
          <a class="contact-method" href="mailto:{BIZ['email']}">
            <span class="icon-box">{icon("mail")}</span>
            <span>
              <span class="label">Email</span>
              <span class="value">{BIZ['email']}</span>
              <span class="meta">For quotes and account enquiries</span>
            </span>
          </a>
          <a class="contact-method" href="{BIZ['maps']}" target="_blank" rel="noopener">
            <span class="icon-box">{icon("pin")}</span>
            <span>
              <span class="label">Yard address</span>
              <span class="value">{BIZ['street']}, {BIZ['city']}, {BIZ['region']} {BIZ['postal']}</span>
              <span class="meta">Open in Google Maps</span>
            </span>
          </a>
        </div>

        <h2 class="cond" style="font-size:1.5rem;text-transform:uppercase;margin-bottom:14px">Yard hours</h2>
        {hours_table()}

        <div style="margin-top:26px">{not_accepted_block()}</div>
      </div>

      <div class="reveal" data-delay="80">
        <iframe class="map-embed" src="{map_src}" title="Map showing FM Recycling at 18 Kitchener Street, Orillia"
                loading="lazy" referrerpolicy="no-referrer-when-downgrade" style="margin-bottom:28px"></iframe>

        <div class="card" style="padding:clamp(22px,4vw,32px)">
          <h2 class="cond" style="font-size:1.5rem;text-transform:uppercase;margin-bottom:6px">Send a message</h2>
          <p style="color:var(--gray-600);font-size:.95rem;margin-bottom:22px">
            For anything urgent — prices, a bin, a pickup — please call. We answer the phone.
          </p>
          <form id="contact-form" novalidate>
            <div class="form-field">
              <label for="f-name">Name <span class="req">*</span></label>
              <input id="f-name" name="name" type="text" required autocomplete="name">
            </div>
            <div class="form-field">
              <label for="f-phone">Phone</label>
              <input id="f-phone" name="phone" type="tel" autocomplete="tel">
            </div>
            <div class="form-field">
              <label for="f-email">Email <span class="req">*</span></label>
              <input id="f-email" name="email" type="email" required autocomplete="email">
            </div>
            <div class="form-field">
              <label for="f-subject">What's it about?</label>
              <select id="f-subject" name="subject">
                <option>Scrap prices</option>
                <option>Roll-off bin</option>
                <option>Flatbed or float pickup</option>
                <option>Commercial account</option>
                <option>Something else</option>
              </select>
            </div>
            <div class="form-field">
              <label for="f-message">Message</label>
              <textarea id="f-message" name="message"
                        placeholder="What have you got, roughly how much, and where is it?"></textarea>
            </div>
            <button class="btn btn-primary btn-block btn-lg" type="submit">Send {icon("arrow")}</button>
            <p class="form-hint" id="form-status" role="status" hidden></p>
            <p class="form-hint">Or call
              <a href="tel:{BIZ['phone_href']}" style="font-weight:700;text-decoration:underline">{BIZ['phone_display']}</a>.</p>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return page(slug="contact.html",
                title="Contact FM Recycling | 18 Kitchener St, Orillia — Hours & Directions",
                description="FM Recycling, 18 Kitchener Street, Orillia ON. Yard hours Mon–Fri "
                            "8am–5pm, Sat 8am–12pm. Call (705) 325-8118 or email "
                            "office@fmrecycling.ca.",
                body=body, og_image="media/bins.jpg")


PAGES = {
    "index.html": build_index,
    "prices.html": build_prices,
    "services.html": build_services,
    "about.html": build_about,
    "contact.html": build_contact,
}


def build_sitemap():
    from datetime import date
    today = date.today().isoformat()
    urls = "".join(
        f"\n  <url><loc>{BIZ['origin']}/{'' if s == 'index.html' else s}</loc>"
        f"<lastmod>{today}</lastmod>"
        f"<priority>{'1.0' if s == 'index.html' else '0.8'}</priority></url>" for s in PAGES)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "\n</urlset>\n")


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="6" fill="#0d0d0d"/>
  <g fill="#f0b01d" stroke="#f0b01d" stroke-width="2" stroke-linejoin="round">
    <path d="M32 10 24 24h6v8h4v-8h6z"/>
    <path d="M14 46l8-14 3.5 2-4 7 7 4z" opacity=".95"/>
    <path d="M50 46l-16 0 0-4 9 0-4-7 3.5-2z" opacity=".8"/>
  </g>
</svg>
"""


def main():
    for slug, fn in PAGES.items():
        (ROOT / slug).write_text(fn(), encoding="utf-8")
        print("  wrote", slug)
    (ROOT / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BIZ['origin']}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    print("  wrote sitemap.xml, robots.txt, favicon.svg")


if __name__ == "__main__":
    main()
