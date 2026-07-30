#!/usr/bin/env python3
"""
Muskoka Digital Boost — static site generator.

Emits plain .html files with no runtime dependencies. Run after editing:

    python3 build.py

The output is ordinary static HTML — host it anywhere. This script exists only
so the nav, footer, and business facts live in exactly one place.
"""

import html
import pathlib
import re

ROOT = pathlib.Path(__file__).parent

# ── Business facts — single source of truth ────────────────────────────────
BIZ = {
    "name": "Muskoka Digital Boost",
    "phone_display": "(437) 225-1540",
    "phone_href": "+14372251540",
    "email": "asuter@muskokadigitalboost.ca",
    "city": "Orillia",
    "region": "ON",
    "region_full": "Ontario",
    "country": "CA",
    "origin": "https://muskokadigitalboost.ca",
    "year": 2026,
}

# ── Icons (stroked, 24×24, currentColor) ───────────────────────────────────
I = {
    "monitor": '<path d="M3 4h18v12H3z"/><path d="M8 20h8M12 16v4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "wallet": '<path d="M3 7a2 2 0 0 1 2-2h13a1 1 0 0 1 1 1v2"/><path d="M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2H5a2 2 0 0 1-2-2Z"/><circle cx="16.5" cy="14" r="1.2"/>',
    "bolt": '<path d="M13 2 4.5 13.5H11L10 22l8.5-11.5H12z"/>',
    "cart": '<circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2 3h3l2.5 12.5h11L21 7H6"/>',
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
    "shield": '<path d="M12 3 5 6v6c0 4.2 2.9 7.9 7 9 4.1-1.1 7-4.8 7-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-8 8H4l2-3a8 8 0 1 1 15-5Z"/>',
    "palette": '<path d="M12 3a9 9 0 1 0 0 18 2 2 0 0 0 1.8-2.9c-.5-1 .2-2.1 1.3-2.1H17a4 4 0 0 0 4-4c0-5-4-9-9-9Z"/><circle cx="7.5" cy="11.5" r="1"/><circle cx="12" cy="8" r="1"/><circle cx="16.5" cy="11.5" r="1"/>',
    "rocket": '<path d="M5 15c-1 2.5-1 5-1 5s2.5 0 5-1"/><path d="M9 15 5.5 11.5c3-6 7-8.5 13-8.5 0 6-2.5 10-8.5 13L9 15Z"/><circle cx="14.5" cy="9.5" r="1.6"/>',
    "pin": '<path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
    "phone": '<path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 5 5L15 12l5 2v3a2 2 0 0 1-2.2 2A16 16 0 0 1 4 5.2 2 2 0 0 1 6 3Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    "check": '<path d="m4 12 5 5L20 6"/>',
    "arrow": '<path d="M4 12h15"/><path d="m13 6 6 6-6 6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l3.5 2"/>',
    "key": '<circle cx="8" cy="14" r="4.5"/><path d="m11.5 11.5 8-8M17 4l2.5 2.5M14.5 6.5 17 9"/>',
    "handshake": '<path d="m11 17 2 2 3-3 3 3 2-2-6.5-6.5"/><path d="M3 12.5 8 7.5l3 2 3-3h4l3 3"/><path d="m3 12.5 4 4"/>',
    # industries
    "hammer": '<path d="m14 6 4 4-8.5 8.5a2.8 2.8 0 0 1-4-4L14 6Z"/><path d="m12.5 4.5 5 5 2-2-5-5-2 2Z"/>',
    "utensils": '<path d="M5 3v7a2 2 0 0 0 4 0V3M7 10v11"/><path d="M17 3c-1.5 1.5-2 3-2 5s.7 3 2 3v10"/>',
    "bag": '<path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "tent": '<path d="m12 4 9 16H3l9-16Z"/><path d="M12 4v16"/>',
    "heart": '<path d="M12 20s-7-4.3-7-9.2A4 4 0 0 1 12 8a4 4 0 0 1 7 2.8c0 4.9-7 9.2-7 9.2Z"/>',
    "house": '<path d="m4 11 8-7 8 7"/><path d="M6 10v10h12V10"/><path d="M10 20v-5h4v5"/>',
    "car": '<path d="M4 15h16v-3l-2-5H6l-2 5v3Z"/><circle cx="7.5" cy="17.5" r="1.5"/><circle cx="16.5" cy="17.5" r="1.5"/>',
    "scale": '<path d="M12 4v16M7 20h10"/><path d="m5 8 3.5 6h-7L5 8ZM19 8l3.5 6h-7L19 8ZM5 8l7-2 7 2"/>',
    "leaf": '<path d="M20 4C10 4 4 9 4 16c0 2 1 4 1 4s2-9 15-13Z"/><path d="M5 20c2-6 7-9 12-10"/>',
    "paw": '<circle cx="8" cy="8" r="1.8"/><circle cx="13" cy="6.5" r="1.8"/><circle cx="17" cy="10" r="1.8"/><path d="M12 12c-3 0-5 2-5 4.5S9 20 12 20s5-1 5-3.5S15 12 12 12Z"/>',
    "cap": '<path d="m3 9 9-4 9 4-9 4-9-4Z"/><path d="M7 11v4c0 1.5 2.2 2.5 5 2.5s5-1 5-2.5v-4"/>',
    "sparkle": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9L12 3Z"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (
        f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" focusable="false">{I[name]}</svg>'
    )


def tick(text):
    return f'<li>{icon("check")}<span>{text}</span></li>'


# ── Navigation ─────────────────────────────────────────────────────────────
NAV = [
    ("services.html", "Services"),
    ("pricing.html", "Pricing"),
    ("about.html", "About"),
    ("service-areas.html", "Service Areas"),
    ("faq.html", "FAQ"),
]


def nav(active):
    CURRENT = ' aria-current="page"'
    items = "".join(
        '<li><a href="{}"{}>{}</a></li>'.format(href, CURRENT if href == active else "", label)
        for href, label in NAV
    )
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-nav">
  <div class="nav-inner">
    <a class="brand" href="index.html" aria-label="{BIZ['name']} — home">
      <span class="brand-mark">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.1"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M13 2 4.5 13.5H11L10 22l8.5-11.5H12z"/>
        </svg>
      </span>
      <span class="brand-text">
        <span class="brand-name">Muskoka Digital Boost</span>
        <span class="brand-sub">Web Development</span>
      </span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false"
            aria-controls="nav-links" aria-label="Open menu">
      {icon("menu", "icon-open")}{icon("close", "icon-close")}
    </button>
    <nav id="nav-links" class="nav-links" aria-label="Main">
      <ul style="display:contents">{items}</ul>
      <a class="btn btn-primary nav-cta" href="contact.html">Get a Free Quote</a>
    </nav>
  </div>
</header>"""


# ── Footer ─────────────────────────────────────────────────────────────────
CREDITS = (
    'Photography of Muskoka, Orillia and area courtesy of Wikimedia Commons '
    'contributors — “Muskoka Sunset” by Averi Cummings (CC&nbsp;BY-SA&nbsp;4.0), '
    '“3 Mile Lake” by Bbadgett (CC&nbsp;BY-SA&nbsp;3.0), '
    '“Orillia ON” and “Lake Muskoka” (CC&nbsp;BY-SA&nbsp;3.0).'
)

FOOTER = f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html">
          <span class="brand-mark">
            <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.1"
                 stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M13 2 4.5 13.5H11L10 22l8.5-11.5H12z"/>
            </svg>
          </span>
          <span class="brand-text">
            <span class="brand-name">Muskoka Digital Boost</span>
            <span class="brand-sub">Web Development</span>
          </span>
        </a>
        <p class="footer-about">
          Professional web development for Muskoka and Simcoe County businesses.
          Based in Orillia, Ontario.
        </p>
      </div>

      <div class="footer-col">
        <h2>Services</h2>
        <ul>
          <li><a href="services.html#custom-websites">Custom Websites</a></li>
          <li><a href="services.html#ecommerce">E-Commerce</a></li>
          <li><a href="services.html#landing-pages">Landing Pages</a></li>
          <li><a href="services.html#maintenance">Hosting &amp; Maintenance</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h2>Company</h2>
        <ul>
          <li><a href="about.html">About Us</a></li>
          <li><a href="pricing.html">Pricing</a></li>
          <li><a href="service-areas.html">Service Areas</a></li>
          <li><a href="faq.html">FAQ</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h2>Contact</h2>
        <ul class="footer-contact">
          <li>{icon("phone")}<a href="tel:{BIZ['phone_href']}">{BIZ['phone_display']}</a></li>
          <li>{icon("mail")}<a href="mailto:{BIZ['email']}">{BIZ['email']}</a></li>
          <li>{icon("pin")}<span>Orillia, Ontario</span></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <span>&copy; {BIZ['year']} {BIZ['name']}. All rights reserved.</span>
      <span>Web Development &middot; Muskoka &amp; Simcoe County, Ontario</span>
    </div>
    <p class="footer-credits" style="padding-bottom:26px">{CREDITS}</p>
  </div>
</footer>"""


# ── Page shell ─────────────────────────────────────────────────────────────
def page(*, slug, title, description, body, active=None, og_image="media/muskoka-sunset.jpg", extra_ld=""):
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
<meta name="theme-color" content="#0b1220">

<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="fonts/dm-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/dm-serif-display-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/styles.css">
{extra_ld}
</head>
<body>
{nav(active or slug)}
<main id="main">
{body}
</main>
{FOOTER}
<script src="js/site.js" defer></script>
</body>
</html>
"""


# ── Shared blocks ──────────────────────────────────────────────────────────
def cta_band(heading, sub, primary=("contact.html", "Get a Free Quote"), secondary=None):
    sec = ""
    if secondary:
        sec = f'<a class="btn btn-light btn-lg" href="{secondary[0]}">{secondary[1]}</a>'
    return f"""
<section class="section">
  <div class="container">
    <div class="cta-band reveal">
      <h2 class="serif">{heading}</h2>
      <p>{sub}</p>
      <div class="cta-actions">
        <a class="btn btn-primary btn-lg" href="{primary[0]}">{primary[1]} {icon("arrow")}</a>
        {sec}
      </div>
    </div>
  </div>
</section>"""


SERVICES = [
    {
        "id": "custom-websites", "icon": "monitor", "name": "Custom Builds",
        "blurb": "Fully custom websites designed and built from scratch. Unique, mobile-ready, and optimized for local search.",
        "long": "No templates and no page builders. Every site is designed around what your business actually needs to show and sell, then hand-coded so it loads fast and holds up on every screen size.",
        "ticks": ["Up to 10+ pages", "Mobile responsive", "SEO foundations", "Contact forms"],
        "facts": [("Turnaround", "7–14 business days"), ("Starts at", "$500 + $30/mo"),
                  ("Best for", "Businesses that need a proper site, not a placeholder")],
    },
    {
        "id": "ecommerce", "icon": "cart", "name": "E-Commerce",
        "blurb": "Professional online stores built to sell. Easy for customers to shop, easy for you to manage.",
        "long": "A storefront you can actually run yourself. Products, payments, stock and orders in one dashboard, with a checkout that does not lose people halfway through.",
        "ticks": ["Product catalog", "Secure payments", "Inventory tools", "Admin dashboard"],
        "facts": [("Turnaround", "Quoted per store"), ("Pricing", "Custom quote"),
                  ("Best for", "Retail, boutiques and anyone selling online")],
    },
    {
        "id": "landing-pages", "icon": "target", "name": "Landing Pages",
        "blurb": "Focused, high-converting pages built to turn ad clicks and referrals into leads and customers.",
        "long": "One page, one job. Built for a specific campaign or offer, wired to your analytics, and turned around in three to five days so it is live while the campaign still matters.",
        "ticks": ["Conversion-focused", "Lead capture", "Analytics ready", "3–5 day delivery"],
        "facts": [("Turnaround", "3–5 business days"), ("Pricing", "Quoted per page"),
                  ("Best for", "Ad campaigns, promotions and seasonal offers")],
    },
    {
        "id": "maintenance", "icon": "shield", "name": "Maintenance",
        "blurb": "$30/month covers hosting, backups, updates, security, and support. Zero technical effort on your end.",
        "long": "The part most shops charge extra for. Hosting, daily backups, security monitoring, software updates and small content changes are all included in the monthly fee.",
        "ticks": ["Hosting included", "Daily backups", "Security monitoring", "Content updates"],
        "facts": [("Billing", "$30/month, cancel anytime"), ("Included with", "Every site we build"),
                  ("Best for", "Any site that needs to stay online and current")],
    },
]

PRICING = [
    {
        "name": "Starter", "amount": "500", "note": "+ $30/mo hosting &amp; maintenance",
        "featured": False,
        "ticks": ["Up to 5 pages", "Mobile-responsive design", "Contact form", "Basic SEO setup"],
        "cta": "Get Started",
    },
    {
        "name": "Business", "amount": "1,200", "note": "+ $30/mo hosting &amp; maintenance",
        "featured": True,
        "ticks": ["Up to 10 pages", "Custom design &amp; branding", "Full SEO optimization", "Google Business setup"],
        "cta": "Get Started",
    },
    {
        "name": "E-Commerce", "amount": None, "note": "Based on your store’s needs",
        "featured": False,
        "ticks": ["Full product catalog", "Secure checkout", "Inventory management", "Admin dashboard"],
        "cta": "Get a Quote",
    },
]

INDUSTRIES = [
    ("hammer", "Contractors &amp; Trades"), ("utensils", "Restaurants &amp; Cafés"),
    ("bag", "Retail &amp; Boutiques"), ("tent", "Tourism &amp; Hospitality"),
    ("heart", "Health &amp; Wellness"), ("house", "Real Estate &amp; Rentals"),
    ("car", "Auto &amp; Marine"), ("scale", "Professional Services"),
    ("leaf", "Landscaping &amp; Lawn Care"), ("paw", "Pet Services &amp; Vets"),
    ("cap", "Education &amp; Coaching"), ("sparkle", "Beauty &amp; Salons"),
]

PROCESS = [
    ("chat", "Discovery Call",
     "A quick, no-pressure conversation to understand your business, audience, and what success looks like for your new website. You’ll get a fixed quote within 24 hours."),
    ("palette", "Design &amp; Build",
     "We design and build your site with your feedback at every step. You’ll see progress previews throughout — nothing goes live without your sign-off."),
    ("rocket", "Launch &amp; Support",
     "Your site goes live and we handle every technical detail — hosting, backups, security, updates. We stick around for the long haul."),
]

FAQS = [
    ("How much does a website cost in Muskoka?",
     'Starter websites begin at $500 for up to 5 pages, plus $30/month for hosting and maintenance. '
     'Business websites start at $1,200. E-commerce is custom-quoted. All pricing is transparent — no '
     'surprises. See the <a href="pricing.html">full pricing page</a> for details.'),
    ("How long does it take to build a website?",
     "Most sites are live in 7–14 business days. Landing pages can be done in 3–5 days. Timeline depends "
     "largely on how quickly we receive your content and feedback."),
    ("Do I need to provide content?",
     "We’ll guide you, but having your text and photos ready speeds things up. We can also help with copy "
     "and source professional stock imagery at no extra cost."),
    ("Will my site rank on Google?",
     'Every site includes SEO foundations — proper structure, meta tags, speed optimization, and '
     'mobile-first design. We specifically target local searches across '
     '<a href="service-areas.html">Muskoka and Simcoe County</a>. SEO is a long game, but we set your '
     'site up to win it.'),
    ("What’s included in the $30/month plan?",
     "Hosting, automated backups, security monitoring, software updates, and minor content changes. "
     "Everything to keep your site safe and running without any effort from you."),
    ("Do you work outside Muskoka?",
     "Yes. We specialize in Muskoka and Simcoe County but work with businesses anywhere in Ontario. "
     "Most projects are done remotely."),
    ("Who owns my website and domain?",
     "You do. Your domain is registered in your name, and your website files belong to you. There’s no "
     "lock-in — if you ever leave, we’ll help you move everything."),
    ("Can you redesign my existing website?",
     "Absolutely. Redesigns are a big part of what we do. We’ll modernize the design, improve speed and "
     "SEO, and make sure you don’t lose your existing Google rankings in the process."),
]

AREAS = [
    ("Orillia", "Our home base. We work closely with Orillia businesses and are available for in-person meetings.",
     ["Orillia", "Severn", "Ramara", "Oro-Medonte"]),
    ("Muskoka", "From Bracebridge to Huntsville to Gravenhurst — specialized websites for tourism, trades, and hospitality.",
     ["Bracebridge", "Huntsville", "Gravenhurst", "Port Carling", "Baysville"]),
    ("Barrie &amp; Simcoe County", "Serving businesses across Barrie, Midland, Collingwood, Penetanguishene, and surrounding areas.",
     ["Barrie", "Midland", "Collingwood", "Penetanguishene", "Wasaga Beach"]),
]


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def faq_ld():
    import json
    items = [{
        "@type": "Question",
        "name": html.unescape(strip_tags(q)),
        "acceptedAnswer": {"@type": "Answer", "text": html.unescape(strip_tags(a))},
    } for q, a in FAQS]
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def biz_ld():
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": BIZ["origin"] + "/#business",
        "name": BIZ["name"],
        "description": "Web design and development studio in Orillia, Ontario, building custom "
                       "websites, online stores and landing pages for businesses across Muskoka "
                       "and Simcoe County.",
        "url": BIZ["origin"] + "/",
        "telephone": BIZ["phone_display"],
        "email": BIZ["email"],
        "image": BIZ["origin"] + "/media/muskoka-sunset.jpg",
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": BIZ["city"],
            "addressRegion": BIZ["region"],
            "addressCountry": BIZ["country"],
        },
        "areaServed": [
            {"@type": "City", "name": n} for n in
            ["Orillia", "Bracebridge", "Huntsville", "Gravenhurst", "Barrie",
             "Midland", "Collingwood", "Penetanguishene", "Wasaga Beach"]
        ],
        "knowsAbout": ["Web design", "Web development", "Local SEO", "E-commerce", "Website hosting"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Web development services",
            "itemListElement": [
                {"@type": "Offer",
                 "itemOffered": {"@type": "Service", "name": s["name"], "description": s["blurb"]}}
                for s in SERVICES
            ],
        },
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


# ── Pages ──────────────────────────────────────────────────────────────────
def build_index():
    svc_cards = "".join(f"""
      <article class="card card-hover reveal" data-delay="{i * 70}">
        <div class="card-num">0{i + 1}</div>
        <div class="icon-box">{icon(s['icon'])}</div>
        <h3>{s['name']}</h3>
        <p>{s['blurb']}</p>
        <ul class="ticks">{''.join(tick(t) for t in s['ticks'])}</ul>
      </article>""" for i, s in enumerate(SERVICES))

    features = "".join(f"""
      <div class="feature reveal" data-delay="{i * 70}">
        <div class="icon-box">{icon(ic)}</div>
        <h3>{t}</h3>
        <p>{d}</p>
      </div>""" for i, (ic, t, d) in enumerate([
        ("monitor", "Custom-Built Websites", "No templates. Every site is designed and coded to match your brand and goals."),
        ("search", "Built for Local SEO", "Every site includes SEO foundations to help your Muskoka business rank on Google."),
        ("wallet", "Affordable &amp; Transparent", "Starting at $500 with $30/month hosting. Honest pricing, no hidden fees."),
        ("bolt", "Fast 7–14 Day Delivery", "Most websites launch within two weeks — without cutting corners on quality."),
    ]))

    steps = "".join(f"""
      <div class="step reveal" data-delay="{i * 80}">
        <h3>{t}</h3>
        <p>{d}</p>
      </div>""" for i, (_, t, d) in enumerate(PROCESS))

    prices = "".join(f"""
      <article class="card price-card{' featured' if p['featured'] else ''} reveal" data-delay="{i * 80}">
        {'<span class="price-badge">Most Popular</span>' if p['featured'] else ''}
        <div class="price-name">{p['name']}</div>
        <div class="price-amount">{'<span class="cur">$</span>' + p['amount'] if p['amount'] else 'Custom'}</div>
        <p class="price-note">{p['note']}</p>
        <ul class="ticks">{''.join(tick(t) for t in p['ticks'])}</ul>
        <a class="btn {'btn-primary' if p['featured'] else 'btn-ghost'} btn-block" href="contact.html">{p['cta']}</a>
      </article>""" for i, p in enumerate(PRICING))

    inds = "".join(
        f'<div class="industry">{icon(ic)}<span>{n}</span></div>' for ic, n in INDUSTRIES)

    areas = "".join(f"""
      <article class="card card-hover area-card reveal" data-delay="{i * 70}">
        <h3>{icon("pin")}{n}</h3>
        <p>{d}</p>
        <ul class="area-list">{''.join(f'<li>{x}</li>' for x in places)}</ul>
      </article>""" for i, (n, d, places) in enumerate(AREAS))

    faq_preview = "".join(f"""
      <details class="faq-item"{' open' if i == 0 else ''}>
        <summary>{q}</summary>
        <div class="faq-answer"><p>{a}</p></div>
      </details>""" for i, (q, a) in enumerate(FAQS[:3]))

    body = f"""
<section class="hero">
  <img class="hero-bg" src="media/muskoka-sunset.jpg" alt="" width="1920" height="1280" fetchpriority="high" decoding="async">
  <div class="hero-inner">
    <div class="hero-copy">
      <span class="hero-badge"><span class="dot"></span> Muskoka &middot; Simcoe County &middot; Orillia</span>
      <h1 class="serif">Professional websites for <em>Muskoka businesses</em></h1>
      <p class="hero-sub">
        Custom-built, fast, and designed to rank in local search. Helping Muskoka
        and Simcoe County businesses grow online.
      </p>
      <div class="hero-actions">
        <a class="btn btn-primary btn-lg" href="contact.html">Get a Free Quote {icon("arrow")}</a>
        <a class="btn btn-light btn-lg" href="services.html">Our Services</a>
      </div>
      <div class="hero-stats">
        <div class="hero-stat">
          <div class="num" data-countup>$500</div>
          <div class="label">Starting price</div>
        </div>
        <div class="hero-stat">
          <div class="num">7–14</div>
          <div class="label">Day delivery</div>
        </div>
        <div class="hero-stat">
          <div class="num">Orillia</div>
          <div class="label">Based &amp; local</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section-white" aria-labelledby="why-heading">
  <div class="container">
    <h2 id="why-heading" class="visually-hidden">Why work with us</h2>
    <div class="feature-row">{features}</div>
  </div>
</section>

<section class="section" id="services">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Services</span>
      <h2 class="serif">Web development services for local businesses</h2>
      <p>Everything your Muskoka or Simcoe County business needs to get online and grow.</p>
    </div>
    <div class="grid grid-4">{svc_cards}</div>
    <p style="margin-top:34px">
      <a class="link-arrow" href="services.html">Explore all services {icon("arrow")}</a>
    </p>
  </div>
</section>

<section class="section section-white">
  <div class="container">
    <div class="stat-band reveal">
      <div class="stat"><div class="num" data-countup>$500</div><div class="label">Starting price</div></div>
      <div class="stat"><div class="num" data-countup>14</div><div class="label">Days to launch, typically</div></div>
      <div class="stat"><div class="num" data-countup>$30</div><div class="label">Monthly hosting &amp; care</div></div>
      <div class="stat"><div class="num" data-countup>100%</div><div class="label">Yours — files and domain</div></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center reveal">
      <span class="eyebrow">Process</span>
      <h2 class="serif">How we work together</h2>
      <p>Three steps, clear communication, and no surprises along the way.</p>
    </div>
    <div class="steps">{steps}</div>
    <p style="margin-top:34px;text-align:center">
      <a class="link-arrow" href="about.html">More about how we work {icon("arrow")}</a>
    </p>
  </div>
</section>

<section class="section section-tint" id="pricing">
  <div class="container">
    <div class="section-head center reveal">
      <span class="eyebrow">Pricing</span>
      <h2 class="serif">Clear, honest pricing</h2>
      <p>No surprises. No hidden costs. Just straightforward pricing in CAD.</p>
    </div>
    <div class="price-grid">{prices}</div>
    <p style="margin-top:34px;text-align:center">
      <a class="link-arrow" href="pricing.html">See full pricing details {icon("arrow")}</a>
    </p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Industries we serve</span>
      <h2 class="serif">We build websites for every kind of local business</h2>
    </div>
    <div class="industry-grid reveal">{inds}</div>
  </div>
</section>

<section class="section section-white">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Service area</span>
      <h2 class="serif">Web design across Muskoka &amp; Simcoe County</h2>
      <p>Based in Orillia, Ontario — wherever you’re located, we’ve got you covered.</p>
    </div>
    <div class="grid grid-3">{areas}</div>
    <p style="margin-top:34px">
      <a class="link-arrow" href="service-areas.html">View all service areas {icon("arrow")}</a>
    </p>
  </div>
</section>

<section class="section">
  <div class="container-narrow">
    <div class="section-head center reveal">
      <span class="eyebrow">FAQ</span>
      <h2 class="serif">Common questions</h2>
    </div>
    <div class="faq-list reveal">{faq_preview}</div>
    <p style="margin-top:30px;text-align:center">
      <a class="link-arrow" href="faq.html">Read all FAQs {icon("arrow")}</a>
    </p>
  </div>
</section>

{cta_band("Let’s build something great",
          "Free, no-obligation quote. We reply within 24 hours.",
          secondary=(f"tel:{BIZ['phone_href']}", f"Call {BIZ['phone_display']}"))}
"""
    return page(
        slug="index.html", active="index.html",
        title="Muskoka Digital Boost | Web Design & Development in Muskoka, Orillia & Simcoe County",
        description="Custom websites for Muskoka and Simcoe County businesses. Built fast, "
                    "designed to rank locally, from $500 plus $30/month. Based in Orillia, Ontario.",
        body=body, extra_ld=biz_ld(),
    )


def build_services():
    blocks = "".join(f"""
<section class="section {'section-white' if i % 2 else ''}" id="{s['id']}">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">0{i + 1} &middot; {s['name']}</span>
        <h2 class="serif" style="font-size:clamp(1.7rem,3.4vw,2.4rem);margin-bottom:16px">{s['name']}</h2>
        <p class="lead" style="margin-bottom:18px">{s['blurb']}</p>
        <p style="color:var(--gray-600)">{s['long']}</p>
        <ul class="ticks" style="margin-top:22px">{''.join(tick(t) for t in s['ticks'])}</ul>
        <p style="margin-top:26px">
          <a class="btn btn-primary" href="contact.html">Get a quote for this {icon("arrow")}</a>
        </p>
      </div>
      <div class="reveal" data-delay="90">
        <div class="card" style="padding:34px;background:linear-gradient(150deg,var(--blue-50),#fff)">
          <div class="icon-box" style="width:62px;height:62px;border-radius:16px">{icon(s['icon'])}</div>
          <dl class="fact-list">{''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in s['facts'])}</dl>
        </div>
      </div>
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
    <h1 class="serif">Web development services for local businesses</h1>
    <p>Everything your Muskoka or Simcoe County business needs to get online and grow —
       built custom, launched fast, and looked after once it’s live.</p>
  </div>
</section>
{blocks}
{cta_band("Not sure which one you need?",
          "Tell us what your business does and we’ll tell you honestly — even if the answer is “less than you think”.")}
"""
    return page(
        slug="services.html",
        title="Web Development Services | Custom Sites, E-Commerce & Landing Pages | Muskoka Digital Boost",
        description="Custom websites, online stores, landing pages, and $30/month hosting and "
                    "maintenance for businesses in Muskoka, Orillia and Simcoe County.",
        body=body,
    )


def build_pricing():
    prices = "".join(f"""
      <article class="card price-card{' featured' if p['featured'] else ''} reveal" data-delay="{i * 80}">
        {'<span class="price-badge">Most Popular</span>' if p['featured'] else ''}
        <div class="price-name">{p['name']}</div>
        <div class="price-amount">{'<span class="cur">$</span>' + p['amount'] if p['amount'] else 'Custom'}</div>
        <p class="price-note">{p['note']}</p>
        <ul class="ticks">{''.join(tick(t) for t in p['ticks'])}</ul>
        <a class="btn {'btn-primary' if p['featured'] else 'btn-ghost'} btn-block" href="contact.html">{p['cta']}</a>
      </article>""" for i, p in enumerate(PRICING))

    included = "".join(f"""
      <div class="feature reveal" data-delay="{i * 60}">
        <div class="icon-box">{icon(ic)}</div>
        <h3>{t}</h3>
        <p>{d}</p>
      </div>""" for i, (ic, t, d) in enumerate([
        ("shield", "Hosting &amp; backups", "Included in the $30/month. Daily backups, security monitoring, and software updates."),
        ("key", "You own everything", "Your domain is registered in your name and the site files are yours. No lock-in, ever."),
        ("search", "SEO foundations", "Clean structure, meta tags, fast loading, and mobile-first — on every plan."),
        ("handshake", "Fixed quotes", "The number we give you is the number you pay. Extra work is quoted before it starts."),
    ]))

    faq_items = "".join(f"""
      <details class="faq-item">
        <summary>{q}</summary>
        <div class="faq-answer"><p>{a}</p></div>
      </details>""" for q, a in [FAQS[0], FAQS[4], FAQS[1]])

    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">Pricing</span>
    </nav>
    <h1 class="serif">Clear, honest pricing</h1>
    <p>No surprises, no hidden costs, no retainers you can’t get out of.
       Every price below is in Canadian dollars.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="price-grid">{prices}</div>
    <p style="margin-top:30px;color:var(--gray-500);font-size:.92rem;max-width:640px">
      Prices are a starting point, not a ceiling you’ll be pushed toward. If your project
      needs more than a plan covers, we quote the difference up front — before any work starts.
    </p>
  </div>
</section>

<section class="section section-white">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Included on every plan</span>
      <h2 class="serif">What you get regardless of price</h2>
    </div>
    <div class="feature-row">{included}</div>
  </div>
</section>

<section class="section">
  <div class="container-narrow">
    <div class="section-head center reveal">
      <span class="eyebrow">Pricing questions</span>
      <h2 class="serif">Before you ask</h2>
    </div>
    <div class="faq-list reveal">{faq_items}</div>
    <p style="margin-top:30px;text-align:center">
      <a class="link-arrow" href="faq.html">Read all FAQs {icon("arrow")}</a>
    </p>
  </div>
</section>

{cta_band("Get a fixed quote in 24 hours",
          "Tell us what you need. We’ll send back a number you can actually plan around.")}
"""
    return page(
        slug="pricing.html",
        title="Website Pricing | From $500 + $30/month | Muskoka Digital Boost",
        description="Transparent website pricing for Muskoka and Simcoe County businesses. "
                    "Starter from $500, Business from $1,200, e-commerce custom-quoted. "
                    "$30/month hosting and maintenance.",
        body=body,
    )


def build_about():
    steps = "".join(f"""
      <div class="step reveal" data-delay="{i * 80}">
        <h3>{t}</h3>
        <p>{d}</p>
      </div>""" for i, (_, t, d) in enumerate(PROCESS))

    values = "".join(f"""
      <div class="feature reveal" data-delay="{i * 60}">
        <div class="icon-box">{icon(ic)}</div>
        <h3>{t}</h3>
        <p>{d}</p>
      </div>""" for i, (ic, t, d) in enumerate([
        ("handshake", "Straight talk",
         "Fixed quotes, plain English, and honest advice — even when the honest advice is “you don’t need that”."),
        ("bolt", "Fast turnaround",
         "Most websites launch in 7–14 days. Your business shouldn’t wait months to get online."),
        ("pin", "Genuinely local",
         'Based in Orillia, serving <a href="service-areas.html" style="color:var(--blue-600);font-weight:600">Muskoka &amp; Simcoe County</a>. In-person meetings available.'),
        ("key", "You own everything",
         "Your domain, your content, your website files. No lock-in, no hostage-taking, ever."),
    ]))

    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">About</span>
    </nav>
    <h1 class="serif">A local studio that treats your business like its own</h1>
    <p>Muskoka Digital Boost is a web design and development studio based in Orillia,
       Ontario — built to give local businesses big-agency quality without big-agency prices.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">Our story</span>
        <h2 class="serif" style="font-size:clamp(1.8rem,3.6vw,2.5rem);margin-bottom:20px">Why we started</h2>
        <p style="color:var(--gray-600);margin-bottom:16px">
          Too many great local businesses across Muskoka and Simcoe County are stuck with
          outdated websites, overpriced agency retainers, or no website at all. Meanwhile,
          their customers are searching Google every day — and finding competitors instead.
        </p>
        <p style="color:var(--gray-600);margin-bottom:16px">
          We started Muskoka Digital Boost to fix that. Our belief is simple: a professional,
          fast, search-optimized website shouldn’t cost $10,000 or take three months. It should
          be affordable, quick to launch, and built by someone who actually picks up the phone
          when you call.
        </p>
        <p style="color:var(--gray-600)">
          Because we’re local, we understand the seasonal rhythms of cottage country, the trades
          that keep this region running, and the tourism traffic that peaks every summer. That
          context shows up in every site we build — from the keywords we target to the way we
          structure your <a href="services.html" style="color:var(--blue-600);font-weight:600">services pages</a>.
        </p>
      </div>
      <figure class="split-media reveal" data-delay="90">
        <img src="media/orillia-waterfront.jpg" width="1400" height="852" loading="lazy" decoding="async"
             alt="Boats moored at the docks in Couchiching Beach Park, Orillia, with the waterfront gazebo and Lake Couchiching behind them">
        <figcaption>Orillia waterfront — our home base.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="section section-white">
  <div class="container">
    <div class="section-head center reveal">
      <span class="eyebrow">Process</span>
      <h2 class="serif">How we work together</h2>
      <p>Three steps, clear communication, and no surprises along the way.</p>
    </div>
    <div class="steps">{steps}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">What we stand for</span>
      <h2 class="serif">The way we do business</h2>
    </div>
    <div class="feature-row">{values}</div>
  </div>
</section>

{cta_band("Let’s talk about your project",
          "A quick call costs nothing and you’ll leave with clear next steps — whether you work with us or not.",
          secondary=("services.html", "Browse Our Services"))}
"""
    return page(
        slug="about.html",
        title="About Us | Local Web Designers in Orillia, Ontario | Muskoka Digital Boost",
        description="Muskoka Digital Boost is a web design studio in Orillia, Ontario, giving "
                    "local businesses big-agency quality without big-agency prices.",
        body=body, og_image="media/orillia-waterfront.jpg",
    )


def build_areas():
    cards = "".join(f"""
      <article class="card card-hover area-card reveal" data-delay="{i * 70}">
        <h3>{icon("pin")}{n}</h3>
        <p>{d}</p>
        <ul class="area-list">{''.join(f'<li>{x}</li>' for x in places)}</ul>
      </article>""" for i, (n, d, places) in enumerate(AREAS))

    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">Service Areas</span>
    </nav>
    <h1 class="serif">Web design across Muskoka &amp; Simcoe County</h1>
    <p>Based in Orillia, Ontario. We work in person across the region and remotely
       anywhere in the province.</p>
  </div>
</section>

<section class="section" aria-labelledby="areas-heading">
  <div class="container">
    <h2 id="areas-heading" class="visually-hidden">Areas we serve</h2>
    <div class="grid grid-3">{cards}</div>
  </div>
</section>

<section class="section section-white">
  <div class="container">
    <div class="split">
      <figure class="split-media reveal">
        <img src="media/muskoka-autumn-dock.jpg" width="1024" height="702" loading="lazy" decoding="async"
             alt="A wooden dock reaching into a calm Muskoka lake, framed by maple trees in autumn colour">
        <figcaption>3 Mile Lake, Muskoka.</figcaption>
      </figure>
      <div class="reveal" data-delay="90">
        <span class="eyebrow">Why local matters</span>
        <h2 class="serif" style="font-size:clamp(1.7rem,3.4vw,2.4rem);margin-bottom:18px">
          We know how this region actually works
        </h2>
        <p style="color:var(--gray-600);margin-bottom:16px">
          A cottage-country restaurant and a year-round contractor need completely different
          websites. One lives or dies on a six-week summer window and Google Maps; the other
          needs to show up when someone searches for an emergency repair in February.
        </p>
        <p style="color:var(--gray-600)">
          Building here means we already know the seasonal patterns, the towns people
          actually search for, and which competitors you’re up against on page one.
        </p>
        <ul class="ticks" style="margin-top:22px">
          {tick("Local keyword targeting by town, not just “Ontario”")}
          {tick("Google Business Profile setup and optimization")}
          {tick("In-person meetings across Orillia and Muskoka")}
          {tick("Remote work anywhere in Ontario")}
        </ul>
      </div>
    </div>
  </div>
</section>

{cta_band("Not sure if you’re in our area?",
          "If you’re in Ontario, you are. Most projects run entirely remotely — give us a call.",
          secondary=(f"tel:{BIZ['phone_href']}", f"Call {BIZ['phone_display']}"))}
"""
    return page(
        slug="service-areas.html",
        title="Service Areas | Web Design in Orillia, Muskoka, Barrie & Simcoe County",
        description="Web design and development across Orillia, Bracebridge, Huntsville, "
                    "Gravenhurst, Barrie, Midland, Collingwood and all of Simcoe County.",
        body=body, og_image="media/muskoka-autumn-dock.jpg",
    )


def build_faq():
    items = "".join(f"""
      <details class="faq-item"{' open' if i == 0 else ''}>
        <summary>{q}</summary>
        <div class="faq-answer"><p>{a}</p></div>
      </details>""" for i, (q, a) in enumerate(FAQS))

    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">FAQ</span>
    </nav>
    <h1 class="serif">Frequently asked questions</h1>
    <p>Everything you might want to know about cost, timelines, SEO, hosting, and
       how we work — before you even pick up the phone.</p>
  </div>
</section>

<section class="section">
  <div class="container-narrow">
    <div class="faq-list">{items}</div>
  </div>
</section>

{cta_band("Still have a question?",
          "Ask us directly — we reply within 24 hours, and there’s never any pressure.",
          primary=("contact.html", "Get in Touch"),
          secondary=(f"tel:{BIZ['phone_href']}", f"Call {BIZ['phone_display']}"))}
"""
    return page(
        slug="faq.html",
        title="Frequently Asked Questions | Website Costs, Timelines & SEO | Muskoka Digital Boost",
        description="Answers on website cost, build timelines, SEO, hosting, content and "
                    "ownership for Muskoka and Simcoe County businesses.",
        body=body, extra_ld=faq_ld(),
    )


def build_contact():
    body = f"""
<section class="page-head">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="index.html">Home</a> <span aria-hidden="true">/</span>
      <span aria-current="page">Contact</span>
    </nav>
    <h1 class="serif">Get a free quote</h1>
    <p>Tell us what your business does and what you need. We reply within 24 hours
       with a fixed price — no obligation, no sales pressure.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="contact-grid">
      <div class="reveal">
        <h2 class="serif" style="font-size:clamp(1.6rem,3.2vw,2.1rem);margin-bottom:22px">
          Reach us directly
        </h2>
        <div class="grid" style="gap:14px;margin-bottom:30px">
          <a class="contact-method" href="tel:{BIZ['phone_href']}">
            <span class="icon-box">{icon("phone")}</span>
            <span>
              <span class="label">Phone</span>
              <span class="value">{BIZ['phone_display']}</span>
              <span class="meta">Mon–Fri, 9am–6pm ET</span>
            </span>
          </a>
          <a class="contact-method" href="mailto:{BIZ['email']}">
            <span class="icon-box">{icon("mail")}</span>
            <span>
              <span class="label">Email</span>
              <span class="value">{BIZ['email']}</span>
              <span class="meta">We reply within 24 hours</span>
            </span>
          </a>
          <div class="contact-method">
            <span class="icon-box">{icon("pin")}</span>
            <span>
              <span class="label">Based in</span>
              <span class="value">Orillia, Ontario</span>
              <span class="meta">Serving Muskoka &amp; Simcoe County</span>
            </span>
          </div>
        </div>

        <figure class="split-media">
          <img src="media/lake-muskoka.jpg" width="1400" height="1050" loading="lazy" decoding="async"
               alt="Open water on Lake Muskoka on a clear day, with a treed shoreline in the distance"
               style="aspect-ratio:16/10">
        </figure>
      </div>

      <div class="card reveal" data-delay="90" style="padding:clamp(26px,4vw,38px)">
        <h2 class="serif" style="font-size:1.5rem;margin-bottom:8px">Request a quote</h2>
        <p style="color:var(--gray-600);font-size:.94rem;margin-bottom:26px">
          Fields marked <span style="color:var(--blue-600)">*</span> are required.
        </p>

        <form id="quote-form" novalidate>
          <div class="form-field">
            <label for="f-name">Your name <span class="req">*</span></label>
            <input id="f-name" name="name" type="text" required autocomplete="name">
          </div>
          <div class="form-field">
            <label for="f-business">Business name</label>
            <input id="f-business" name="business" type="text" autocomplete="organization">
          </div>
          <div class="form-field">
            <label for="f-email">Email <span class="req">*</span></label>
            <input id="f-email" name="email" type="email" required autocomplete="email">
          </div>
          <div class="form-field">
            <label for="f-phone">Phone</label>
            <input id="f-phone" name="phone" type="tel" autocomplete="tel">
          </div>
          <div class="form-field">
            <label for="f-project">What do you need?</label>
            <select id="f-project" name="project">
              <option>New website</option>
              <option>Website redesign</option>
              <option>Online store</option>
              <option>Landing page</option>
              <option>Hosting &amp; maintenance only</option>
              <option>Not sure yet</option>
            </select>
          </div>
          <div class="form-field">
            <label for="f-budget">Rough budget</label>
            <select id="f-budget" name="budget">
              <option>Around $500</option>
              <option>$500 – $1,200</option>
              <option>$1,200+</option>
              <option>Not sure yet</option>
            </select>
          </div>
          <div class="form-field">
            <label for="f-details">Tell us about the project</label>
            <textarea id="f-details" name="details"
                      placeholder="What does your business do, and what do you want the site to achieve?"></textarea>
          </div>
          <button class="btn btn-primary btn-block btn-lg" type="submit">
            Send request {icon("arrow")}
          </button>
          <p class="form-hint" id="form-status" role="status" hidden></p>
          <p class="form-hint">
            Prefer to talk? Call <a href="tel:{BIZ['phone_href']}"
            style="color:var(--blue-600);font-weight:600">{BIZ['phone_display']}</a>.
          </p>
        </form>
      </div>
    </div>
  </div>
</section>
"""
    return page(
        slug="contact.html",
        title="Contact | Get a Free Website Quote | Muskoka Digital Boost",
        description="Get a free, no-obligation website quote for your Muskoka or Simcoe County "
                    "business. Call (437) 225-1540 or email asuter@muskokadigitalboost.ca.",
        body=body, og_image="media/lake-muskoka.jpg",
    )


PAGES = {
    "index.html": build_index,
    "services.html": build_services,
    "pricing.html": build_pricing,
    "about.html": build_about,
    "service-areas.html": build_areas,
    "faq.html": build_faq,
    "contact.html": build_contact,
}


def build_sitemap():
    from datetime import date
    today = date.today().isoformat()
    urls = "".join(
        f"\n  <url><loc>{BIZ['origin']}/{'' if s == 'index.html' else s}</loc>"
        f"<lastmod>{today}</lastmod>"
        f"<priority>{'1.0' if s == 'index.html' else '0.8'}</priority></url>"
        for s in PAGES
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{urls}\n</urlset>\n")


def main():
    for slug, fn in PAGES.items():
        (ROOT / slug).write_text(fn(), encoding="utf-8")
        print("  wrote", slug)

    (ROOT / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BIZ['origin']}/sitemap.xml\n", encoding="utf-8")
    print("  wrote sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
