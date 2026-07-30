# fmrecycling.ca — rebuild

Static rebuild of the FM Recycling website (Orillia, Ontario). Five pages, no
framework, no build step needed to host. Copy and positioning are carried over
from their existing Wix site; the hero leads harder on posted prices and
same-day cash.

## Running it

```bash
python3 -m http.server 8000
```

Fonts are self-hosted; the `crossorigin` preloads want HTTP rather than
`file://`, so use the server when checking your work.

## Editing

Content lives in **`build.py`**, not in the `.html` files. The HTML is
generated — edits made to it directly are lost on the next build.

```bash
python3 build.py     # regenerates all 5 pages + sitemap.xml + robots.txt + favicon.svg
```

| What | Where in `build.py` |
|---|---|
| Phone, email, address, coordinates | `BIZ` |
| **Scrap prices** | `PRICE_TABLES` |
| Date shown as "last updated" | `PRICES_UPDATED` |
| Yard hours | `HOURS` (and `HOURS` in `js/site.js` — see below) |
| What's turned away at the gate | `NOT_ACCEPTED` |
| Services and their copy | `SERVICES` |

### Updating prices

This is the page people actually come for. Edit `PRICE_TABLES`, bump
`PRICES_UPDATED`, run `python3 build.py`, commit. One edit updates the prices
page, the home page category counts, and the "last updated" stamp together.

### ⚠️ Hours are defined in two places

`HOURS` in `build.py` renders the visible tables. `HOURS` in `js/site.js` drives
the live "Open now / Closed" indicator in the top bar. **Change both**, or the
badge will contradict the table. The JS copy also holds `CLOSURES` — a list of
specific dates the yard is shut:

```js
var CLOSURES = ['2026-07-31', '2026-08-01', '2026-08-03'];  // Civic Holiday weekend
```

Those three dates are from the closure notice on their current site. **Remove
them once that weekend has passed**, and add new dates for future holidays.
A stale closure date will wrongly tell people you're shut.

## Deploying

Upload the folder. Netlify, Vercel, Cloudflare Pages, GitHub Pages or plain
shared hosting all work — there is nothing to compile.

Not needed on the server: `build.py`, `brand.md`, `README.md`,
`media-index.json`. Harmless if uploaded, just unnecessary.

## What changed from the Wix site

**Content and correctness**

- All four price tables transcribed and laid out as real `<table>` elements with
  proper headers, so they're readable by screen readers and parseable by search
  engines. On the Wix site each table is two unlinked text boxes sitting side by
  side — visually a table, structurally not one.
- Their price disclaimer and "updated" date are kept and made prominent.
- The "we do not accept propane tanks / fuel tanks / fire extinguishers" notice
  appears on the home page, the prices page and the contact page rather than
  once in a banner.

**New**

- A live **Open now / Closed** indicator in the top bar, computed in the yard's
  own timezone (`America/Toronto`) — so someone checking from Alberta still gets
  Orillia's answer. It's progressive enhancement: the full hours are in the HTML
  regardless.
- Google Maps embed and a `RecyclingCenter` schema.org block with real opening
  hours, coordinates and service area. Local SEO depends on this and the Wix
  site had none of it.

**Design and technical**

- Brand palette taken from the logo itself — black and `#f0b01d`. Barlow
  Condensed for headings to echo the logo's compressed wordmark.
- Fonts self-hosted (~86 KB): no third-party request, nothing sent to Google.
- **Three of their photos were being served rotated** — two upside-down, one on
  its side — because the EXIF orientation flag was never applied. Corrected.
- The logo dropped from 142 KB to 8 KB by palette-quantising the flat artwork.
- ~381 KB first load. Every image below the fold is lazy-loaded with explicit
  dimensions so nothing shifts as it loads.

**Verified:** all internal links and anchors resolve, every image has
descriptive alt text, heading hierarchy is clean across all 5 pages, and all
sampled text meets WCAG AA contrast — including text over the hero photo.
Checked with JS enabled and disabled; nothing is hidden or wrong in either.

## Known gaps — worth your attention

1. **Spot-check the Ferrous and Aluminium price rows before this goes live.**
   Their site stores each table as two independent text columns with no row
   structure joining a material to a price, so alignment had to be reconstructed
   from document order. Copper/Brass and Stainless paired unambiguously.
   Ferrous and Aluminium each contain lines where two values share one
   paragraph, so those two are the ones to eyeball. See `brand.md`.
2. **The contact form has no backend.** It composes a prefilled `mailto:` as a
   fallback. Wire it to Formspree or Netlify Forms and swap the handler at the
   bottom of `js/site.js`.
3. **No reviews or testimonials.** None are published anywhere reachable, so
   none were invented. If FM has a Google Business Profile with ratings, that's
   the single highest-value addition to this site.
4. **The long-weekend closure dates are hardcoded and will expire.** See the
   warning above.
5. **"Since 2000"** appears on the about page and bin services — that's their own
   claim from their bin services copy. Confirm it applies to the business as a
   whole before leaning on it harder.

## Files

```
index.html prices.html services.html      generated — edit build.py instead
about.html contact.html
sitemap.xml robots.txt favicon.svg

build.py            generator + all site content and prices
brand.md            palette, type, voice, and the pricing caveat in full
css/styles.css      single stylesheet
js/site.js          nav, reveal, open/closed badge, form — all enhancement only
fonts/              self-hosted Barlow + Barlow Condensed (latin subset)
media/              FM Recycling's own photography, EXIF-corrected
media-index.json    what each image is, where it came from, where it's used
```
