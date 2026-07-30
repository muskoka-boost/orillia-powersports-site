# Muskoka Digital Boost — Brand Spec

Derived from the existing muskokadigitalboost.ca (Nov 2025 crawl) plus regional
imagery. Positioning and copy are **unchanged** per client direction — this is a
design and engineering rebuild, not a repositioning.

## Voice

Plain-spoken, confident, anti-agency. Short declarative sentences. Prices stated
out loud. The existing About page line — *"built by someone who actually picks up
the phone when you call"* — is the truest sentence on the site and sets the tone
for everything else.

Never: "solutions", "leverage", "elevate your digital presence", "in today's
fast-paced world".

## Palette

Carried over from the original stylesheet, with two additions.

| Token | Hex | Use |
|---|---|---|
| `--navy` | `#0b1220` | Hero background, footer |
| `--ink` | `#0f172a` | Headings, body on light |
| `--blue-700` | `#1d4ed8` | Button hover, links on light |
| `--blue-600` | `#2563eb` | **Primary.** Buttons, active nav, accents |
| `--blue-400` | `#60a5fa` | Accents on dark, icon strokes on navy |
| `--blue-50` | `#eff6ff` | Tinted section bands |
| `--amber` | `#f59e0b` | **New.** Sampled from the hero sunset. Used sparingly — "Most Popular" badge, the eyebrow rule, one word in the hero. |
| `--gray-600` | `#4b5563` | Body copy |
| `--line` | `#e5e7eb` | Borders, dividers |

The amber is the one real addition. All-blue read cold and generic; a single warm
accent pulled from the hero photo ties the type to the imagery and gives the
pricing table somewhere to point.

## Type

Unchanged from the original — the pairing was already right.

- **DM Serif Display** — h1/h2 display. Gives an editorial, established feel that
  separates them from every other blue-gradient web-dev shop.
- **DM Sans** — everything else. 400/500/600/700.
- Fluid sizing via `clamp()` so the hero never overflows at 320px.

## Treatment

- **Dark hero, light body.** The sunset photo carries a navy gradient overlay so
  white headline text clears 4.5:1 contrast. Everything below is airy and light.
- **No emoji as UI.** The original used 🖥️🔍💰⚡ as service icons and 🏗️🍽️🛍️ for
  industries. Replaced with inline stroked SVG. This is a design studio's own
  site — emoji icons undercut the entire pitch.
- **Real numbers in the HTML.** The original animated its stats from zero via JS,
  meaning the shipped markup literally read `0% Client Satisfaction`. Values are
  now static in the DOM; the count-up is progressive enhancement only.
- Generous whitespace, 1200px max, 14px/22px radii, soft blue-tinted shadows.
- Motion is subtle and respects `prefers-reduced-motion`.

## Imagery

No brand photography exists — the original site had **zero images**. Sourced four
real photographs of the actual service area from Wikimedia Commons (credited in
the footer) rather than generic stock, because "we're genuinely local" is the
core claim and generic lake stock would undercut it.

| File | Subject | Page |
|---|---|---|
| `muskoka-sunset.jpg` | Sunset over a Muskoka lake, pines in silhouette | Home hero |
| `orillia-waterfront.jpg` | Couchiching Beach Park, Orillia — boats, gazebo | About |
| `muskoka-autumn-dock.jpg` | Dock on 3 Mile Lake, autumn maples | Service areas |
| `lake-muskoka.jpg` | Open water, Lake Muskoka | Contact |

## Explicitly not included

- **No testimonials.** The business has no published reviews. Inventing them was
  not an option, so the design earns trust structurally instead — transparent
  pricing, a clear process, and an explicit "what's included" guarantee block.
- **No portfolio.** Same reason: no client sites were supplied. A `work.html`
  slot is the single highest-value addition once real projects can be shown.
