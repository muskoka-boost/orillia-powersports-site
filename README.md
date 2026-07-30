# muskokadigitalboost.ca — rebuild

Static rebuild of the Muskoka Digital Boost website. Seven pages, no framework,
no build step required to host. Positioning and copy are carried over from the
existing site unchanged; this is a design and engineering rebuild.

## Running it

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
```

Fonts are self-hosted and load over `file://` fine, but a couple of things
(`crossorigin` font preloads) behave properly only over HTTP — use the server
when checking your work.

## Editing

Page content lives in **`build.py`**, not in the `.html` files. The HTML is
generated; edits made directly to it are lost on the next build.

```bash
python3 build.py     # regenerates all 7 pages + sitemap.xml + robots.txt
```

Everything worth changing is near the top of that file:

| What | Where |
|---|---|
| Phone, email, city, domain | `BIZ` dict |
| Services and their copy | `SERVICES` |
| Plans and prices | `PRICING` |
| FAQ questions and answers | `FAQS` (also feeds the FAQ schema) |
| Service areas and town lists | `AREAS` |
| Industry list | `INDUSTRIES` |
| Nav order | `NAV` |

Changing a price in `PRICING` updates the home page, the pricing page, and the
structured data in one edit. That was the point of the generator — the old site
had prices hard-coded in several files.

## Deploying

Upload the whole folder. Netlify, Vercel, Cloudflare Pages, GitHub Pages, or
plain shared hosting all work — there is nothing to compile.

Excluded from a deploy: `build.py`, `brand.md`, `README.md`, `media-index.json`.
They are harmless if uploaded, just unnecessary.

## What changed from the old site

**Bugs fixed**

- **Stat counters shipped as zeros.** The old markup literally contained
  `0% Client Satisfaction` and `$0 Starting Price`; JavaScript animated them up
  to their real values on scroll. Anyone with blocked or slow JS — and every
  crawler that does not execute it — saw a site claiming zero percent client
  satisfaction. Real values are now in the HTML and the count-up only animates
  toward what is already there.
- Scroll animations are additive. Content is visible by default and the hidden
  state is only applied once JS has confirmed it can undo it, with a 3-second
  failsafe. A JS error can no longer blank out the page.

**Design**

- Real photography — the old site had no images at all.
- Emoji icons (🖥️ 🔍 💰 ⚡ 🏗️ 🍽️) replaced with inline SVG. Emoji render
  differently on every platform and undercut a design studio's own site.
- Fonts self-hosted rather than pulled from Google Fonts: one less third-party
  connection on first paint, and no visitor data sent to Google.
- Full mobile nav, focus-visible states, skip link, `prefers-reduced-motion`
  support throughout.

**SEO / technical**

- `schema.org` `ProfessionalService` on the home page, `FAQPage` on the FAQ.
- Open Graph and Twitter card tags with real images.
- `sitemap.xml` and `robots.txt`, generated.
- Canonical URLs, per-page titles and descriptions.
- All seven original URLs preserved, so existing rankings carry over.
- ~319 KB first load; every image lazy-loaded below the fold with explicit
  dimensions to prevent layout shift.

**Verified:** all internal links and anchors resolve, every image has
descriptive alt text, heading hierarchy is clean on all 7 pages, and all
sampled text meets WCAG AA contrast. Checked with JS enabled, JS disabled,
and `prefers-reduced-motion: reduce`.

## Known gaps — worth your attention

1. **The contact form has no backend.** It composes a prefilled `mailto:` as a
   fallback, which works but is not great — it depends on the visitor having a
   mail client configured. Wire it to Formspree, Netlify Forms, or similar and
   replace the handler at the bottom of `js/site.js`. This is the single most
   valuable thing to fix.
2. **No portfolio.** For a web design studio this is the biggest credibility
   gap. Nobody hires a designer without seeing their work. Send over 3–6 client
   sites and a `work.html` becomes the strongest page here.
3. **No testimonials.** The business has no published reviews, so rather than
   invent any, the design earns trust structurally — transparent pricing, a
   stated process, and an explicit "what's included" block. Collect a few real
   reviews and there is an obvious slot for them on the home page.
4. **"100% — yours, files and domain"** replaced the old "100% Client
   Satisfaction" stat. The original claim was unverifiable with no reviews
   published; ownership is a real promise already made on the About page. Change
   it back in `build_index()` if you disagree.
5. **Business hours** on the contact page (`Mon–Fri, 9am–6pm ET`) were not on
   the old site — I inferred them. Correct them in `build_contact()` if wrong.

## Photography

Four Wikimedia Commons photographs of the actual service area, credited in the
footer as their CC BY-SA licences require. **Keep that credit line if you keep
the photos.** Swap in your own work and you can delete it — see
`media-index.json` for what each file is and where it is used.

## Files

```
index.html services.html pricing.html      generated — edit build.py instead
about.html service-areas.html faq.html
contact.html sitemap.xml robots.txt

build.py            generator + all site content
brand.md            design rationale: palette, type, voice, what was excluded
css/styles.css      single stylesheet
js/site.js          nav, scroll reveal, count-up, form — all enhancement only
fonts/              self-hosted DM Sans (variable) + DM Serif Display
media/              photography
media-index.json    image sources, licences, and where each is used
```
